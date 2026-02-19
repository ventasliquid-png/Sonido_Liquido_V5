import sqlite3
import os

DB_PATH = r"c:\dev\RAR_V1\v5_cantera_oro.db"

if not os.path.exists(DB_PATH):
    print(f"[!] DB not found at {DB_PATH}")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        print("[ TABLES ]")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(f"- {t[0]}")
            
        # Check schema of cantera_productos if it exists
        print("\n[ SCHEMA: cantera_productos ]")
        try:
            cursor.execute("PRAGMA table_info(cantera_productos)")
            columns = cursor.fetchall()
            if columns:
                for col in columns:
                    print(col)
            else:
                print("Table 'cantera_productos' not found or empty schema.")
        except Exception as e:
            print(f"Error checking schema: {e}")

        conn.close()
    except Exception as e:
        print(f"[X] Error connecting to DB: {e}")
