# scripts/inspect_tables.py
import sys
import os
from sqlalchemy import inspect

sys.path.append(os.getcwd())
from backend.core.database import engine

def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_tables()
    print("Tablas encontradas:", tables)
    
    if "empresas_transporte" in tables:
        print("✅ empresas_transporte EXISTE")
    else:
        print("❌ empresas_transporte NO EXISTE")

if __name__ == "__main__":
    list_tables()
