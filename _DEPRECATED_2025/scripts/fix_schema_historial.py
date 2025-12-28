
import sqlite3
import os

DB_PATH = "pilot.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Checking for 'historial_cache' column...")
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [c[1] for c in cursor.fetchall()]
        
        if 'historial_cache' in columns:
            print("Column 'historial_cache' already exists.")
        else:
            print("Adding 'historial_cache' column...")
            # SQLite doesn't support JSON type natively in all versions, but we can stick it in TEXT or BLOB. 
            # SQLAlchemy defaults to JSON usually mapping to TEXT in SQLite if using the standard dialect.
            # Using TEXT is safest.
            cursor.execute("ALTER TABLE clientes ADD COLUMN historial_cache TEXT")
            print("Column added successfully.")
            conn.commit()
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
