import sys
import os
from sqlalchemy import create_engine, text, inspect

# Add project root to path
sys.path.append(os.getcwd())

# Hardcoded Cloud URL (IOWA)
CLOUD_DB_URL = "postgresql://postgres:Spawn1482.@104.197.57.226:5432/postgres?sslmode=require"

def migrate_cloud():
    print(f"--- INICIANDO MIGRACION CLOUD (IOWA) - MOTOR DE PRECIOS V5 ---")
    print(f"Target: {CLOUD_DB_URL.split('@')[1]}")

    engine = create_engine(CLOUD_DB_URL)
    inspector = inspect(engine)

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. Update productos_costos
            # Check if table exists first
            if inspector.has_table('productos_costos'):
                columns_costos = [c['name'] for c in inspector.get_columns('productos_costos')]
                
                if 'precio_fijo_override' not in columns_costos:
                    print("Agregando 'precio_fijo_override' a 'productos_costos'...")
                    conn.execute(text("ALTER TABLE productos_costos ADD COLUMN precio_fijo_override NUMERIC(12, 2) DEFAULT NULL"))
                else:
                    print("Columna 'precio_fijo_override' ya existe.")

                if 'permitir_descuentos' not in columns_costos:
                    print("Agregando 'permitir_descuentos' a 'productos_costos'...")
                    conn.execute(text("ALTER TABLE productos_costos ADD COLUMN permitir_descuentos BOOLEAN DEFAULT TRUE"))
                else:
                    print("Columna 'permitir_descuentos' ya existe.")
            else:
                print("⚠ Tabla 'productos_costos' no existe en Cloud. Saltando...")

            # 2. Update clientes
            if inspector.has_table('clientes'):
                columns_clientes = [c['name'] for c in inspector.get_columns('clientes')]
                
                if 'estrategia_precio' not in columns_clientes:
                    print("Agregando 'estrategia_precio' a 'clientes'...")
                    conn.execute(text("ALTER TABLE clientes ADD COLUMN estrategia_precio VARCHAR DEFAULT 'MAYORISTA_FISCAL'"))
                else:
                    print("Columna 'estrategia_precio' ya existe.")
            else:
                 print("⚠ Tabla 'clientes' no existe en Cloud. Saltando...")

            trans.commit()
            print("--- MIGRACION CLOUD EXITOSA ---")
            
        except Exception as e:
            trans.rollback()
            print(f"!!! ERROR EN MIGRACION CLOUD: {e}")
            raise e

if __name__ == "__main__":
    migrate_cloud()
