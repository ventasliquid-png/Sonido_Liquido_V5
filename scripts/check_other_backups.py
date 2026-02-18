import sys
import os
from sqlalchemy import create_engine, text

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

BACKUPS = [
    "pilot_PRE_SIMULACRO.db",
    "iowa_snapshot.sqlite"
]

def check_backups():
    # [FIX] Use current directory where script is running (or project root)
    # BASE_DIR is scripts/.. -> c:\dev\Sonido_Liquido_V5
    PROJECT_ROOT = BASE_DIR 
    
    print(f"--- [DEBUG] Scanning directory: {PROJECT_ROOT} ---", file=sys.stderr)
    
    for backup_name in BACKUPS:
        abs_path = os.path.join(PROJECT_ROOT, backup_name)
        if not os.path.exists(abs_path):
            print(f"--- [SKIP] {backup_name} not found at {abs_path} ---", file=sys.stderr)
            continue
            
        db_url = f"sqlite:///{abs_path}"
        print(f"--- [DEBUG] Checking {backup_name} ---", file=sys.stderr)
        
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                # Check for table
                res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'"))
                if res.fetchone():
                    print(f"    [FOUND] Table 'clientes' exists in {backup_name}", file=sys.stderr)
                    # Check count
                    count = conn.execute(text("SELECT count(*) FROM clientes")).scalar()
                    print(f"    [DATA] Row count: {count}", file=sys.stderr)
                else:
                    print(f"    [MISSING] Table 'clientes' NOT found in {backup_name}", file=sys.stderr)
        except Exception as e:
            print(f"    [ERROR] Could not read {backup_name}: {e}", file=sys.stderr)

if __name__ == "__main__":
    check_backups()
