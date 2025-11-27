import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from core.database import engine

def update_schema():
    with engine.connect() as conn:
        print("Adding columns to domicilios table...")
        try:
            conn.execute(text("ALTER TABLE domicilios ADD COLUMN transporte_id UUID;"))
            print("Added transporte_id")
        except Exception as e:
            print(f"Error adding transporte_id (maybe exists): {e}")

        try:
            conn.execute(text("ALTER TABLE domicilios ADD COLUMN intermediario_id UUID;"))
            print("Added intermediario_id")
        except Exception as e:
            print(f"Error adding intermediario_id (maybe exists): {e}")
            
        try:
            conn.execute(text("ALTER TABLE domicilios ADD CONSTRAINT fk_domicilios_transporte FOREIGN KEY (transporte_id) REFERENCES empresas_transporte(id);"))
            print("Added FK transporte")
        except Exception as e:
            print(f"Error adding FK transporte: {e}")

        try:
            conn.execute(text("ALTER TABLE domicilios ADD CONSTRAINT fk_domicilios_intermediario FOREIGN KEY (intermediario_id) REFERENCES empresas_transporte(id);"))
            print("Added FK intermediario")
        except Exception as e:
            print(f"Error adding FK intermediario: {e}")
            
        conn.commit()
        print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
