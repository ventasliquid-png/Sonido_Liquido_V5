import sqlite3
import os

dev_db = r'c:\dev\Sonido_Liquido_V5\pilot_v5x.db'
prod_db = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'

def get_columns(db_path, table):
    if not os.path.exists(db_path):
        return f"File {db_path} not found"
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        conn.close()
        return cols
    except Exception as e:
        return str(e)

print(f"DEV Rubros: {get_columns(dev_db, 'rubros')}")
print(f"PROD Rubros: {get_columns(prod_db, 'rubros')}")
print(f"DEV Productos: {get_columns(dev_db, 'productos')}")
print(f"PROD Productos: {get_columns(prod_db, 'productos')}")
