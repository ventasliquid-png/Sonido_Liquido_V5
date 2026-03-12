
import sqlite3
import os

DB_PATH = 'c:\\dev\\Sonido_Liquido_V5\\backend\\pilot.db'

def update_schema_v5_4():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='productos_proveedores'")
        if cursor.fetchone()[0] == 0:
            print("Creating table 'productos_proveedores'...")
            cursor.execute("""
                CREATE TABLE productos_proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    proveedor_id CHAR(36) NOT NULL,
                    costo NUMERIC(12, 4) NOT NULL DEFAULT 0,
                    moneda VARCHAR(3) DEFAULT 'ARS',
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones VARCHAR(255),
                    FOREIGN KEY(producto_id) REFERENCES productos(id),
                    FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
                )
            """)
            print("Table 'productos_proveedores' created successfully.")
        else:
            print("Table 'productos_proveedores' already exists.")

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema_v5_4()
