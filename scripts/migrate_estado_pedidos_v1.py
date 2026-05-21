# scripts/migrate_estado_pedidos_v1.py
# Migracion: campo estado (string) -> bits en flags_estado (PedidoFlags)
# Sesión 813 OF — 2026-05-21
# ============================================================

import sqlite3
import shutil
from pathlib import Path

# --- CONFIG ---
BASE_DIR    = Path(__file__).resolve().parent.parent
DB_PATH     = BASE_DIR / "pilot_v5x.db"
BACKUP_PATH = BASE_DIR / "pilot_v5x.db.bak_pre_migra_estados"

# Mapa estado string -> máscara de bits a encender (OR)
ESTADO_A_BITS = {
    "PENDIENTE":   1,          # EXISTENCE
    "PRESUPUESTO": 1 | 4,      # EXISTENCE + ES_PRESUPUESTO
    "BORRADOR":    1 | 8,      # EXISTENCE + ES_BORRADOR
    "INTERNO":     1 | 16,     # EXISTENCE + ES_INTERNO
    "CUMPLIDO":    1 | 32,     # EXISTENCE + ES_CUMPLIDO
    "ANULADO":     1 | 128,    # EXISTENCE + ES_ANULADO
    "RESERVADO":   1 | 256,    # EXISTENCE + ES_RESERVADO
}

# Bits preexistentes que NO deben ser alterados
BITS_PREEXISTENTES = {
    6:  64,    # PEDIDO_DUPLICATE_CONFIRMED
    9:  512,   # INGESTA_CON_CORRECCION
    12: 4096,  # NO_FISCAL_FORCE
}

