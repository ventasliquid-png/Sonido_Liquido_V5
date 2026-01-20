import sqlite3
import os
import sys

def check_db(path):
    print(f"\n--- CHECKING {path} ---")
    if not os.path.exists(path):
        print("FILE NOT FOUND")
        return

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        print(f"INTEGRITY: {integrity}")

        # Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"TABLES: {[t[0] for t in tables]}")
        
        # Clientes
        try:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            count = cursor.fetchone()[0]
            print(f"CLIENTES COUNT: {count}")
        except Exception as e:
            print(f"CLIENTES QUERY FAILED: {e}")

        conn.close()
    except Exception as e:
        print(f"DB ERROR: {e}")

check_db(os.path.join('backend', 'data', 'pilot.db'))
check_db('pilot.db')
