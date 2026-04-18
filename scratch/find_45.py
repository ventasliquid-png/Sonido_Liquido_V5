import sqlite3
import os
from pathlib import Path

def inspect_db(path):
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        results = []
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results.append((table, count))
            except:
                pass
        conn.close()
        return results
    except:
        return None

def main():
    search_dirs = [
        r'C:\dev\Sonido_Liquido_V5',
        r'C:\dev\RAR_V1',
        r'C:\dev\HAWA 1.0'
    ]
    
    print(f"{'Path':<60} | {'Table':<20} | {'Count':<5}")
    print("-" * 90)
    
    for d in search_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            if '_DEPRECATED' in root or 'node_modules' in root or '.venv' in root:
                continue
            for f in files:
                if f.endswith('.db'):
                    full_path = os.path.join(root, f)
                    res = inspect_db(full_path)
                    if res:
                        for table, count in res:
                            if count > 0:
                                print(f"{full_path:<60} | {table:<20} | {count:<5}")

if __name__ == "__main__":
    main()
