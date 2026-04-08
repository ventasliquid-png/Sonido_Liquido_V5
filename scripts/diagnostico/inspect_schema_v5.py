
import sqlite3
import os

DB_PATH = os.path.join("backend", "pilot.db")

def inspect_table(table_name):
    print(f"--- STRUCTURE OF {table_name} ---")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            # cid, name, type, notnull, dflt_value, pk
            print(f"- {col[1]} ({col[2]})")
        conn.close()
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        inspect_table("pedidos")
        print("\n")
        inspect_table("remitos")
    else:
        print(f"Database not found at {DB_PATH}")
