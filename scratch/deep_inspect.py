import sqlite3
import os

def check_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        results = []
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                count = cur.fetchone()[0]
                cur.execute(f"PRAGMA table_info({t})")
                cols = [c[1].lower() for c in cur.fetchall()]
                results.append((t, count, cols))
            except:
                pass
        conn.close()
        return results
    except:
        return None

def main():
    paths = [r'C:\dev\Sonido_Liquido_V5', r'C:\dev\RAR_V1', r'C:\dev\HAWA 1.0']
    print(f"{'DATABASE':<60} | {'TABLE':<20} | {'COUNT':<6} | {'HAS SKU?':<8}")
    print("-" * 100)
    for p in paths:
        if not os.path.exists(p): continue
        for root, dirs, files in os.walk(p):
            if any(x in root for x in ['_DEPRECATED', 'node_modules', '.git', '.venv']):
                continue
            for f in files:
                if f.endswith('.db'):
                    db_p = os.path.join(root, f)
                    res = check_db(db_p)
                    if res:
                        for table, count, cols in res:
                            if count > 0:
                                has_sku = 'sku' in cols
                                # Filter for potential matches
                                if 10 <= count <= 100:
                                    print(f"{db_p:<60} | {table:<20} | {count:<6} | {has_sku}")

if __name__ == "__main__":
    main()
