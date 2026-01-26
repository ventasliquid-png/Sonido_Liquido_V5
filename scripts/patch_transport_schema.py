import sqlite3
import os

DB_PATH = 'pilot.db'

def patch_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("--- Patching empresas_transporte table ---")
        
        # List of columns to check/add
        # (Column Name, SQLite Type)
        columns_to_add = [
            ('cuit', 'VARCHAR(15)'),
            ('condicion_iva_id', 'CHAR(32)'), # UUID
            ('localidad', 'VARCHAR'),
            ('provincia_id', 'VARCHAR(5)'),
            ('direccion_despacho', 'VARCHAR'),
            ('horario_despacho', 'VARCHAR'),
            ('telefono_despacho', 'VARCHAR')
        ]

        # Get existing columns
        cursor.execute("PRAGMA table_info(empresas_transporte)")
        existing_cols = [row[1] for row in cursor.fetchall()]

        for col_name, col_type in columns_to_add:
            if col_name not in existing_cols:
                print(f"Adding column: {col_name} ({col_type})...")
                cursor.execute(f"ALTER TABLE empresas_transporte ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column {col_name} already exists.")
        
        conn.commit()
        print("--- Patch applied successfully ---")
        
    except Exception as e:
        print(f"Error patching DB: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    patch_db()
