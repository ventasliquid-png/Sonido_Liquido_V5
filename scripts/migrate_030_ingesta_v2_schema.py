import sqlite3

MIGRATION_ID = "030_ingesta_v2_schema"
NRO_SESION = 800

DB_PATH = "C:/dev/Sonido_Liquido_V5/pilot_v5x.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    print(f"[*] Iniciando migración {MIGRATION_ID}...")
    
    # 1. Tabla FacturasRaw
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingesta_facturas_raw (
        id CHAR(32) PRIMARY KEY,
        filename VARCHAR NOT NULL,
        pdf_bytes BLOB NOT NULL,
        audit_status VARCHAR DEFAULT 'RECIBIDO',
        audit_warning VARCHAR,
        parsed_data_raw TEXT,
        created_at DATETIME,
        processed_at DATETIME
    )
    """)
    
    # 2. Tabla FacturasProcesadas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingesta_facturas_procesadas (
        id CHAR(32) PRIMARY KEY,
        raw_id CHAR(32) NOT NULL,
        cliente_id CHAR(32),
        pedido_id INTEGER,
        numero_factura VARCHAR,
        cae VARCHAR,
        vto_cae VARCHAR,
        parsed_data_final TEXT,
        audit_log TEXT,
        estado VARCHAR DEFAULT 'PREVIEW',
        flags_estado BIGINT DEFAULT 1,
        created_at DATETIME,
        processed_at DATETIME,
        FOREIGN KEY(raw_id) REFERENCES ingesta_facturas_raw(id),
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id)
    )
    """)
    
    # 3. Índices
    cur.execute("CREATE INDEX IF NOT EXISTS idx_raw_id ON ingesta_facturas_procesadas(raw_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_proc_cliente ON ingesta_facturas_procesadas(cliente_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_proc_pedido ON ingesta_facturas_procesadas(pedido_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_proc_nro ON ingesta_facturas_procesadas(numero_factura)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_proc_cae ON ingesta_facturas_procesadas(cae)")

    print(f"[migrate_030] Tablas de ingesta creadas con éxito.")

    # 4. Registro de migración
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION)
    )
    
    conn.commit()
    print(f"[migrate_030] OK — registrado en _migraciones_aplicadas.")
    
except Exception as e:
    print(f"[migrate_030] ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
