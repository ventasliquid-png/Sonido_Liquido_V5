import sys
import os
from sqlalchemy import text, inspect

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import engine

def migrate():
    inspector = inspect(engine)
    
    print("--- INICIANDO MIGRACION MOTOR DE PRECIOS V5 ---")

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. Update productos_costos
            columns_costos = [c['name'] for c in inspector.get_columns('productos_costos')]
            
            if 'precio_fijo_override' not in columns_costos:
                print("Agregando columna 'precio_fijo_override' a 'productos_costos'...")
                conn.execute(text("ALTER TABLE productos_costos ADD COLUMN precio_fijo_override NUMERIC(12, 2) DEFAULT NULL"))
            else:
                print("Columna 'precio_fijo_override' ya existe.")

            if 'permitir_descuentos' not in columns_costos:
                print("Agregando columna 'permitir_descuentos' a 'productos_costos'...")
                # SQLite doesn't support adding column with default true as easily in one go compatible with all, 
                # but standard SQL does.
                conn.execute(text("ALTER TABLE productos_costos ADD COLUMN permitir_descuentos BOOLEAN DEFAULT 1"))
            else:
                print("Columna 'permitir_descuentos' ya existe.")

            # 2. Update clientes
            columns_clientes = [c['name'] for c in inspector.get_columns('clientes')]
            
            if 'estrategia_precio' not in columns_clientes:
                print("Agregando columna 'estrategia_precio' a 'clientes'...")
                conn.execute(text("ALTER TABLE clientes ADD COLUMN estrategia_precio VARCHAR DEFAULT 'MAYORISTA_FISCAL'"))
            else:
                print("Columna 'estrategia_precio' ya existe.")

            trans.commit()
            print("--- MIGRACION EXITOSA ---")
            
        except Exception as e:
            trans.rollback()
            print(f"!!! ERROR EN MIGRACION: {e}")
            raise e

if __name__ == "__main__":
    migrate()
