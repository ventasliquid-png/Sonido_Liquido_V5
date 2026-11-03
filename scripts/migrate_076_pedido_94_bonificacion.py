"""
migrate_076_pedido_94_bonificacion.py
=====================================
Card #144 (S898, 03/11/2026; caso del pedido #94 de Centro Pet, a decidir por Carlos desde el 28/10): el pedido #94 (10/08, CUMPLIDO) quedo con 120 x 11.600 SIN la
bonificacion del 5 % = $ 1.684.320 con IVA, y la factura 2582 (11/08) imprime 120 x 11.600 con 5 % de bonificacion = neto $ 1.322.400, total $ 1.600.104: el pedido quedo
$ 84.216 arriba y nadie lo vio. Criterio (Carlos, 02/11, «el precio de la factura es el correcto»): la factura manda; el pedido #94 tomo el precio sin la bonificacion.

QUE HACE: SOLO si el pedido #94 sigue como se audito (un unico renglon 120 x 11.600 sin descuento, subtotal 1.392.000 y total 1.684.320) y la factura 2582 (A, punto de venta 1)
esta enlazada a ese pedido con neto 1.322.400 y total 1.600.104, le pone al renglon el 5 % de descuento (descuento en pesos 69.600, subtotal 1.322.400) y deja el total en
1.600.104, igual al de la factura. Deja una nota [SISTEMA] en el pedido.
QUE NO HACE: no toca la factura, los remitos ni ningun otro pedido; no cambia el estado (sigue CUMPLIDO). Si el pedido no esta como se audito, informa y lo deja.

SEGURIDAD: SAVEPOINT, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y criterio de estado); sale 0.

MIGRATION_ID = "076_pedido_94_bonificacion"
NRO_SESION = 898
"""
import os
import sqlite3

MIGRATION_ID = "076_pedido_94_bonificacion"
NRO_SESION = 898
EPS = 0.011
PEDIDO_ID = "94"
FACTURA_NUMERO = 2582

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_076] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("pedidos", "pedidos_items", "facturas"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_076] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_076] Iniciando {MIGRATION_ID}...")
resultado = "saltado"
try:
    cur.execute("SAVEPOINT ped")
    ped = cur.execute("SELECT id, total, nota FROM pedidos WHERE id = ?", (PEDIDO_ID,)).fetchone()
    fac = cur.execute("""SELECT pedido_id, neto_gravado, total FROM facturas
                         WHERE tipo_comprobante = 'FACTURA_A' AND punto_venta = 1 AND numero_comprobante = ?""", (FACTURA_NUMERO,)).fetchone()
    items = cur.execute("SELECT id, cantidad, precio_unitario, COALESCE(descuento_porcentaje, 0), COALESCE(descuento_importe, 0), subtotal FROM pedidos_items WHERE pedido_id = ?", (PEDIDO_ID,)).fetchall()
    if not ped or not fac:
        print(f"[migrate_076] AVISO -- el pedido #{PEDIDO_ID} o la factura {FACTURA_NUMERO} no estan en esta base: no se toca.")
    elif str(fac[0]) != PEDIDO_ID or abs((fac[1] or 0) - 1322400.0) > EPS or abs((fac[2] or 0) - 1600104.0) > EPS:
        print(f"[migrate_076] AVISO -- la factura {FACTURA_NUMERO} no esta como se audito (pedido {fac[0]}, neto {fac[1]}, total {fac[2]}): no se toca.")
    elif len(items) == 1 and abs(items[0][1] - 120.0) < EPS and abs(items[0][2] - 11600.0) < EPS and abs(items[0][5] - 1322400.0) < EPS and abs(ped[1] - 1600104.0) < EPS:
        resultado = "ya estaba"
        print(f"[migrate_076] El pedido #{PEDIDO_ID} ya tiene la bonificacion y el total de la factura: nada que hacer.")
    elif len(items) == 1 and abs(items[0][1] - 120.0) < EPS and abs(items[0][2] - 11600.0) < EPS and abs(items[0][3]) < EPS and abs(items[0][4]) < EPS \
            and abs(items[0][5] - 1392000.0) < EPS and abs(ped[1] - 1684320.0) < EPS:
        iid = items[0][0]
        descuento = round(120.0 * 11600.0 * 0.05, 2)
        subtotal = round(120.0 * 11600.0 - descuento, 2)
        total = round(subtotal * 1.21, 2)
        if abs(subtotal - 1322400.0) > EPS or abs(total - 1600104.0) > EPS:
            print(f"[migrate_076] AVISO -- la cuenta no da la de la factura ({subtotal} / {total}): no se toca.")
        else:
            marca = (f"[SISTEMA] Se agrego la bonificacion del 5 % del renglon segun la factura 00001-00002582 (S898, migrate_076, Card #144): "
                     f"subtotal 1.392.000,00 -> {subtotal:,.2f}; total {ped[1]:,.2f} -> {total:,.2f}.")
            cur.execute("UPDATE pedidos_items SET descuento_porcentaje = 5.0, descuento_importe = ?, subtotal = ? WHERE id = ?", (descuento, subtotal, iid))
            cur.execute("UPDATE pedidos SET total = ?, nota = ? WHERE id = ?", (total, ((ped[2] or "") + "\n" + marca).strip(), PEDIDO_ID))
            resultado = "corregido"
            print(f"[migrate_076] OK -- pedido #{PEDIDO_ID}: 5 % de bonificacion en el renglon, subtotal {subtotal:,.2f}, total {ped[1]:,.2f} -> {total:,.2f}.")
    else:
        print(f"[migrate_076] AVISO -- el pedido #{PEDIDO_ID} no esta como se audito ({len(items)} renglon(es), total {ped[1]}): no se toca.")
    cur.execute("RELEASE ped")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO ped"); cur.execute("RELEASE ped")
    print(f"[migrate_076] ERROR -- {type(e).__name__}: {e} (el pedido quedo como estaba)")

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_076] {MIGRATION_ID} registrada ({resultado}).")
conn.close()
