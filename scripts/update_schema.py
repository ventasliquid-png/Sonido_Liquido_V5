
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

# Force Local DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
pilot_db_path = os.path.join(ROOT_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{pilot_db_path}"

print(f"--- MIGRATING SCHEMA ON: {DATABASE_URL} ---")
engine = create_engine(DATABASE_URL)

def add_column_if_not_exists(conn, table, column, definition):
    try:
        # Check if column exists
        # SQLite defines PRAGMA table_info(table_name)
        # But easier just to try adding and ignore error? No, cleaner to check.
        # But SQLite 'ALTER TABLE ADD COLUMN' is safe?
        query = text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.execute(query)
        print(f"  [ADDED] {table}.{column}")
    except Exception as e:
        if "duplicate column" in str(e).lower() or "no such table" in str(e).lower():
            print(f"  [SKIP] {table}.{column} (Exists or Error: {e})")
        else:
             # SQLite throws "duplicate column name"
             print(f"  [SKIP] {table}.{column} (Already exists)")

def migrate_schema():
    print("\n--- ADDING MISSING COLUMNS (V5.5/V7) ---")
    with engine.connect() as conn:
        # Metadata Logística (V5.5)
        add_column_if_not_exists(conn, "productos", "proveedor_habitual_id", "CHAR(32)")
        add_column_if_not_exists(conn, "productos", "presentacion_compra", "VARCHAR")
        add_column_if_not_exists(conn, "productos", "unidades_bulto", "NUMERIC DEFAULT 1.0")
        
        # Fiscal
        add_column_if_not_exists(conn, "productos", "tasa_iva_id", "INTEGER")
        
        # Naturaleza
        add_column_if_not_exists(conn, "productos", "tipo_producto", "VARCHAR DEFAULT 'VENTA'")
        
        # Stock Táctico (V7)
        add_column_if_not_exists(conn, "productos", "stock_fisico", "NUMERIC DEFAULT 0.0")
        add_column_if_not_exists(conn, "productos", "stock_reservado", "NUMERIC DEFAULT 0.0")
        
        # Matemática de Unidades
        add_column_if_not_exists(conn, "productos", "unidad_stock_id", "INTEGER")
        add_column_if_not_exists(conn, "productos", "unidad_compra_id", "INTEGER")
        add_column_if_not_exists(conn, "productos", "factor_compra", "NUMERIC DEFAULT 1.0")
        add_column_if_not_exists(conn, "productos", "venta_minima", "NUMERIC DEFAULT 1.0")
        
        # Commit not needed for DDL in some connection modes, but safe to call if transaction active?
        # Engine connect usually autocommits DDL in sqlite?
        # Let's try.
        
    print("\n--- MIGRATION COMPLETE ---")

if __name__ == "__main__":
    try:
        migrate_schema()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
