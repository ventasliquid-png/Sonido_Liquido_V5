# scripts/generate_schema_report.py
import sys
import os
from sqlalchemy import inspect

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.database import engine

def inspect_schema():
    inspector = inspect(engine)
    
    tables_to_check = ['remitos', 'remitos_items', 'productos']
    
    print("# REPORTE DE ESQUEMA DE BASE DE DATOS (VALIDACIÓN ARQUITECTURA V7)\n")
    
    for table_name in tables_to_check:
        print(f"## Tabla: `{table_name}`")
        columns = inspector.get_columns(table_name)
        print("| Nombre Columna | Tipo | Nullable | Default |")
        print("| :--- | :--- | :--- | :--- |")
        for col in columns:
            # Filter interested columns for productos to avoid noise
            if table_name == 'productos' and col['name'] not in ['id', 'sku', 'nombre', 'stock_fisico', 'stock_reservado']:
                continue
                
            print(f"| {col['name']} | {col['type']} | {col['nullable']} | {col.get('default')} |")
        print("\n")

if __name__ == "__main__":
    inspect_schema()
