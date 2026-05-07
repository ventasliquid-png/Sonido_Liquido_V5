"""
migrate_000_control_migraciones.py
====================================
PATRÓN ESTÁNDAR DE MIGRACIONES — Sonido Líquido V5
====================================
Todos los scripts de migración deben seguir este patrón:

    MIGRATION_ID = "NNN_nombre_descriptivo"
    NRO_SESION = XXXX

    conn = get_db_conn()
    if ya_aplicada(conn, MIGRATION_ID):
        print(f"[migrate] SKIP — {MIGRATION_ID} ya aplicada.")
        conn.close()
        exit(0)

    # ... ejecutar migración ...

    registrar(conn, MIGRATION_ID, NRO_SESION)
    conn.close()

Este script (000) debe correrse primero — crea la tabla de control.
Es idempotente: usa CREATE TABLE IF NOT EXISTS.
"""
import sqlite3, os

MIGRATION_ID = "000_control_migraciones"
NRO_SESION = 797

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") \
          or "C:/dev/Sonido_Liquido_V5/pilot_v5x.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")
conn.commit()

# Auto-registrarse si no está
existe = conn.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()
if not existe:
    conn.execute(
        "INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION)
    )
    conn.commit()
    print(f"[migrate_000] OK — tabla _migraciones_aplicadas creada y registrada.")
else:
    print(f"[migrate_000] SKIP — ya aplicada.")

conn.close()
