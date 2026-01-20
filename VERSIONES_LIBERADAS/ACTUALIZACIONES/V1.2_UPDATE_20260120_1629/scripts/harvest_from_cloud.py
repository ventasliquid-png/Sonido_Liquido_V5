import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Hardcoded connection for recovery
DB_PASSWORD = os.getenv('DB_PASSWORD')
CLOUD_DB_URL = f"postgresql://postgres:{DB_PASSWORD}@104.197.57.226:5432/postgres?sslmode=require"
DATA_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"

def harvest():
    print(f"--- Intentando conectar a IOWA (Cloud DB) ---")
    print(f"Target: {CLOUD_DB_URL.split('@')[1]}")
    
    try:
        engine = create_engine(CLOUD_DB_URL, connect_args={'connect_timeout': 10})
        
        # 1. Inspect Tables
        print("Consultando tablas...")
        
        # Clientes
        try:
            print("Bajando clientes...")
            df_cli = pd.read_sql("SELECT * FROM clientes", engine)
            print(f"  -> {len(df_cli)} clientes encontrados.")
            
            # Map columns to expected RAW format
            # Expected raw: nombre, cuit, etc.
            # DB has: razon_social, cuit, etc.
            df_cli['nombre'] = df_cli['razon_social']
            df_cli['estado'] = 'PENDIENTE' # Reset status for Cleaner to review
            
            # Save
            path = os.path.join(DATA_DIR, "clientes_limpios.csv") # Save as CLEAN to preserve edits? Or RAW?
            # User wants to SEE corrections. If we save as limpios.csv, DataCleaner picks it up first.
            df_cli.to_csv(path, index=False)
            print(f"  ✅ Guardado en {path}")
            
        except Exception as e:
            print(f"  ❌ Error bajando clientes: {e}")

        # Productos
        try:
            print("Bajando productos...")
            df_prod = pd.read_sql("SELECT * FROM productos", engine)
            print(f"  -> {len(df_prod)} productos encontrados.")
            
            df_prod['nombre_original'] = df_prod['nombre'] # Preserve
            df_prod['estado'] = 'PENDIENTE'
            
            path = os.path.join(DATA_DIR, "productos_limpios.csv")
            df_prod.to_csv(path, index=False)
            print(f"  ✅ Guardado en {path}")
            
        except Exception as e:
            print(f"  ❌ Error bajando productos: {e}")

    except Exception as e:
        print("\n❌ FALLO LA CONEXIÓN A LA NUBE.")
        print("Es muy probable que el Firewall o la IP estén bloqueando.")
        print(f"Detalle: {e}")

if __name__ == "__main__":
    harvest()
