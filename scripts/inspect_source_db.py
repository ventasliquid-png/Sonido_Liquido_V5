import sys
import os
from sqlalchemy import create_engine, text

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# [FIX] Use local directory
PROJECT_ROOT = BASE_DIR
SOURCE_DB = "pilot(1).db"

def inspect_source():
    abs_path = os.path.join(PROJECT_ROOT, SOURCE_DB)
    db_url = f"sqlite:///{abs_path}"
    print(f"--- [DEBUG] Inspecting Source: {abs_path} ---", file=sys.stderr)
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # List tables
            print("--- Tables ---", file=sys.stderr)
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            for t in tables:
                print(f"   {t[0]}", file=sys.stderr)
                
            # Inspect key tables: clientes, productos, pedidos, contactos, empresas_transporte
            key_tables = ['clientes', 'productos', 'pedidos', 'contactos', 'empresas_transporte']
            for kt in key_tables:
                # Find exact case
                target = next((t[0] for t in tables if t[0].lower() == kt), None)
                if target:
                    print(f"\n--- Schema: {target} ---", file=sys.stderr)
                    cols = conn.execute(text(f"PRAGMA table_info({target})")).fetchall()
                    for c in cols:
                        print(f"   - {c[1]} ({c[2]})", file=sys.stderr)
                else:
                    print(f"\n--- Missing Table: {kt} ---", file=sys.stderr)

            # Check Data Counts
            print("\n--- Row Counts ---", file=sys.stderr)
            for kt in key_tables:
                 target = next((t[0] for t in tables if t[0].lower() == kt), None)
                 if target:
                     cnt = conn.execute(text(f"SELECT count(*) FROM {target}")).scalar()
                     print(f"   {target}: {cnt}", file=sys.stderr)

    except Exception as e:
        print(f"    [ERROR] {e}", file=sys.stderr)

if __name__ == "__main__":
    inspect_source()
