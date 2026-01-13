import sys
import os
from sqlalchemy import text

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal

def rename_ramos_to_segmentos():
    print("--- Migrating DB: Ramos -> Segmentos ---")
    db = SessionLocal()
    try:
        # Check if table 'ramos' exists
        result = db.execute(text("SELECT to_regclass('public.ramos')"))
        if result.scalar():
            print("Found table 'ramos'. Renaming to 'segmentos'...")
            db.execute(text("ALTER TABLE ramos RENAME TO segmentos"))
            db.commit()
            print("✅ Table renamed successfully.")
        else:
            print("Table 'ramos' not found. Checking if 'segmentos' exists...")
            result = db.execute(text("SELECT to_regclass('public.segmentos')"))
            if result.scalar():
                print("✅ Table 'segmentos' already exists.")
            else:
                print("❌ Neither 'ramos' nor 'segmentos' table found.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    rename_ramos_to_segmentos()
