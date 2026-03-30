import sqlite3
import os
from dotenv import load_dotenv
# Forzamos .env antes de cualquier import de core.database
load_dotenv('backend/.env', override=True)

from backend.core.database import Base, engine
from sqlalchemy import inspect

# Ensure we are using the correct DB for the audit script
# (The engine in core.database should already be configured to pilot_v5x.db after our previous fixes)

def audit_schema():
    print(f"[*] Starting Schema Integrity Audit...")
    
    # Get SQLAlchemy metadata
    # (We assume models are already imported via main.py or similar, 
    # but here we might need to import them explicitly to populate Base.metadata)
    try:
        from backend.clientes.models import Cliente, Domicilio, Provincia
        from backend.productos.models import Producto, ProductoCosto, Rubro
        from backend.contactos.models import Persona, Vinculo
    except ImportError as e:
        print(f"[!] Error importing models: {e}")
        return

    inspector = inspect(engine)
    
    tables_to_check = ['clientes', 'productos', 'productos_costos', 'personas', 'vinculos', 'rubros', 'domicilios', 'provincias']
    
    for table_name in tables_to_check:
        print(f"\n[Table: {table_name}]")
        
        # Get columns from DB
        db_columns = {col['name'] for col in inspector.get_columns(table_name)}
        
        # Get columns from SQLAlchemy Model
        # Find the class for this table
        model_class = next((cls for cls in Base.__subclasses__() if getattr(cls, '__tablename__', None) == table_name), None)
        
        if not model_class:
            print(f" [?] No SQLAlchemy model found for table {table_name}")
            continue
            
        model_columns = {col.name for col in model_class.__table__.columns}
        
        missing_in_db = model_columns - db_columns
        missing_in_model = db_columns - model_columns
        
        if missing_in_db:
            print(f" [!] MISSING IN DB: {missing_in_db}")
        else:
            print(f" [OK] DB columns match models.")
            
        if missing_in_model:
            print(f" [?] Extra in DB (not in model): {missing_in_model}")

if __name__ == "__main__":
    audit_schema()
