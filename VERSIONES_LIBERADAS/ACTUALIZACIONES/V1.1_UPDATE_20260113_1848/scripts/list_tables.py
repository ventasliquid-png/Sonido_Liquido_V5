import sqlite3
import json

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot.db"

def list_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(json.dumps([t[0] for t in tables], indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
