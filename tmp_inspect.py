import os
import sys

# Absolute path to DB
db_path = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from backend.core.database import engine
from sqlalchemy import inspect

def inspect_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"--- TABLES IN DB ---")
    print(tables)
    
    for table_name in ['clientes', 'domicilios']:
        if table_name in tables:
            columns = inspector.get_columns(table_name)
            print(f"\n--- COLUMNS IN '{table_name}' TABLE ---")
            for column in columns:
                print(f"- {column['name']}")
        else:
            print(f"\n[!] Table '{table_name}' not found.")

if __name__ == "__main__":
    inspect_db()
