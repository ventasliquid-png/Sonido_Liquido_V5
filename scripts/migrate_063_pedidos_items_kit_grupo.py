"""
migrate_063_pedidos_items_kit_grupo.py
======================================
S888 (19/10/2026), Card #177 (kits del pedido, v3). Nike ratifico el diseno con Sello de Oro el 19/10: cada renglon del pedido puede llevar un NUMERO de kit.

  pedidos_items.kit_grupo  INTEGER NULL   -- NULL = el renglon no es de ningun kit. Es una etiqueta LOCAL al pedido: no es un SKU, no es un contador entre pedidos y el kit
                                             no tiene trazabilidad como item. Un kit existe solo si 2 o mas renglones del mismo pedido comparten el numero.

El bit PedidoFlags.ES_KIT (bit 47 del PEDIDO) NO se toca aca: lo calcula el servidor al guardar el pedido (backend/pedidos/kits.py). Los pedidos que ya existen quedan sin kit.

QUE NO HACE: no cambia ningun dato (todos los renglones quedan con kit_grupo NULL), no toca ninguna otra tabla ni ninguna otra columna.
GUARDAS: si falta la tabla pedidos_items no se hace nada y NO se registra (se reintenta en el proximo arranque); si la columna ya existe (alguien la agrego a mano) no se vuelve a agregar y se
registra igual. Informa (sin frenar) si algun pedido ya tuviera prendido el bit 47: estaba libre, no deberia pasar.
FALLA RUIDOSO: si el ALTER TABLE falla sale con 1, para que auto_migrar frene el arranque: el modelo ya declara la columna y arrancar sin ella dejaria todas las consultas de pedidos en error.

MIGRATION_ID = "063_pedidos_items_kit_grupo"
NRO_SESION = 888
"""
import os
import sqlite3

MIGRATION_ID = "063_pedidos_items_kit_grupo"
NRO_SESION = 888
BIT_ES_KIT = 1 << 47

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_063] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pedidos_items'").fetchone():
    print("[migrate_063] AVISO -- falta la tabla 'pedidos_items': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_063] Iniciando {MIGRATION_ID}...")
try:
    columnas = {r[1] for r in cur.execute("PRAGMA table_info(pedidos_items)")}
    if "kit_grupo" in columnas:
        print("[migrate_063] La columna kit_grupo ya existe: no se vuelve a agregar.")
    else:
        cur.execute("ALTER TABLE pedidos_items ADD COLUMN kit_grupo INTEGER")
    tipo = {r[1]: r[2] for r in cur.execute("PRAGMA table_info(pedidos_items)")}.get("kit_grupo")
    if tipo is None:
        raise RuntimeError("despues del ALTER TABLE la columna kit_grupo no figura en pedidos_items")
    if cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pedidos'").fetchone():
        con_bit = cur.execute("SELECT COUNT(*) FROM pedidos WHERE (flags_estado & ?) != 0", (BIT_ES_KIT,)).fetchone()[0]
        if con_bit:
            print(f"[migrate_063] AVISO -- {con_bit} pedido(s) ya tienen prendido el bit 47 (ES_KIT), que estaba libre: se recalcula la proxima vez que se guarden.")
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    n = cur.execute("SELECT COUNT(*) FROM pedidos_items").fetchone()[0]
    print(f"[migrate_063] OK -- pedidos_items.kit_grupo ({tipo}, NULL) listo; {n} renglones sin kit; {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    print(f"[migrate_063] ERROR -- {type(e).__name__}: {e}. No se registra; auto_migrar frena el arranque.")
    conn.close()
    raise SystemExit(1)
conn.close()
