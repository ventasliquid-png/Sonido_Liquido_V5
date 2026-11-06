"""
migrate_080_fechas_pedidos_nacidos_de_factura.py
================================================
H27 (CA, auditoria del 05/11/2026; Carlos 06/11: «sí a la migración de fechas»; mapa del flujo documental S901, Card #217 F4). Un pedido que NACE de una factura (bit 38) tiene que llevar la fecha
de la FACTURA, no la del dia en que se cargo: la venta la perfecciona el hecho comercial (Nike, Sello de Oro, 06/11, Q1). Hasta el codigo de la S901 la Ingesta clasica creaba esos pedidos con la
fecha de carga, y asi quedaron dos en la base de produccion:
  - #153 (Medi Cient): factura 2612 del 06/10/2026, pedido del 03/11/2026 12:06 -> en el Espejo figuraba la venta de octubre en noviembre;
  - #155 (Doc Baires): factura 2603 del 16/09/2026, pedido del 05/11/2026 10:28 -> la venta de septiembre figuraba en noviembre y el aviso de duplicado del #156 salto por esa fecha.

QUE HACE: a cada uno de los dos, SOLO si sigue como se audito (nacido de factura -bit 38-, no retroactivo -sin el bit 39-, con la fecha de carga auditada y vinculado a la factura auditada, con el
numero y la fecha que se auditaron), le pone la fecha de la factura (a las 00:00, igual que contra natura) y le agrega UNA linea [SISTEMA] con la fecha anterior y el motivo.
QUE NO HACE: no toca el estado, los flags, los renglones, el total, los remitos (el remito conserva la fecha en que se emitio de verdad), las facturas ni ningun otro pedido. Si un pedido no esta
como se audito, o ya tiene la fecha de la factura, informa y lo deja.

SEGURIDAD: SAVEPOINT por pedido, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y criterio de estado); sale 0.

MIGRATION_ID = "080_fechas_pedidos_nacidos_de_factura"
NRO_SESION = 901
"""
import os
import sqlite3
from datetime import datetime

MIGRATION_ID = "080_fechas_pedidos_nacidos_de_factura"
NRO_SESION = 901
BIT38, BIT39 = 1 << 38, 1 << 39
# (pedido, fecha de carga auditada, numero de la factura, fecha de la factura)
CASOS = [
    (153, "2026-11-03", 2612, "2026-10-06"),
    (155, "2026-11-05", 2603, "2026-09-16"),
]

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_080] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("pedidos", "facturas", "facturas_remitos", "remitos"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_080] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_080] Iniciando {MIGRATION_ID}...")
corregidos = 0
for pid, carga, numero, fecha_factura in CASOS:
    try:
        cur.execute("SAVEPOINT ped")
        ped = cur.execute("SELECT id, fecha, flags_estado, nota FROM pedidos WHERE id = ?", (pid,)).fetchone()
        if not ped:
            print(f"[migrate_080] AVISO -- el pedido #{pid} no esta en esta base: no se toca.")
        else:
            flags, nota, fecha_actual = int(ped[2] or 0), ped[3] or "", str(ped[1] or "")
            # la factura auditada, vinculada al pedido directamente o por alguno de sus remitos
            fac = cur.execute(
                "SELECT f.id FROM facturas f WHERE f.numero_comprobante = ? AND substr(f.fecha_emision, 1, 10) = ? AND (CAST(f.pedido_id AS TEXT) = ? OR EXISTS ("
                "SELECT 1 FROM facturas_remitos fr JOIN remitos r ON r.id = fr.remito_id WHERE fr.factura_id = f.id AND r.pedido_id = ?))",
                (numero, fecha_factura, str(pid), pid)).fetchone()
            if fecha_actual[:10] == fecha_factura:
                print(f"[migrate_080] El pedido #{pid} ya lleva la fecha de la factura ({fecha_factura}): nada que hacer.")
            elif not (flags & BIT38 and not flags & BIT39 and fecha_actual[:10] == carga and fac):
                print(f"[migrate_080] AVISO -- el pedido #{pid} no esta como se audito (fecha {fecha_actual[:16]}, nacido de factura: {bool(flags & BIT38)}, retroactivo: {bool(flags & BIT39)}, "
                      f"factura {numero} del {fecha_factura} vinculada: {bool(fac)}): no se toca.")
            else:
                hoy = datetime.now().strftime("%d/%m/%Y")
                d, m, a = fecha_factura[8:10], fecha_factura[5:7], fecha_factura[0:4]
                marca = (f"[SISTEMA] Fecha corregida el {hoy} (S901, migrate_080, H27): el pedido nació de la factura {numero} del {d}/{m}/{a}, pero había quedado con la fecha de carga "
                         f"({fecha_actual[8:10]}/{fecha_actual[5:7]}/{fecha_actual[0:4]} {fecha_actual[11:16]}). Ahora lleva la fecha de la factura, que es la de la venta. Los remitos conservan su fecha.")
                cur.execute("UPDATE pedidos SET fecha = ?, nota = ? WHERE id = ?", (f"{fecha_factura} 00:00:00.000000", (nota + "\n" + marca) if nota else marca, pid))
                corregidos += 1
                print(f"[migrate_080] OK -- pedido #{pid}: fecha {fecha_actual[:16]} -> {fecha_factura} (factura {numero}) y una linea [SISTEMA] con la fecha anterior.")
        cur.execute("RELEASE ped")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO ped"); cur.execute("RELEASE ped")
        print(f"[migrate_080] ERROR -- pedido #{pid}: {type(e).__name__}: {e} (el pedido quedo como estaba)")

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_080] {MIGRATION_ID} registrada ({corregidos} corregido{'s' if corregidos != 1 else ''}).")
conn.close()
