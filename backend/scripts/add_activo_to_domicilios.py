import sys
import os
from sqlalchemy import text

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal

def add_activo_to_domicilios():
    print("--- Migrating DB: Adding 'activo' to 'domicilios' ---")
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='domicilios' AND column_name='activo'"))
        if result.scalar():
            print("✅ Column 'activo' already exists in 'domicilios'.")
        else:
            print("Adding 'activo' column...")
            db.execute(text("ALTER TABLE domicilios ADD COLUMN activo BOOLEAN DEFAULT TRUE NOT NULL"))
            db.commit()
            print("✅ Column 'activo' added successfully.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_activo_to_domicilios()
