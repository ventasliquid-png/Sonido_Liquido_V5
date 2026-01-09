import sqlite3
import psycopg2
import os
from dotenv import dotenv_values

# Configuration
LOCAL_DB = r"c:\dev\Sonido_Liquido_V5\pilot.db"
ENV_PATH = r"c:\dev\Sonido_Liquido_V5\backend\.env"

config = dotenv_values(ENV_PATH)
IOWA_URL = config.get("DATABASE_URL")
if not IOWA_URL:
    print("❌ ERROR: DATABASE_URL not found in .env")
    exit(1)

# Helper for psycopg2 connection
from urllib.parse import urlparse
p = urlparse(IOWA_URL)
pg_config = {
    'dbname': p.path[1:],
    'user': p.username,
    'password': p.password,
    'host': p.hostname,
    'port': p.port
}

# Topological Sort: Masters -> Entities -> Transactions
TABLES = [
    'provincias',
    'condiciones_iva', 
    'segmentos', 
    'rubros', 
    'unidades', 
    'tasas_iva', 
    'listas_precios',
    'clientes', 
    'productos', 
    'domicilios', 
    'pedidos', 
    'pedidos_items'
]

def wipe_and_replace():
    print("🚀 INICIANDO PROTOCOLO 'PUSH SESSION TO IOWA'...")
    
    # 1. Connect to Local
    try:
        local_conn = sqlite3.connect(LOCAL_DB)
        local_conn.row_factory = sqlite3.Row
        local_cursor = local_conn.cursor()
        print(f"✅ Conectado a LOCAL: {LOCAL_DB}")
    except Exception as e:
        print(f"❌ Error conectando a Local: {e}")
        return

    # 2. Connect to IOWA
    try:
        iowa_conn = psycopg2.connect(**pg_config)
        iowa_cursor = iowa_conn.cursor()
        print(f"✅ Conectado a IOWA: {pg_config['host']}")
    except Exception as e:
        print(f"❌ Error conectando a IOWA: {e}")
        return

    try:
        # 3. WIPE IOWA
        print("🧹 WIPING IOWA TABLES (Cascade)...")
        # Order matters for constraints
        iowa_cursor.execute("TRUNCATE pedidos_items, pedidos, domicilios, clientes, productos, listas_precios, segmentos, condiciones_iva, rubros, unidades, tasas_iva, provincias RESTART IDENTITY CASCADE;")
        iowa_conn.commit()
        print("✨ IOWA LIMPIA (Tabula Rasa)")

        # 4. TRANSFER DATA
        for table in TABLES:
            print(f"📦 Transfiriendo tabla: {table}...")
            
            # Read Local
            try:
                rows = local_cursor.execute(f"SELECT * FROM {table}").fetchall()
            except sqlite3.OperationalError:
                print(f"⚠️ Tabla local {table} no existe o vacía. Saltando.")
                continue

            if not rows:
                print(f"ℹ️ Tabla {table} vacía. Saltando.")
                continue

            # Prepare columns and values
            columns = list(rows[0].keys())
            col_str = ",".join(columns)
            placeholders = ",".join(["%s"] * len(columns))
            query = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
            
            # Sanitizer for Booleans (SQLite 0/1 -> Postgres False/True)
            bool_cols = [
                'activo', 'es_fiscal', 'es_entrega', 'liberado_despacho', 
                'es_combo', 'stock_infinito', 'controlar_stock',
                'requiere_auditoria', 'es_kit', 'es_servicio', 'permite_venta',
                'tiene_bonus', 'es_insumo' 
            ]
            
            data = []
            for row in rows:
                new_row = []
                for col_name, val in zip(columns, row):
                    if col_name in bool_cols and val in [0, 1]:
                        new_row.append(bool(val))
                    else:
                        new_row.append(val)
                data.append(tuple(new_row))
                        
            # Write to IOWA
            try:
                iowa_cursor.executemany(query, data)
                iowa_conn.commit()
                print(f"   -> {len(data)} registros insertados en {table}.")
            except Exception as e:
                iowa_conn.rollback()
                print(f"❌ Error insertando en {table}: {e}")

        # 5. VERIFICACIÓN FINAL
        iowa_cursor.execute("SELECT razon_social FROM clientes WHERE razon_social LIKE '%GELATO%'")
        check = iowa_cursor.fetchone()
        
        if check:
            print(f"🏆 VALIDACIÓN EXITOSA: Cliente testigo encontrado: {check[0]}")
        else:
            print("⚠️ ADVERTENCIA: Cliente testigo no encontrado en IOWA.")

        iowa_conn.commit()

    except Exception as e:
        print(f"❌ Error Crítico durante la sincronización: {e}")
        iowa_conn.rollback()
    
    finally:
        local_conn.close()
        iowa_conn.close()
        print("🏁 PROTOCOLO FINALIZADO.")

if __name__ == "__main__":
    wipe_and_replace()