def main():
    print("=" * 60)
    print("  MIGRACION: estado string -> PedidoFlags bits")
    print("  Script: migrate_estado_pedidos_v1.py")
    print("=" * 60)

    # ── 1. BACKUP ──────────────────────────────────────────────
    print("\n[1] BACKUP")
    if not DB_PATH.exists():
        print(f"  ERROR: No se encontró la base de datos en {DB_PATH}")
        return

    if BACKUP_PATH.exists():
        print(f"  STOP: El backup ya existe en:")
        print(f"  {BACKUP_PATH}")
        print("  Eliminar el backup manualmente si querés re-ejecutar.")
        return

    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"  [OK] Backup creado: {BACKUP_PATH.name}")

    # ── 2. LECTURA ESTADO ACTUAL ───────────────────────────────
    print("\n[2] ESTADO ACTUAL — conteo por estado")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    conteo = cur.execute(
        "SELECT estado, COUNT(*) as n FROM pedidos GROUP BY estado ORDER BY n DESC"
    ).fetchall()

    for row in conteo:
        estado = row["estado"] or "(NULL)"
        print(f"  {estado:<20}  {row['n']:>4} pedidos")

    pedidos = cur.execute(
        "SELECT id, estado, flags_estado FROM pedidos ORDER BY id"
    ).fetchall()
    print(f"\n  Total: {len(pedidos)} pedidos")

    # ── 3. CALCULAR PLAN DE MIGRACION ─────────────────────────
    print("\n[3] PLAN DE MIGRACION")
    print(f"  {'ID':>5}  {'Estado':<14}  {'flags_actual':>12}  {'bits_a_OR':>10}  {'flags_nuevo':>12}  {'Preexist. OK?'}")
    print(f"  {'-'*5}  {'-'*14}  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*13}")

    plan = []
    estados_desconocidos = []

    for p in pedidos:
        estado       = (p["estado"] or "").strip().upper()
        flags_actual = p["flags_estado"] or 0
        pid          = p["id"]

        if estado not in ESTADO_A_BITS:
            estados_desconocidos.append((pid, p["estado"], flags_actual))
            continue

        mascara     = ESTADO_A_BITS[estado]
        flags_nuevo = flags_actual | mascara

        # Verificar que los bits preexistentes no cambian
        preexist_ok = all(
            (flags_actual & v) == (flags_nuevo & v)
            for v in BITS_PREEXISTENTES.values()
        )
        ok_str = "[OK]" if preexist_ok else "[!] ALERTA"

        plan.append((pid, p["estado"], flags_actual, mascara, flags_nuevo, preexist_ok))
        print(f"  {pid:>5}  {p['estado']:<14}  {flags_actual:>12}  {mascara:>10}  {flags_nuevo:>12}  {ok_str}")

    if estados_desconocidos:
        print(f"\n  [!] ESTADOS DESCONOCIDOS (no se migrarán, el operador decide):")
        for pid, est, fl in estados_desconocidos:
            print(f"    id={pid}  estado='{est}'  flags={fl}")

    alertas = [r for r in plan if not r[5]]
    if alertas:
        print(f"\n  [!] ALERTAS DE BITS PREEXISTENTES ({len(alertas)} pedidos):")
        for r in alertas:
            print(f"    id={r[0]}  estado='{r[1]}'  actual={r[2]}  nuevo={r[4]}")

    # ── 4. RESUMEN PREVENTIVO ─────────────────────────────────
    print(f"\n[4] RESUMEN")
    print(f"  Pedidos a migrar          : {len(plan)}")
    print(f"  Pedidos estado desconocido: {len(estados_desconocidos)}")
    print(f"  Alertas bits preexistentes: {len(alertas)}")

    if alertas:
        print("\n  STOP: Hay alertas de bits preexistentes. Revisar antes de continuar.")
        conn.close()
        return

    # ── 5. CONFIRMACIÓN PIN ────────────────────────────────────
    print("\n" + "=" * 60)
    print("  El campo estado (string) NO se elimina — queda read-only.")
    print("  La migracion usa OR: los flags preexistentes se preservan.")
    print("=" * 60)
    pin = input("\n¿Ejecutar migracion? (escribir PIN 1974 para confirmar): ").strip()

    if pin != "1974":
        print("\n  Migracion cancelada.")
        print(f"  El backup quedó en: {BACKUP_PATH}")
        print("  Podés eliminarlo manualmente si no lo necesitás.")
        conn.close()
        return

    # ── 6. EJECUCIÓN ──────────────────────────────────────────
    print("\n[5] EJECUTANDO...")
    migrados = 0
    for pid, estado_str, flags_actual, mascara, flags_nuevo, _ in plan:
        cur.execute(
            "UPDATE pedidos SET flags_estado = ? WHERE id = ?",
            (flags_nuevo, pid)
        )
        migrados += 1

    conn.commit()
    print(f"  [OK] {migrados} pedidos actualizados.")

    # ── 7. VERIFICACIÓN POST-MIGRACION ────────────────────────
    print("\n[6] VERIFICACIÓN POST-MIGRACION")
    print(f"  {'ID':>5}  {'Estado':<14}  {'flags_antes':>11}  {'flags_despues':>13}  {'OK?'}")
    print(f"  {'-'*5}  {'-'*14}  {'-'*11}  {'-'*13}  {'-'*5}")

    errores = 0
    for pid, estado_str, flags_actual, mascara, flags_esperado, _ in plan:
        row = cur.execute(
            "SELECT flags_estado FROM pedidos WHERE id = ?", (pid,)
        ).fetchone()
        flags_real = row["flags_estado"] or 0

        preexist_ok = all(
            (flags_actual & v) == (flags_real & v)
            for v in BITS_PREEXISTENTES.values()
        )
        bits_ok = (flags_real == flags_esperado)
        ok_str  = "[OK]" if (preexist_ok and bits_ok) else "[!] ERROR"
        if not (preexist_ok and bits_ok):
            errores += 1

        print(f"  {pid:>5}  {estado_str:<14}  {flags_actual:>11}  {flags_real:>13}  {ok_str}")

    print(f"\n  Errores detectados: {errores}")
    if errores == 0:
        print("  [OK] MIGRACION EXITOSA — todos los bits correctos.")
    else:
        print("  [!] MIGRACION CON ERRORES — revisar antes de operar.")

    conn.close()

if __name__ == "__main__":
    main()
