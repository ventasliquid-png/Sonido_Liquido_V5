import sqlite3
import os

MIGRATION_ID = "036_remitos_flags_estado"
NRO_SESION = 836

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_036] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_036] Iniciando {MIGRATION_ID}...")
    cur.execute(
        "ALTER TABLE remitos ADD COLUMN flags_estado INTEGER DEFAULT 0"
    )
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_036] OK — {MIGRATION_ID} aplicada y registrada.")

    # Verificación post-migración
    cur.execute("SELECT flags_estado FROM remitos LIMIT 3")
    rows = cur.fetchall()
    print(f"[migrate_036] Sample flags_estado: {rows}")

    cur.execute("PRAGMA table_info(remitos)")
    cols = cur.fetchall()
    flags_col = next((c for c in cols if c[1] == "flags_estado"), None)
    print(f"[migrate_036] PRAGMA confirm: {flags_col}")

except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        cur.execute(
            "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
            (MIGRATION_ID, NRO_SESION),
        )
        conn.commit()
        print(f"[migrate_036] SKIP — columna ya existía, registrada en control.")
    else:
        print(f"[migrate_036] ERROR: {e}")
        conn.rollback()
finally:
    conn.close()
