
import sqlite3
import os

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path, timeout=60)
cur = conn.cursor()
cur.execute("PRAGMA busy_timeout = 60000")

try:
    print(f"--- [VAULT PHASE 1] Migrating Structure in {db_path} ---")
    
    # 1. Update 'domicilios' table
    cur.execute("PRAGMA table_info(domicilios)")
    columns = [c[1] for c in cur.fetchall()]
    
    if 'flags_infra' not in columns:
        print("Adding 'flags_infra' to 'domicilios'...")
        cur.execute("ALTER TABLE domicilios ADD COLUMN flags_infra BIGINT DEFAULT 0")
    else:
        print("'flags_infra' already exists in 'domicilios'.")

    # 2. Create 'vinculos_geograficos' table
    print("Creating 'vinculos_geograficos' table if not exists...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vinculos_geograficos (
        id CHAR(36) PRIMARY KEY,
        entidad_tipo VARCHAR(20) NOT NULL,
        entidad_id CHAR(36) NOT NULL,
        domicilio_id CHAR(36) NOT NULL,
        alias VARCHAR(255),
        flags_relacion BIGINT DEFAULT 0,
        activo BOOLEAN DEFAULT 1,
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (domicilio_id) REFERENCES domicilios(id)
    );
    """)
    
    # Create Indexes for performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vg_entidad ON vinculos_geograficos (entidad_tipo, entidad_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vg_domicilio ON vinculos_geograficos (domicilio_id);")

    conn.commit()
    print("--- [VAULT PHASE 1] SUCCESS ---")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    conn.rollback()
finally:
    conn.close()
