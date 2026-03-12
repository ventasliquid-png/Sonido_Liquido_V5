import sys
import os
from sqlalchemy import create_engine, text

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

SNAPSHOT_DB = "iowa_snapshot.sqlite"

def check_schema():
    # [FIX] Use PROJECT ROOT
    PROJECT_ROOT = BASE_DIR
    abs_path = os.path.join(PROJECT_ROOT, SNAPSHOT_DB)
    
    db_url = f"sqlite:///{abs_path}"
    print(f"--- [DEBUG] Inspecting Schema of {abs_path} ---", file=sys.stderr)
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 1. List all tables
            print("--- Lists of Tables ---", file=sys.stderr)
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            for t in tables:
                print(f"   Table: {t[0]}", file=sys.stderr)
            
            # 2. Inspect 'clientes' (or whatever matches)
            target = None
            for t in tables:
                if t[0].lower() == 'clientes':
                    target = t[0]
                    break
            
            if target:
                print(f"--- Inspecting '{target}' ---", file=sys.stderr)
                res = conn.execute(text(f"PRAGMA table_info({target})"))
                columns = res.fetchall()
                for col in columns:
                    print(f"   - {col[1]} ({col[2]})", file=sys.stderr)
            else:
                print("--- 'clientes' table NOT found in metadata ---", file=sys.stderr)
                
    except Exception as e:
        print(f"    [ERROR] Could not read schema: {e}", file=sys.stderr)

if __name__ == "__main__":
    check_schema()
