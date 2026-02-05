
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

# Force Local DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
pilot_db_path = os.path.join(ROOT_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{pilot_db_path}"

print(f"--- FIXING CLIENTE 2 ADDRESSES ON: {DATABASE_URL} ---")
engine = create_engine(DATABASE_URL)

def fix_addresses():
    print("\n--- UPDATING EMPTY ADDRESSES ---")
    query_find = text("SELECT id, calle FROM domicilios WHERE calle IS NULL OR calle = ''")
    
    with engine.connect() as conn:
        empty = conn.execute(query_find).fetchall()
        print(f"Found {len(empty)} empty/null addresses.")
        
        # Specific fix for Cliente 2 Fiscal (ID 2d7b...)
        # From previous inspecting: 2d7b93ea8d194f6f9aba1ed4cde58433
        target_id = "2d7b93ea8d194f6f9aba1ed4cde58433"
        
        update_sql = text(f"UPDATE domicilios SET calle = 'CALLE FISCAL RECUPERADA', numero = '123' WHERE id = '{target_id}'")
        res = conn.execute(update_sql)
        print(f"Update Result for Fiscal: Rows matched/affected: {res.rowcount}")

        # Verify "La Piedra"
        # 421e4606fa9241b19c6235ee0da34040
        sec_id = "421e4606fa9241b19c6235ee0da34040"
        check_sec = text(f"SELECT * FROM domicilios WHERE id = '{sec_id}'")
        sec_rows = conn.execute(check_sec).fetchall()
        for r in sec_rows:
             print(f"Secondary Check: ID {r.id}, Activo: {r.activo}, Fiscal: {r.es_fiscal}, Calle: '{r.calle}'")
             
        conn.commit()
    
    print("--- FIX COMPLETE ---")

if __name__ == "__main__":
    try:
        fix_addresses()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
