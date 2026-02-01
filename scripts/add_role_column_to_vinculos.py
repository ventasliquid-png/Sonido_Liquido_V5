import sqlite3
import os

db_path = r'C:\dev\Sonido_Liquido_V5\pilot.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"ERROR: DB file not found at {db_path}")
        return

    print(f"Connecting to database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check vinculos table columns
        cursor.execute("PRAGMA table_info(vinculos)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if 'tipo_contacto_id' not in columns:
            print("Adding tipo_contacto_id column to vinculos table...")
            cursor.execute("ALTER TABLE vinculos ADD COLUMN tipo_contacto_id VARCHAR")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column tipo_contacto_id already exists.")
            
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")

if __name__ == "__main__":
    migrate()
