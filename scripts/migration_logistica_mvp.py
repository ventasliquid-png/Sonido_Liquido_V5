import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'pilot.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("costo_envio_cliente", "FLOAT DEFAULT 0.0"),
        ("costo_flete_interno", "FLOAT DEFAULT 0.0"),
        ("estado_logistico", "TEXT DEFAULT 'PENDIENTE'")
    ]
    
    print(f"Migrating database at: {DB_PATH}")
    
    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(pedidos)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}...")
                cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column {col_name} already exists.")
        
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
