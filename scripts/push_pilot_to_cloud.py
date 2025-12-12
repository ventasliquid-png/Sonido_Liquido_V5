import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import os
import sys

# Hardcoded connection for recovery (Same as harvest)
CLOUD_DB_URL = "postgresql://postgres:Spawn1482.@104.197.57.226:5432/postgres?sslmode=require"
DATA_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"

def push_to_cloud():
    print(f"--- Sincronizando PILOTO -> IOWA (Cloud) ---")
    
    try:
        engine = create_engine(CLOUD_DB_URL, connect_args={'connect_timeout': 10})
        
        # 1. Push Clientes
        path_cli = os.path.join(DATA_DIR, "clientes_master.csv")
        if os.path.exists(path_cli):
            print(f"Leyendo {path_cli}...")
            df_cli = pd.read_csv(path_cli)
            
            if not df_cli.empty:
                print(f"Subiendo {len(df_cli)} clientes...")
                # Iterate and Upsert
                with engine.connect() as conn:
                    for _, row in df_cli.iterrows():
                        cuit = str(row['cuit'])
                        nombre = row['razon_social']
                        
                        # Check exist
                        check_sql = text("SELECT id FROM clientes WHERE cuit = :cuit")
                        existing = conn.execute(check_sql, {"cuit": cuit}).fetchone()
                        
                        if existing:
                            # Update Name
                            upd_sql = text("UPDATE clientes SET razon_social = :nombre, updated_at = NOW() WHERE cuit = :cuit")
                            conn.execute(upd_sql, {"nombre": nombre, "cuit": cuit})
                            print(f"  [UPD] {nombre}")
                        else:
                            # Insert (Minimal)
                            # UUID generation in Postgres default?
                            ins_sql = text("""
                                INSERT INTO clientes (id, razon_social, cuit, activo, created_at, updated_at)
                                VALUES (gen_random_uuid(), :nombre, :cuit, true, NOW(), NOW())
                            """)
                            conn.execute(ins_sql, {"nombre": nombre, "cuit": cuit})
                            print(f"  [NEW] {nombre}")
                    
                    conn.commit()
                print("✅ Clientes sincronizados.")
            else:
                print("⚠ clientes_master.csv está vacío.")
        else:
             print("⚠ No se encontró clientes_master.csv")

        # 2. Push Productos
        path_prod = os.path.join(DATA_DIR, "productos_master.csv")
        if os.path.exists(path_prod):
            print(f"Leyendo {path_prod}...")
            df_prod = pd.read_csv(path_prod)
            
            if not df_prod.empty:
                print(f"Subiendo {len(df_prod)} productos...")
                 # Iterate and Upsert
                with engine.connect() as conn:
                     # Get Rubro Default ID from Cloud? 
                     # We assume Rubro 'GENERAL' exists or handle it?
                     # Let's check/create Rubro 'GENERAL' on Cloud first
                     rubro_sql = text("SELECT id FROM rubros WHERE nombre = 'GENERAL'")
                     rubro_id = conn.execute(rubro_sql).scalar()
                     
                     if not rubro_id:
                         print("  Creando Rubro GENERAL en Cloud...")
                         ins_rub = text("INSERT INTO rubros (codigo, nombre, activo) VALUES ('GEN', 'GENERAL', true) RETURNING id")
                         rubro_id = conn.execute(ins_rub).scalar()
                         conn.commit()

                     for _, row in df_prod.iterrows():
                        nombre = row['nombre']
                        
                        # Check exist
                        check_sql = text("SELECT id FROM productos WHERE nombre = :nombre")
                        existing = conn.execute(check_sql, {"nombre": nombre}).fetchone()
                        
                        if existing:
                             # Exists
                             print(f"  [SKP] {nombre} (Ya existe)")
                        else:
                            # Insert
                            ins_sql = text("""
                                INSERT INTO productos (nombre, rubro_id, activo, created_at)
                                VALUES (:nombre, :rubro_id, true, NOW())
                            """)
                            conn.execute(ins_sql, {"nombre": nombre, "rubro_id": rubro_id})
                            print(f"  [NEW] {nombre}")
                     
                     conn.commit()
                print("✅ Productos sincronizados.")
            else:
                 print("⚠ productos_master.csv está vacío.")
        else:
             print("⚠ No se encontró productos_master.csv")

    except Exception as e:
        print("\n❌ FALLO LA SINCRONIZACIÓN A LA NUBE.")
        print(f"Detalle: {e}")

if __name__ == "__main__":
    push_to_cloud()
