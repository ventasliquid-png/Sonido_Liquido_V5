import importlib
import inspect
import sys
import os
import sqlite3

# FORCE LOCAL DB CONNECTION
os.environ["DATABASE_URL"] = "sqlite:///./pilot.db"

# from sqlalchemy.orm import DeclaredAttr # Error here
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import DeclarativeMeta

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)

# Manual Base import because of relative path issues if not careful
# We will use importlib for Base too or assumes it works
from backend.core.database import Base

# Database to check
DB_PATH = os.path.join(PROJECT_ROOT, "pilot.db")

def get_models_from_module(module_name):
    """Import a module and find all SQLAlchemy models in it."""
    models = []
    try:
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Base) and obj != Base:
                # Avoid imported classes from other modules if possible, 
                # but for now we just collect everything and dedup later.
                models.append(obj)
    except ImportError as e:
        print(f"[WARN] Could not import {module_name}: {e}")
    except Exception as e:
        print(f"[WARN] Error inspecting {module_name}: {e}")
    return models

def get_actual_db_columns(table_name):
    """Get columns from SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        return cols
    except Exception as e:
        print(f"[ERROR] DB Connection failed: {e}")
        return {}

def scan_integrity():
    print(f"--- STARTING INTEGRITY SCAN ON {DB_PATH} ---")
    
    # modules to check
    modules = [
        "backend.clientes.models",
        "backend.pedidos.models",
        "backend.productos.models",
        "backend.remitos.models",
        "backend.logistica.models",
        "backend.maestros.models",
        "backend.contactos.models",
        "backend.auth.models",
        "backend.proveedores.models"
    ]
    
    found_models = set()
    for mod in modules:
        found_models.update(get_models_from_module(mod))
        
    print(f"Found {len(found_models)} SQLAlchemy models.")
    
    issues_found = 0
    
    for model in found_models:
        if not hasattr(model, "__tablename__"):
            continue
            
        table_name = model.__tablename__
        mapper = sa_inspect(model)
        
        # Get expected columns from ORM
        expected_cols = {c.key for c in mapper.columns}
        
        # Get actual columns from DB
        actual_cols_map = get_actual_db_columns(table_name)
        actual_cols = set(actual_cols_map.keys())
        
        # Determine mismatch
        missing_in_db = expected_cols - actual_cols
        
        if missing_in_db:
            issues_found += 1
            print(f"\n[CRITICAL] Table '{table_name}' MISSING COLUMNS in DB:")
            for col in missing_in_db:
                print(f"   - {col}")
        else:
            # print(f"[OK] {table_name}")
            pass

    print("\n--- SCAN COMPLETE ---")
    if issues_found == 0:
        print("SUCCESS: No schema mismatches found.")
    else:
        print(f"FAILURE: Found {issues_found} tables with missing columns.")

if __name__ == "__main__":
    scan_integrity()
