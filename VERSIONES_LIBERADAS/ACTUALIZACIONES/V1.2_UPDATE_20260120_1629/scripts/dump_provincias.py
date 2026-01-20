import sqlite3
import json

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot.db"

def dump_provincias():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM provincias")
        rows = cursor.fetchall()
        print(json.dumps(rows, indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_provincias()
