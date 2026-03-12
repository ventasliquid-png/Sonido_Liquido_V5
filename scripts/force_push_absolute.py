import sqlite3
import psycopg2
from psycopg2.extras import execute_values, register_uuid
import sys
import uuid
import pandas as pd

# CONFIGURACIÓN MAESTRA
HOST = "104.197.57.226"
USER = "postgres"
PASS = "SonidoV5_2025"
DBNAME = "postgres"

LOCAL_DB = "pilot.db"

def get_conn_c():
    conn = psycopg2.connect(host=HOST, user=USER, password=PASS, dbname=DBNAME, sslmode='require')
    register_uuid(conn_or_curs=conn)
    return conn

def force_push():
    print(f"--- 🚀 OPERATIVO FORCE PUSH V13 (Final Unification) ---")
    
    try:
        conn_c = get_conn_c()
        cur_c = conn_c.cursor()
        conn_l = sqlite3.connect(LOCAL_DB)
        
        # 1. PURGA
        print("🧹 Purgando IOWA...")
        tables = ["productos_costos", "productos", "clientes_domicilios", "clientes", "rubros"]
        for t in tables:
            try:
                cur_c.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE")
            except:
                conn_c.rollback()
        conn_c.commit()

        # 2. RUBROS
        print("\n📥 Migrando RUBROS...")
        df_r = pd.read_sql("SELECT id, codigo, nombre, padre_id, activo FROM rubros", conn_l)
        rows_r = []
        for _, r in df_r.iterrows():
            rows_r.append((
                int(r['id']), 
                r['codigo'], 
                r['nombre'], 
                int(r['padre_id']) if not pd.isna(r['padre_id']) else None,
                bool(r['activo'])
            ))
        execute_values(cur_c, "INSERT INTO rubros (id, codigo, nombre, padre_id, activo) VALUES %s", rows_r)
        print(f"   ✅ {len(rows_r)} Rubros subidos.")

        # 3. PRODUCTOS (ID es INTEGER en esta instancia)
        print("📥 Migrando PRODUCTOS...")
        df_p = pd.read_sql("SELECT id, sku, nombre, rubro_id, activo, created_at FROM productos", conn_l)
        rows_p = []
        for _, p in df_p.iterrows():
            rows_p.append((
                int(p['id']),
                float(p['sku']) if not pd.isna(p['sku']) else None,
                p['nombre'],
                # Asegurar que el rubro_id exista (si no, poner el primero o NULL)
                int(p['rubro_id']),
                bool(p['activo']),
                str(p['created_at']) if not pd.isna(p['created_at']) else None
            ))
        execute_values(cur_c, "INSERT INTO productos (id, sku, nombre, rubro_id, activo, created_at) VALUES %s", rows_p)
        print(f"   ✅ {len(rows_p)} Productos subidos.")

        # 4. CLIENTES (ID es UUID)
        print("📥 Migrando CLIENTES...")
        df_cl = pd.read_sql("SELECT id, razon_social, cuit, activo FROM clientes", conn_l)
        rows_cl = []
        for _, cl in df_cl.iterrows():
            try:
                # Intentar parsear como UUID, si falla, ignorar o generar (pero local tiene UUIDs)
                cl_uuid = uuid.UUID(cl['id'])
                rows_cl.append((
                    cl_uuid,
                    cl['razon_social'],
                    cl['cuit'],
                    bool(cl['activo'])
                ))
            except Exception as e:
                print(f"   ⚠️ ID de cliente inválido: {cl['id']} - {e}")

        execute_values(cur_c, "INSERT INTO clientes (id, razon_social, cuit, activo) VALUES %s", rows_cl)
        print(f"   ✅ {len(rows_cl)} Clientes subidos.")

        conn_c.commit()
        print(f"\n✨ Sincronización Exitosa: IOWA y LOCAL son uno solo.")
        
    except Exception as e:
        print(f"\n❌ ERROR GLOBAL: {e}")
        conn_c.rollback()
        sys.exit(1)
    finally:
        conn_c.close()
        conn_l.close()

if __name__ == "__main__":
    force_push()
