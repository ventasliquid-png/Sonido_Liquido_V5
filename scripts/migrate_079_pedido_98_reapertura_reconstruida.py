"""
migrate_079_pedido_98_reapertura_reconstruida.py
================================================
Card #215 (S900, 05/11/2026; pedido de Carlos: «el bit del 98, ¿no lo podés agregar a mano?»): el pedido #98 es el caso real que dio origen a la Card #215. Estaba CUMPLIDO sin
marca de ajuste desde el 04/11 (16:27), con un cierre que dio por salidos 60 paquetes que no salieron (remito 0015-00003043, «salió sin papel»); se reabrio, se anulo ese remito y se
volvio a cerrar con ajuste el 05/11 a las 10:16 (pedido 80, entregado 20). Esa reapertura se hizo ANTES de que el sistema registrara las salidas de Cumplido, asi que no dejo huella.

QUE HACE: SOLO si el pedido #98 sigue como se audito (CUMPLIDO, con el bit 46, sin el bit 50, con la nota del cierre con discrepancia «pedido 80.0, entregado 20.0» de las 10:16 y su
remito 0015-00003043 anulado), le prende el bit 50 (FUE_REABIERTO, Nike 05/11) y le agrega UNA linea [SISTEMA] que cuenta lo ocurrido y aclara que se escribio despues del hecho y que
la hora exacta de la reapertura no quedo registrada (entre el 04/11 16:28 y el 05/11 10:16).
QUE NO HACE: no cambia el estado (sigue CUMPLIDO), ni los renglones, ni los remitos, ni ningun otro pedido. Si el pedido no esta como se audito, o ya tiene el bit 50 (porque el sistema
nuevo ya lo registro), informa y lo deja.

SEGURIDAD: SAVEPOINT, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y criterio de estado); sale 0.

MIGRATION_ID = "079_pedido_98_reapertura_reconstruida"
NRO_SESION = 900
"""
import os
import sqlite3
from datetime import datetime

MIGRATION_ID = "079_pedido_98_reapertura_reconstruida"
NRO_SESION = 900
PEDIDO_ID = 98
REMITO_NUMERO = "0015-00003043"
BIT34, BIT35, BIT46, BIT50 = 1 << 34, 1 << 35, 1 << 46, 1 << 50

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_079] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("pedidos", "remitos"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_079] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_079] Iniciando {MIGRATION_ID}...")
resultado = "saltado"
try:
    cur.execute("SAVEPOINT ped")
    ped = cur.execute("SELECT id, estado, flags_estado, nota FROM pedidos WHERE id = ?", (PEDIDO_ID,)).fetchone()
    if not ped:
        print(f"[migrate_079] AVISO -- el pedido #{PEDIDO_ID} no esta en esta base: no se toca.")
    else:
        flags, nota = int(ped[2] or 0), ped[3] or ""
        rem = cur.execute("SELECT estado, flags_estado FROM remitos WHERE pedido_id = ? AND numero_legal = ?", (PEDIDO_ID, REMITO_NUMERO)).fetchone()
        remito_anulado = bool(rem) and ((rem[0] or "").upper() == "ANULADO" or int(rem[1] or 0) & BIT35)
        if flags & BIT50:
            resultado = "ya estaba"
            print(f"[migrate_079] El pedido #{PEDIDO_ID} ya tiene el bit 50 (el sistema nuevo ya registro la reapertura): nada que hacer.")
        elif not ((ped[1] or "").upper() == "CUMPLIDO" and flags & BIT34 and flags & BIT46
                  and "Cierre confirmado con discrepancia" in nota and "pedido 80.0, entregado 20.0" in nota and "2026-11-05 10:16" in nota and remito_anulado):
            print(f"[migrate_079] AVISO -- el pedido #{PEDIDO_ID} no esta como se audito (estado {ped[1]}, remito {REMITO_NUMERO} anulado: {remito_anulado}): no se toca.")
        else:
            hoy = datetime.now().strftime("%d/%m/%Y")
            marca = ("[SISTEMA] Reapertura reconstruida el " + hoy + " (S900, migrate_079, Card #215): el pedido estaba Cumplido sin marca de ajuste desde el 04/11/2026 (16:27), con un cierre que "
                     "dio por salidos 60 paquetes que no salieron (remito " + REMITO_NUMERO + ", «salió sin papel»); se reabrió, se anuló ese remito y se volvió a cerrar con ajuste el "
                     "05/11/2026 a las 10:16 (pedido 80, entregado 20). La hora exacta de la reapertura no quedó registrada: fue entre el 04/11 16:28 y el 05/11 10:16. "
                     "Línea escrita después del hecho, a partir de las copias de P de esas dos horas; prende la marca FUE_REABIERTO (bit 50).")
            cur.execute("UPDATE pedidos SET flags_estado = ?, nota = ? WHERE id = ?", (flags | BIT50, (nota + "\n" + marca) if nota else marca, PEDIDO_ID))
            resultado = "corregido"
            print(f"[migrate_079] OK -- pedido #{PEDIDO_ID}: bit 50 prendido y una linea [SISTEMA] con la reapertura reconstruida (sigue CUMPLIDO).")
    cur.execute("RELEASE ped")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO ped"); cur.execute("RELEASE ped")
    print(f"[migrate_079] ERROR -- {type(e).__name__}: {e} (el pedido quedo como estaba)")

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_079] {MIGRATION_ID} registrada ({resultado}).")
conn.close()
