
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath("."))

from backend.core.database import engine

def check_columns():
    inspector = inspect(engine)
    for col in inspector.get_columns('domicilios'):
        print(f"Name: {col['name']}, Type: {col['type']}")
    
    columns = [c['name'] for c in inspector.get_columns('domicilios')]
    
    required = ['metodo_entrega', 'modalidad_envio', 'origen_logistico']
    missing = [col for col in required if col not in columns]
    
    with engine.connect() as conn:
        if missing:
            print(f"MISSING COLUMNS: {missing}")
            # Fix columns
            try:
                for col in missing:
                    print(f"ADDING COLUMN: {col}")
                    conn.execute(text(f"ALTER TABLE domicilios ADD COLUMN {col} VARCHAR;"))
                conn.commit()
                print("COLUMNS ADDED SUCCESSFULLY.")
            except Exception as e:
                print(f"ERROR ADDING COLUMNS: {e}")
        else:
            print("ALL COLUMNS PRESENT.")

if __name__ == "__main__":
    check_columns()
