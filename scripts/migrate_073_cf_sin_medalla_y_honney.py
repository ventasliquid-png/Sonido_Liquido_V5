"""
migrate_073_cf_sin_medalla_y_honney.py
======================================
S894 (28/10/2026). Carlos: «Hacelo y de paso volá "Honney" a secas, que es uno que no tiene nada».
(1) Un Consumidor Final es Blanco (Carlos 28/10; commit 8898f46b): la regla de clientes ya no le da la medalla Rosa (bit 19) y se la saca al
    guardar la ficha, pero las fichas que nadie volvió a guardar la conservan (en P: M&M Odontológicos La Plata, que queda Blanco por decisión
    de Carlos). La pantalla ya los muestra Blancos; acá se limpia el dato: se apaga el bit 19 de todo cliente CF (condición Consumidor Final o
    CUIT 00000000000/11111111119) que no es Rosa (nivel 9/11 o CUIT 11111111111), con una línea [SISTEMA] en observaciones.
(2) «HONNEY» (alta 07/04/2026): sin CUIT, sin ninguna marca (flags 0: fósil anterior al genoma, «borrado físico autorizado» según
    HardDeleteManager) y sin ninguna referencia. No confundir con «HONEYMAX S A», que tiene pedidos y facturas y no se toca. Se borra solo si
    sigue así: mismo id y nombre, sin marcas o virgen, y su id no aparece en ninguna otra tabla.
SEGURIDAD: después del backup de auto_migrar; SAVEPOINT por paso; idempotente; sale 0.

MIGRATION_ID = "073_cf_sin_medalla_y_honney"
NRO_SESION = 894
"""
import os
import sqlite3

MIGRATION_ID = "073_cf_sin_medalla_y_honney"
NRO_SESION = 894
B19, IS_VIRGIN = 1 << 19, 1 << 1
HONNEY = ("13b34c02b38749e291113500d22591ef", "HONNEY")
NOTA = "[SISTEMA] 28/10/2026 (S894, migrate_073): sin la medalla Rosa (bit 19): un Consumidor Final es Blanco (Carlos). Marcas antes: {antes}."

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_073] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("clientes", "condiciones_iva"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_073] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)
TABLAS = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]

print(f"[migrate_073] Iniciando {MIGRATION_ID}...")
limpios, aviso_honney, errores = [], None, []
# (1) Consumidor Final sin medalla Rosa
try:
    cur.execute("SAVEPOINT cf")
    filas = cur.execute("""SELECT c.id, c.razon_social, c.flags_estado, c.observaciones FROM clientes c
                           LEFT JOIN condiciones_iva ci ON ci.id = c.condicion_iva_id
                           WHERE (c.flags_estado & ?) != 0
                             AND (upper(coalesce(ci.nombre, '')) LIKE '%CONSUMIDOR FINAL%' OR c.cuit IN ('00000000000', '11111111119'))
                             AND coalesce(c.cuit, '') != '11111111111' AND (c.flags_estado & 15) NOT IN (9, 11)""", (B19,)).fetchall()
    for cid, nombre, flags, obs in filas:
        flags = int(flags)
        nota = NOTA.format(antes=flags)
        cur.execute("UPDATE clientes SET flags_estado = ?, observaciones = ? WHERE id = ?", (flags & ~B19, ((obs + "\n") if obs else "") + nota, cid))
        limpios.append((nombre, flags, flags & ~B19))
    cur.execute("RELEASE cf")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO cf"); cur.execute("RELEASE cf")
    errores.append(("medallas de CF", f"{type(e).__name__}: {e}"))

# (2) HONNEY
try:
    cur.execute("SAVEPOINT honney")
    cid, nombre = HONNEY
    fila = cur.execute("SELECT razon_social, flags_estado, coalesce(cuit, '') FROM clientes WHERE id = ?", (cid,)).fetchone()
    if fila is None:
        aviso_honney = "no existe en esta base"
    elif fila[0] != nombre or not (int(fila[1] or 0) == 0 or int(fila[1]) & IS_VIRGIN) or fila[2].strip():
        aviso_honney = f"ya no es la ficha auditada (nombre «{fila[0]}», marcas {fila[1]}, CUIT «{fila[2]}»): no se borra"
    else:
        refs = []
        for t in TABLAS:
            for col in [r[1] for r in cur.execute(f"PRAGMA table_info('{t}')").fetchall()]:
                try:
                    n = cur.execute(f"SELECT COUNT(*) FROM '{t}' WHERE \"{col}\" = ?", (cid,)).fetchone()[0]
                except sqlite3.Error:
                    continue
                if n and not (t == "clientes" and col in ("id", "cliente_origen_id")):
                    refs.append((t, col, n))
        if refs:
            aviso_honney = f"la referencian {refs}: no se borra"
        else:
            cur.execute("DELETE FROM clientes WHERE id = ?", (cid,))
    cur.execute("RELEASE honney")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO honney"); cur.execute("RELEASE honney")
    errores.append(("HONNEY", f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_073] OK -- CF sin medalla Rosa: {len(limpios)}; HONNEY: {'borrado' if aviso_honney is None and not any(n == 'HONNEY' for n, _ in errores) else 'no se borró'}; "
      f"con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, a, d in limpios:
    print(f"[migrate_073]   {n}: marcas {a} -> {d}")
if aviso_honney:
    print(f"[migrate_073] AVISO -- HONNEY: {aviso_honney}")
for n, m in errores:
    print(f"[migrate_073] ERROR -- {n}: {m} (quedó como estaba)")
conn.close()
