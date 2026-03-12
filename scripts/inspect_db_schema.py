import sqlite3
import os

DB_PATH = 'pilot.db'

def inspect_table():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print(f"--- Schema for empresas_transporte in {DB_PATH} ---")
        cursor.execute("PRAGMA table_info(empresas_transporte)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        print("\n--- Rows sample ---")
        cursor.execute("SELECT * FROM empresas_transporte LIMIT 1")
        print(cursor.fetchone())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_table()
