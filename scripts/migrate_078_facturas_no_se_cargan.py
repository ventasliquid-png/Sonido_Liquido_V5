"""
migrate_078_facturas_no_se_cargan.py
====================================
Card #212 (S899, 04/11/2026; Carlos: «Deberías poner un Menú "Facturas" a la izquierda a nivel Remito o Pedido o Productos»). La pantalla «Facturas» muestra tres cosas: las facturas
cargadas, las que se subieron sin terminar y las que FALTAN (huecos de la numeración de ARCA). Lo que se decidió no cargar a propósito no es un hueco: vive en una tabla chica.

QUE HACE: crea la tabla `facturas_no_se_cargan` (la misma que declara el modelo FacturaNoSeCarga; el arranque ya crea las tablas de los modelos, esto la asegura antes) y le carga las dos
decisiones de Carlos del 03/11: la factura A 0001-00002586 (factura de toda la OC del pedido #98; lo entregado se facturó con la 2600 y el cliente pidió la NC 74) y la nota de crédito A
0001-00000074 (anula la 2586; V5 no tiene la 2586, cargarla acreditaría la 2600 por error).
QUE NO HACE: no toca facturas, pedidos, remitos ni la Ingesta.

SEGURIDAD: SAVEPOINT, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas e INSERT OR IGNORE sobre la clave unica); sale 0.

MIGRATION_ID = "078_facturas_no_se_cargan"
NRO_SESION = 899
"""
import os
import sqlite3

MIGRATION_ID = "078_facturas_no_se_cargan"
NRO_SESION = 899
DECIDIDO_POR = "Carlos (decisión del 03/11/2026)"
SEMILLA = [
    ("FACTURA_A", 1, 2586,
     "Factura de toda la OC del pedido #98 (14/08); lo entregado se facturó con la 2600 y el cliente pidió la NC 74. Carlos 03/11: no se carga."),
    ("NOTA_CREDITO_A", 1, 74,
     "Anula la 2586 (28/10). V5 no tiene la 2586: cargarla acreditaría la 2600 por error. Carlos 03/11: no se carga."),
]

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_078] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_078] Iniciando {MIGRATION_ID}...")
resultado = "saltado"
try:
    cur.execute("SAVEPOINT nsc")
    cur.execute("""CREATE TABLE IF NOT EXISTS facturas_no_se_cargan (
        id INTEGER NOT NULL,
        tipo_comprobante VARCHAR NOT NULL,
        punto_venta INTEGER NOT NULL,
        numero_comprobante INTEGER NOT NULL,
        motivo VARCHAR NOT NULL,
        decidido_por VARCHAR,
        created_at DATETIME,
        PRIMARY KEY (id),
        CONSTRAINT uq_factura_no_se_carga UNIQUE (tipo_comprobante, punto_venta, numero_comprobante)
    )""")
    nuevas = 0
    for tipo, pv, numero, motivo in SEMILLA:
        cur.execute("""INSERT OR IGNORE INTO facturas_no_se_cargan (tipo_comprobante, punto_venta, numero_comprobante, motivo, decidido_por, created_at)
                       VALUES (?, ?, ?, ?, ?, datetime('now'))""", (tipo, pv, numero, motivo, DECIDIDO_POR))
        if cur.rowcount:
            nuevas += 1
            print(f"[migrate_078] OK -- {tipo} {pv:04d}-{numero:08d}: queda como «no se carga a propósito».")
    cur.execute("RELEASE nsc")
    resultado = f"{nuevas} marca(s) nueva(s)" if nuevas else "ya estaba"
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO nsc"); cur.execute("RELEASE nsc")
    print(f"[migrate_078] ERROR -- {type(e).__name__}: {e} (no se registró; se reintenta en el próximo arranque)")
    conn.close()
    raise SystemExit(0)

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_078] {MIGRATION_ID} registrada ({resultado}).")
conn.close()
