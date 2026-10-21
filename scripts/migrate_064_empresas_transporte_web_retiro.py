"""
migrate_064_empresas_transporte_web_retiro.py
=============================================
S890 (21/10/2026), paquete 1 de remitos, punto 2 (Carlos): «en la práctica accedemos a la web de registro del transporte (Cruz del Sur por ejemplo) y esa dirección
web sería lo más práctico que el sistema puede poner, porque es un copy paste o un hipervínculo, y se abre la página de solicitud de retiro».

  empresas_transporte.web_retiro  VARCHAR(255) NULL   -- la página del transporte para PEDIR EL RETIRO (no la de seguimiento: esa es web_tracking).
                                                        La ventana del remito la ofrece como enlace y para copiar.

QUE NO HACE: no carga ninguna web (todas quedan en NULL; la de Cruz del Sur la carga la migración del remito 3031), no toca ninguna otra tabla ni columna.
GUARDAS: si falta la tabla empresas_transporte no se hace nada y NO se registra (se reintenta en el próximo arranque); si la columna ya existe no se vuelve a agregar y se
registra igual.
FALLA RUIDOSO: si el ALTER TABLE falla sale con 1, para que auto_migrar frene el arranque: el modelo ya declara la columna y arrancar sin ella dejaría en error todas las
consultas de transportes (y con ellas los remitos).

MIGRATION_ID = "064_empresas_transporte_web_retiro"
NRO_SESION = 890
"""
import os
import sqlite3

MIGRATION_ID = "064_empresas_transporte_web_retiro"
NRO_SESION = 890

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_064] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='empresas_transporte'").fetchone():
    print("[migrate_064] AVISO -- falta la tabla 'empresas_transporte': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_064] Iniciando {MIGRATION_ID}...")
try:
    columnas = {r[1] for r in cur.execute("PRAGMA table_info(empresas_transporte)")}
    if "web_retiro" in columnas:
        print("[migrate_064] La columna web_retiro ya existe: no se vuelve a agregar.")
    else:
        cur.execute("ALTER TABLE empresas_transporte ADD COLUMN web_retiro VARCHAR(255)")
    tipo = {r[1]: r[2] for r in cur.execute("PRAGMA table_info(empresas_transporte)")}.get("web_retiro")
    if tipo is None:
        raise RuntimeError("despues del ALTER TABLE la columna web_retiro no figura en empresas_transporte")
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    n = cur.execute("SELECT COUNT(*) FROM empresas_transporte").fetchone()[0]
    print(f"[migrate_064] OK -- empresas_transporte.web_retiro ({tipo}, NULL) lista; {n} transportes sin web de retiro cargada; {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    print(f"[migrate_064] ERROR -- {type(e).__name__}: {e}. No se registra; auto_migrar frena el arranque.")
    conn.close()
    raise SystemExit(1)
conn.close()
