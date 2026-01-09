import sqlite3
import os
import glob

def audit_db(db_path):
    print(f"\n--- Auditing: {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        for table in [t[0] for t in tables]:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} records")
        
        conn.close()
    except Exception as e:
        print(f"Error auditing {db_path}: {e}")

if __name__ == "__main__":
    db_files = glob.glob("**/*.db", recursive=True) + glob.glob("**/*.sqlite", recursive=True)
    for db_file in db_files:
        if os.path.getsize(db_file) > 100 * 1024:
            audit_db(db_file)
        else:
            print(f"Skipping {db_file} (too small: {os.path.getsize(db_file)} bytes)")
