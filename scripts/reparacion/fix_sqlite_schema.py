import sqlite3
import os

db_path = "pilot_v5x.db"

def fix_schema():
    print(f"Checking schema for {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check clientes table
    cursor.execute("PRAGMA table_info(clientes)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns in 'clientes': {columns}")
    
    if "transporte_habitual_id" not in columns:
        print("Adding 'transporte_habitual_id' to 'clientes'...")
        try:
            cursor.execute("ALTER TABLE clientes ADD COLUMN transporte_habitual_id CHAR(32)")
            print("Successfully added 'transporte_habitual_id'.")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("'transporte_habitual_id' already exists.")

    # [V5.8] Check for other missing columns if needed
    # (Checking the model view_file earlier)
    # legacy_id_bas? flags_estado? 
    # The traceback showed they are in the SELECT, so they exist if the query reached transporte_habitual_id.
    
    conn.commit()
    conn.close()
    print("Schema fix completed.")

if __name__ == "__main__":
    if os.path.exists(db_path):
        fix_schema()
    else:
        print(f"Database {db_path} not found.")
