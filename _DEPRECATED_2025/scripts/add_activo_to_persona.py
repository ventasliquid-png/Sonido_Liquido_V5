import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import engine

def add_activo_to_persona():
    print("--- [MIGRATION] Adding 'activo' column to 'personas' table ---")
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='personas' AND column_name='activo'"))
            if result.fetchone():
                print("   -> Column 'activo' already exists.")
            else:
                print("   -> Adding column 'activo'...")
                connection.execute(text("ALTER TABLE personas ADD COLUMN activo BOOLEAN DEFAULT TRUE"))
                connection.commit()
                print("   -> Column added successfully.")
        except Exception as e:
            print(f"   -> Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_activo_to_persona()
