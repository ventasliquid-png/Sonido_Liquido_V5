import sqlite3
import os

MIGRATION_ID = "037_cliente_origen_id"
NRO_SESION = 858

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_037] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_037] Iniciando {MIGRATION_ID}...")
    # Auto-referencial: por defecto cada cliente apunta a si mismo (sin vinculo).
    # Si apunta a OTRO registro, ese es el vinculo Rosa->Blanco (Doctrina de
    # Linaje de Identidad V14.6, dictamen Nike). NUNCA comparar con "if campo:"
    # -- siempre nunca es NULL. Comparar id != cliente_origen_id.
    cur.execute(
        "ALTER TABLE clientes ADD COLUMN cliente_origen_id CHAR(32) REFERENCES clientes(id)"
    )
    cur.execute(
        "UPDATE clientes SET cliente_origen_id = id WHERE cliente_origen_id IS NULL"
    )
    filas = cur.rowcount
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_037] OK — {MIGRATION_ID} aplicada. {filas} clientes backfilled (auto-referencia).")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        cur.execute(
            "UPDATE clientes SET cliente_origen_id = id WHERE cliente_origen_id IS NULL"
        )
        cur.execute(
            "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
            (MIGRATION_ID, NRO_SESION),
        )
        conn.commit()
        print(f"[migrate_037] SKIP — columna ya existía, backfill + registro de control aplicados igual.")
    else:
        print(f"[migrate_037] ERROR: {e}")
        conn.rollback()
finally:
    conn.close()
