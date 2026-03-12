
import sqlite3
import os
import uuid

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path, timeout=60)
cur = conn.cursor()
cur.execute("PRAGMA busy_timeout = 60000")

try:
    print("--- [VAULT PHASE 1.5] Schema Pivot: Universal Domicilios ---")
    
    # Check if we already did this
    cur.execute("PRAGMA table_info(domicilios)")
    cols = [c[1] for c in cur.fetchall()]
    
    # If the current 'domicilios' table still doesn't have 'flags_infra' (or has cliente_id as NOT NULL)
    # Actually, let's just use a more robust way: Rename legacy and create new.
    
    cur.execute("ALTER TABLE domicilios RENAME TO domicilios_legacy")
    print("Renamed 'domicilios' to 'domicilios_legacy'")

    print("Creating Universal 'domicilios' table...")
    cur.execute("""
    CREATE TABLE domicilios (
        id CHAR(36) PRIMARY KEY,
        alias VARCHAR(255),
        calle VARCHAR(255) NOT NULL,
        numero VARCHAR(50),
        piso VARCHAR(50),
        depto VARCHAR(50),
        maps_link TEXT,
        notas_logistica TEXT,
        contacto_id INTEGER,
        cp VARCHAR(20),
        localidad VARCHAR(255),
        provincia_id VARCHAR(5),
        activo BOOLEAN DEFAULT 1,
        flags_infra BIGINT DEFAULT 0,
        observaciones TEXT,
        
        -- Legacy support (nullable now)
        cliente_id CHAR(36),
        es_fiscal BOOLEAN DEFAULT 0,
        es_entrega BOOLEAN DEFAULT 0,
        es_predeterminado BOOLEAN DEFAULT 0,
        
        -- V14 pipe parity
        calle_entrega VARCHAR(255),
        numero_entrega VARCHAR(50),
        piso_entrega VARCHAR(50),
        depto_entrega VARCHAR(50),
        cp_entrega VARCHAR(20),
        localidad_entrega VARCHAR(255),
        provincia_entrega_id VARCHAR(5),
        
        -- Logistics links
        transporte_habitual_nodo_id CHAR(36),
        transporte_id CHAR(36),
        intermediario_id CHAR(36),
        metodo_entrega VARCHAR(50),
        modalidad_envio VARCHAR(50),
        origen_logistico VARCHAR(50),
        bit_identidad BIGINT
    );
    """)

    print("Pumping data from legacy to universal...")
    # Get all column names from legacy to map them
    cur.execute("PRAGMA table_info(domicilios_legacy)")
    legacy_cols = [c[1] for c in cur.fetchall()]
    
    # Intersection of columns
    cur.execute("PRAGMA table_info(domicilios)")
    new_cols = [c[1] for c in cur.fetchall()]
    common_cols = [c for c in legacy_cols if c in new_cols]
    
    cols_str = ", ".join(common_cols)
    cur.execute(f"INSERT INTO domicilios ({cols_str}) SELECT {cols_str} FROM domicilios_legacy")
    
    print(f"Transfered {cur.rowcount} records.")

    conn.commit()
    print("--- [VAULT PHASE 1.5] SUCCESS ---")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    conn.rollback()
finally:
    conn.close()
