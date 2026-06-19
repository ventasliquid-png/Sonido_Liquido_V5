import sqlite3
import os

MIGRATION_ID = "032_contacto_responsable_id"
NRO_SESION = 830

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_032] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_032] Iniciando {MIGRATION_ID}...")
    cur.execute(
        "ALTER TABLE pedidos ADD COLUMN contacto_responsable_id TEXT REFERENCES vinculos(id)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_032] OK — {MIGRATION_ID} aplicada y registrada.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        cur.execute(
            "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
            (MIGRATION_ID, NRO_SESION),
        )
        conn.commit()
        print(f"[migrate_032] SKIP — columna ya existía, registrada en control.")
    else:
        print(f"[migrate_032] ERROR: {e}")
        conn.rollback()
finally:
    conn.close()
