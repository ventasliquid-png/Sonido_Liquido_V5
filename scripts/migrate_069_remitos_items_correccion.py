"""
migrate_069_remitos_items_correccion.py
=======================================
S893 (26/10/2026), nodo Remitos. Carlos: lo que se pierde, se rechaza, vuelve o no salió NO puede vivir solo en una nota: tiene que mover el renglón del pedido
(que el sistema no crea que está cumplido lo que no se entregó). La corrección es un renglón de cantidad negativa (el mecanismo de la devolución de la Etapa 6)
atado al renglón del remito que corrige y con su causa.

QUE HACE:
  1. remitos_items.corrige_item_id INTEGER NULL (el renglón de remito que este renglón corrige) con su índice.
  2. remitos_items.causa VARCHAR NULL (NO_SALIO / SE_PERDIO / SE_RECHAZO / VOLVIO).
QUE NO HACE: no toca ningún dato existente (todos los renglones quedan NULL = renglón común), ni crea correcciones. Idempotente.
GUARDAS: si falta la tabla remitos_items no se hace nada y NO se registra. Una transaccion; si falla, deshace todo y sale con 1: el modelo ya declara las dos
columnas y arrancar sin ellas dejaria en error todas las consultas de renglones de remito.

MIGRATION_ID = "069_remitos_items_correccion"
NRO_SESION = 893
"""
import os
import sqlite3
import sys

MIGRATION_ID = "069_remitos_items_correccion"
NRO_SESION = 893

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(RAIZ, "pilot_v5x.db")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_069] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
tablas = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
if "remitos_items" not in tablas:
    print("[migrate_069] AVISO -- falta la tabla remitos_items: no se hace nada y la migracion NO se registra (se reintenta).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_069] Iniciando {MIGRATION_ID}...")
try:
    cur.execute("BEGIN")
    columnas = {r[1] for r in cur.execute("PRAGMA table_info(remitos_items)")}
    if "corrige_item_id" not in columnas:
        cur.execute("ALTER TABLE remitos_items ADD COLUMN corrige_item_id INTEGER")
    if "causa" not in columnas:
        cur.execute("ALTER TABLE remitos_items ADD COLUMN causa VARCHAR")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_remitos_items_corrige_item_id ON remitos_items (corrige_item_id)")
    total = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("COMMIT")
    print(f"[migrate_069] OK -- remitos_items.corrige_item_id y remitos_items.causa listas ({total} renglones, todos como renglon comun).")
    print(f"[migrate_069] {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    try:
        cur.execute("ROLLBACK")
    except Exception:  # noqa: BLE001
        pass
    print(f"[migrate_069] ERROR -- {type(e).__name__}: {e}. Se deshizo todo y no se registra; auto_migrar frena el arranque.")
    conn.close()
    raise SystemExit(1)
conn.close()
