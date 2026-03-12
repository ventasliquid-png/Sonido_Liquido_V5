import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot.db")

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Get columns for 'domicilios'
    cursor.execute("PRAGMA table_info(domicilios)")
    columns = cursor.fetchall()
    
    # Debug print: (cid, name, type, notnull, dflt_value, pk)
    found_cols = [col[1] for col in columns]
    print("Columns in 'domicilios':", found_cols)
    
    if "piso" in found_cols and "depto" in found_cols:
        print("✅ Columms 'piso' and 'depto' EXIST.")
    else:
        print("❌ MISSING columns!")

    conn.close()

if __name__ == "__main__":
    main()
