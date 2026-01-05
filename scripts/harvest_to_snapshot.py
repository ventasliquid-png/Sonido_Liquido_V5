import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import os
import sys

# URL Definitiva confirmada por test experimental
CLOUD_URL = "postgresql://postgres:SonidoV5_2025@104.197.57.226:5432/postgres?sslmode=require"
SNAPSHOT_DB = "iowa_snapshot.sqlite"

def harvest_to_sqlite():
    print(f"--- 📡 INICIANDO SNAPSHOT DESDE IOWA (Working: SonidoV5_2025) ---")
    
    try:
        # 1. Conectar a Cloud (Postgres)
        engine_cloud = create_engine(CLOUD_URL, connect_args={'connect_timeout': 15})
        
        # 2. Conectar a Local (SQLite Snapshot)
        if os.path.exists(SNAPSHOT_DB):
            os.remove(SNAPSHOT_DB)
        engine_local = create_engine(f"sqlite:///{SNAPSHOT_DB}")
        
        # 3. Descargar Tablas Críticas
        tables = ['clientes', 'productos']
        
        for table in tables:
            try:
                print(f"📥 Descargando {table.upper()} de IOWA...")
                df = pd.read_sql(f"SELECT * FROM {table}", engine_cloud)
                if not df.empty:
                    df.to_sql(table, engine_local, index=False)
                    print(f"   ✅ {len(df)} registros capturados.")
                else:
                    print(f"   ⚠️  Tabla '{table}' vacía en IOWA.")
            except Exception as e:
                print(f"   ❌ Error en tabla '{table}': {e}")
        
        if os.path.exists(SNAPSHOT_DB):
            print(f"\n✨ Snapshot completado en: {SNAPSHOT_DB}")
        else:
            print("\n⚠️ Snapshot falló o cargó un archivo vacío.")
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN HARVEST: {e}")
        sys.exit(1)

if __name__ == "__main__":
    harvest_to_sqlite()
