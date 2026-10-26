"""
migrate_068_remitos_oc.py
=========================
S893 (26/10/2026), nodo Remitos. Carlos (25/10, MARCO_REMITOS.md A1): «la OC se copia al remito». Para encontrar un remito por su orden de
compra (F3 del nodo) y para que el remito no dependa de lo que el pedido diga después.

QUE HACE:
  1. remitos.oc VARCHAR NULL (columna nueva).
  2. A cada remito que todavia no tiene OC le copia la de su pedido (sin espacios en las puntas), si el pedido tiene una. Carlos (26/10): se
     copia tambien a los remitos que ya existen, para que la busqueda por OC ande desde el primer dia.
QUE NO HACE: no toca ninguna otra columna, estado, numero ni fecha; no pisa una OC que el remito ya tenga; los remitos de pedidos sin OC
quedan en NULL. Idempotente.
GUARDAS: si falta la tabla remitos o pedidos no se hace nada y NO se registra. Una transaccion; si falla, deshace todo y sale con 1: el modelo ya
declara remitos.oc y arrancar sin ella dejaria en error todas las consultas de remitos.

MIGRATION_ID = "068_remitos_oc"
NRO_SESION = 893
"""
import os
import sqlite3
import sys

MIGRATION_ID = "068_remitos_oc"
NRO_SESION = 893

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(RAIZ, "pilot_v5x.db")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_068] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
tablas = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
if "remitos" not in tablas or "pedidos" not in tablas:
    print("[migrate_068] AVISO -- faltan las tablas remitos o pedidos: no se hace nada y la migracion NO se registra (se reintenta).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_068] Iniciando {MIGRATION_ID}...")
try:
    cur.execute("BEGIN")
    if "oc" not in {r[1] for r in cur.execute("PRAGMA table_info(remitos)")}:
        cur.execute("ALTER TABLE remitos ADD COLUMN oc VARCHAR")
    cur.execute("""UPDATE remitos SET oc = (SELECT trim(p.oc) FROM pedidos p WHERE p.id = remitos.pedido_id)
                   WHERE (oc IS NULL OR trim(oc) = '')
                     AND EXISTS (SELECT 1 FROM pedidos p WHERE p.id = remitos.pedido_id AND p.oc IS NOT NULL AND trim(p.oc) != '')""")
    copiadas = cur.rowcount
    total = cur.execute("SELECT COUNT(*) FROM remitos").fetchone()[0]
    con_oc = cur.execute("SELECT COUNT(*) FROM remitos WHERE oc IS NOT NULL AND trim(oc) != ''").fetchone()[0]
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("COMMIT")
    print(f"[migrate_068] OK -- remitos.oc lista; OC copiada del pedido en {copiadas} remitos; {con_oc} de {total} remitos tienen OC.")
    print(f"[migrate_068] {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    try:
        cur.execute("ROLLBACK")
    except Exception:  # noqa: BLE001
        pass
    print(f"[migrate_068] ERROR -- {type(e).__name__}: {e}. Se deshizo todo y no se registra; auto_migrar frena el arranque.")
    conn.close()
    raise SystemExit(1)
conn.close()
