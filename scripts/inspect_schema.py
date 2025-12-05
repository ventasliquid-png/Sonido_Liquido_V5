import sys
import os
from sqlalchemy import inspect, text

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import engine

def inspect_schema():
    inspector = inspect(engine)
    
    print("--- Columnas en 'rubros' ---")
    columns = inspector.get_columns('rubros')
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

    print("\n--- Columnas en 'productos' ---")
    columns = inspector.get_columns('productos')
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

    print("\n--- Columnas en 'productos_costos' ---")
    columns = inspector.get_columns('productos_costos')
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

if __name__ == "__main__":
    inspect_schema()
