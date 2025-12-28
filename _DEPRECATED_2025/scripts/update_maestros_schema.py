import sys
import os
from sqlalchemy import text

# Add backend directory to path so 'core' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import engine

def update_schema():
    print("--- [MIGRATION] Updating Maestros Schema ---")
    
    # 1. Create Enum Type
    print("1. Checking 'tipo_lista_enum'...")
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("CREATE TYPE tipo_lista_enum AS ENUM ('FISCAL', 'PRESUPUESTO');"))
            trans.commit()
            print("   -> Created 'tipo_lista_enum'.")
        except Exception as e:
            trans.rollback()
            print("   -> Enum likely exists (Skipping).")

    # 2. Update 'listas_precios'
    print("2. Updating 'listas_precios' table...")
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("ALTER TABLE listas_precios ADD COLUMN IF NOT EXISTS coeficiente NUMERIC(10, 4) DEFAULT 1.0;"))
            connection.execute(text("ALTER TABLE listas_precios ADD COLUMN IF NOT EXISTS tipo tipo_lista_enum DEFAULT 'PRESUPUESTO';"))
            trans.commit()
            print("   -> Columns added.")
        except Exception as e:
            trans.rollback()
            print("   -> Error updating table:", e)

    # 3. Create 'ramos'
    print("3. Creating 'ramos' table...")
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS ramos (
                    id UUID PRIMARY KEY,
                    nombre VARCHAR NOT NULL UNIQUE,
                    descripcion VARCHAR,
                    activo BOOLEAN DEFAULT TRUE
                );
            """))
            trans.commit()
            print("   -> Table 'ramos' ready.")
        except Exception as e:
            trans.rollback()
            print("   -> Error creating table:", e)

    # 4. Create 'vendedores'
    print("4. Creating 'vendedores' table...")
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS vendedores (
                    id UUID PRIMARY KEY,
                    nombre VARCHAR NOT NULL,
                    email VARCHAR,
                    telefono VARCHAR,
                    comision_porcentaje NUMERIC(5, 2) DEFAULT 0,
                    cbu_alias VARCHAR,
                    activo BOOLEAN DEFAULT TRUE
                );
            """))
            trans.commit()
            print("   -> Table 'vendedores' ready.")
        except Exception as e:
            trans.rollback()
            print("   -> Error creating table:", e)

    print("--- [MIGRATION] Completed Successfully ---")

if __name__ == "__main__":
    update_schema()
