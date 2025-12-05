import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import engine

def update_schema():
    print("--- Updating Schema V5 (Productos & Rubros) ---")
    with engine.connect() as conn:
        # 1. Rubros: Rename descripcion -> nombre
        try:
            print("Checking 'rubros' table...")
            # Check if 'nombre' exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='rubros' AND column_name='nombre'"))
            if not result.fetchone():
                print("Renaming 'descripcion' to 'nombre' in 'rubros'...")
                conn.execute(text("ALTER TABLE rubros RENAME COLUMN descripcion TO nombre"))
                conn.commit()
                print("✅ Renamed column.")
            else:
                print("ℹ️ Column 'nombre' already exists.")
        except Exception as e:
            print(f"❌ Error updating rubros: {e}")

        # 2. Productos: Add new columns
        new_columns = [
            ("proveedor_habitual_id", "UUID"),
            ("tasa_iva_id", "INTEGER"),
            ("tipo_producto", "VARCHAR DEFAULT 'VENTA'"),
            ("unidad_stock_id", "INTEGER"),
            ("unidad_compra_id", "INTEGER"),
            ("factor_compra", "NUMERIC(10, 2) DEFAULT 1.0"),
        ]

        print("Checking 'productos' table...")
        for col_name, col_type in new_columns:
            try:
                result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='productos' AND column_name='{col_name}'"))
                if not result.fetchone():
                    print(f"Adding column '{col_name}'...")
                    conn.execute(text(f"ALTER TABLE productos ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"✅ Added {col_name}.")
                else:
                    print(f"ℹ️ Column '{col_name}' already exists.")
            except Exception as e:
                print(f"❌ Error adding {col_name}: {e}")

        # 3. Fix Defaults for created_at
        tables = ['rubros', 'productos']
        for table in tables:
            try:
                print(f"Setting default for 'created_at' in '{table}'...")
                conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN created_at SET DEFAULT NOW()"))
                print(f"✅ Set default for created_at in {table}.")
                
                print(f"Setting default for 'updated_at' in '{table}'...")
                conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN updated_at SET DEFAULT NOW()"))
                print(f"✅ Set default for updated_at in {table}.")
                
                conn.commit()
            except Exception as e:
                print(f"❌ Error setting defaults for {table}: {e}")

    print("--- Schema Update Complete ---")

if __name__ == "__main__":
    update_schema()
