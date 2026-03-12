
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
import sys

# --- CONFIGURACIÓN IOWA (DESTINO) ---
IOWA_HOST = "104.197.57.226"
IOWA_USER = "postgres"
IOWA_PASS = os.getenv('DB_PASSWORD')
IOWA_DB = "postgres"

# --- CONFIGURACIÓN PILOTO (ORIGEN) ---
LOCAL_DB_PATH = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\produccion.db"

def get_local_connection():
    try:
        return sqlite3.connect(LOCAL_DB_PATH)
    except Exception as e:
        print(f"❌ Error conectando a SQLite Local: {e}")
        sys.exit(1)

def get_iowa_connection():
    try:
        return psycopg2.connect(
            host=IOWA_HOST,
            user=IOWA_USER,
            password=IOWA_PASS,
            dbname=IOWA_DB,
            sslmode='require'
        )
    except Exception as e:
        print(f"❌ Error conectando a IOWA Cloud: {e}")
        sys.exit(1)

def migrate_table(local_conn, remote_conn, table_name, columns):
    print(f"\n🚀 Migrando tabla: {table_name}...")
    
    # 1. Leer de Local
    cursor_local = local_conn.cursor()
    col_str = ", ".join(columns)
    try:
        cursor_local.execute(f"SELECT {col_str} FROM {table_name}")
        rows = cursor_local.fetchall()
    except Exception as e:
        print(f"⚠️  Tabla {table_name} no existe o error en local: {e}")
        return

    if not rows:
        print(f"ℹ️  Tabla {table_name} vacía en local. Saltando.")
        return

    print(f"📦 Encontrados {len(rows)} registros en local.")

    # 2. Limpiar Destino (Truncate con Cascade para evitar FK errors)
    cursor_remote = remote_conn.cursor()
    try:
        print(f"🧹 Limpiando tabla remota {table_name}...")
        cursor_remote.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
    except Exception as e:
        print(f"⚠️  Error truncando {table_name} (quizás no existe): {e}")
        remote_conn.rollback()
        return

    # 3. Insertar en IOWA
    # Generar placeholders %s, %s, ...
    placeholders = ",".join(["%s"] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({col_str}) VALUES %s"
    
    try:
        execute_values(cursor_remote, insert_query, rows)
        remote_conn.commit()
        print(f"✅ Éxito: {len(rows)} registros insertados en IOWA.")
    except Exception as e:
        print(f"❌ Error insertando en IOWA: {e}")
        remote_conn.rollback()

def run_migration():
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ No se encuentra la base de datos local: {LOCAL_DB_PATH}")
        return

    local_conn = get_local_connection()
    remote_conn = get_iowa_connection()

    # --- DEFINIR TABLAS A MIGRAR ---
    # Orden importe por FKs: Maestros -> Clientes -> Productos
    
    # 1. Rubros (Necesario para productos)
    # Nota: SQLite y Postgres pueden diferir. Asumimos estructura compatible V5.
    # migrate_table(local_conn, remote_conn, "rubros", ["id", "nombre", "codigo", "padre_id", "activo"])

    # 2. Clientes
    # Columnas comunes seguras
    cols_clientes = [
        "id", "razon_social", "cuit", "activo", 
        "condicion_iva_id", "segmento_id" 
        # Agregaremos mas si existen en local
    ]
    # Validar columnas existentes dinamicamente seria mejor, pero por ahora hardcode seguro
    # Para ser mas robustos, leemos las columnas de sqlite
    
    cursor = local_conn.execute("PRAGMA table_info(clientes)")
    col_names = [row[1] for row in cursor.fetchall()]
    # Filtrar solo las que sabemos que existen en destino o son seguras
    # Por simplicidad en este script rapido, migraremos las criticas detectadas en el cleaner
    
    # En V5 el cleaner usa: razon_social, cuit, activo.
    # El resto puede ser defaults o nulos. Asumimos compatibilidad de nombres.
    
    # --- MIGRACIÓN CLIENTES ---
    print("\n🚀 Migrando tabla: clientes...")
    cursor_local = local_conn.cursor()
    cursor_local.execute("SELECT id, razon_social, cuit, activo FROM clientes")
    rows = cursor_local.fetchall()

    if rows:
        print(f"📦 Encontrados {len(rows)} registros.")
        
        # Casting manual: SQLite (1/0) -> Python Bool (True/False) -> Postgres (boolean)
        cleaned_rows = []
        for r in rows:
            # r = (id, razon_social, cuit, activo_int)
            cleaned_rows.append((r[0], r[1], r[2], bool(r[3])))

        cursor_remote = remote_conn.cursor()
        try:
            print("🧹 Limpiando tabla remota clientes...")
            cursor_remote.execute("TRUNCATE TABLE clientes CASCADE;")
            
            # Incluimos 'id' en el INSERT
            query = "INSERT INTO clientes (id, razon_social, cuit, activo) VALUES %s"
            execute_values(cursor_remote, query, cleaned_rows)
            
            # Actualizar secuencia de IDs en Postgres para evitar conflictos futuros
            max_id = max([r[0] for r in rows])
            cursor_remote.execute(f"SELECT setval('clientes_id_seq', {max_id}, true)")
            
            remote_conn.commit()
            print(f"✅ Éxito: {len(rows)} clientes insertados.")
        except Exception as e:
            print(f"❌ Error migrando clientes: {e}")
            remote_conn.rollback()

    # --- MIGRACIÓN PRODUCTOS ---
    print("\n🚀 Migrando tabla: productos...")
    # Asumimos que productos tiene nombre y activo
    cursor_local.execute("SELECT nombre, activo FROM productos")
    prod_rows = cursor_local.fetchall()
    
    if prod_rows:
        # Cast activo
        cleaned_prods = [(r[0], bool(r[1])) for r in prod_rows]
        
        cursor_remote = remote_conn.cursor()
        try:
            print("🧹 Limpiando tabla remota productos...")
            # Cuidado con FKs (Rubro). Si borramos productos, necesitamos asegurar rubros antes? 
            # Como IOWA esta vacio o sucio, Truncate Cascade esta bien.
            # PERO necesitamos un rubro default si o si.
            
            # 1. Asegurar rubro 'GENERAL'
            cursor_remote.execute("SELECT id FROM rubros WHERE nombre = 'GENERAL'")
            rubro = cursor_remote.fetchone()
            if not rubro:
                cursor_remote.execute("INSERT INTO rubros (nombre, codigo, activo) VALUES ('GENERAL', 'GEN', true) RETURNING id")
                rubro_id = cursor_remote.fetchone()[0]
            else:
                rubro_id = rubro[0]
                
            # Insertar productos con rubro default
            # Postgres requiere rubro_id. Local no lo tenia en la query anterior.
            # Vamos a insertar con rubro_default hardcodeado para esta migracion simple.
            
            final_prods = [(r[0], r[1], rubro_id) for r in cleaned_prods]
            
            cursor_remote.execute("TRUNCATE TABLE productos CASCADE;")
            query_prod = "INSERT INTO productos (nombre, activo, rubro_id) VALUES %s"
            execute_values(cursor_remote, query_prod, final_prods)
            remote_conn.commit()
            print(f"✅ Éxito: {len(final_prods)} productos insertados.")
            
        except Exception as e:
             print(f"❌ Error migrando productos: {e}")
             remote_conn.rollback()

    print("\n🏁 Migración Finalizada.")
    local_conn.close()
    remote_conn.close()

if __name__ == "__main__":
    run_migration()
