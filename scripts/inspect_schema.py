import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'pilot.db')

def inspect():
    if not os.path.exists(DB_PATH):
        print("DB Not Found")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Inspecting table: pedidos in {DB_PATH}")
    cursor.execute("PRAGMA table_info(pedidos)")
    columns = cursor.fetchall()
    
    # cid, name, type, notnull, dflt_value, pk
    names = [c[1] for c in columns]
    print(f"Columns found ({len(names)}):")
    for n in names:
        print(f"- {n}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
