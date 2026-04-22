import sqlite3

def get_tables(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    conn.close()
    return tables

dev_db = 'c:/dev/Sonido_Liquido_V5/pilot_v5x.db'
prod_db = 'C:/dev/V5-LS/data/V5_LS_MASTER.db'

t_dev = get_tables(dev_db)
t_prod = get_tables(prod_db)

print(f"Extra in PROD: {t_prod - t_dev}")
print(f"Missing in PROD: {t_dev - t_prod}")

for t in t_prod & t_dev:
    # Check if columns match
    c_dev = {r[1] for r in sqlite3.connect(dev_db).execute(f"PRAGMA table_info({t})")}
    c_prod = {r[1] for r in sqlite3.connect(prod_db).execute(f"PRAGMA table_info({t})")}
    if c_dev != c_prod:
        print(f"Column Mismatch in {t}:")
        print(f"  Only in DEV: {c_dev - c_prod}")
        print(f"  Only in PROD: {c_prod - c_dev}")
