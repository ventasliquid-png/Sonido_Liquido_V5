
import sqlite3
import os

db_path = r'C:\dev\Sonido_Liquido_V5\pilot.db'

if not os.path.exists(db_path):
    print(f"ERROR: DB file not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contactos';")
        if not cursor.fetchone():
            print("Table 'contactos' DOES NOT EXIST.")
        else:
            cursor.execute("SELECT count(*) FROM contactos")
            count = cursor.fetchone()[0]
            print(f"Total rows in 'contactos': {count}")
            
            if count > 0:
                print("First 5 rows:")
                cursor.execute("SELECT * FROM contactos LIMIT 5")
                for row in cursor.fetchall():
                    print(row)
        
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")
