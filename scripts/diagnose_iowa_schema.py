
import os
import psycopg2
from dotenv import load_dotenv

# Try to load env from current dir or root
load_dotenv()

IOWA_HOST = "104.197.57.226"
IOWA_USER = "postgres"
IOWA_PASS = "SonidoV5_2025"
IOWA_DB = "postgres"

def diagnose_iowa():
    print(f"--- [DIAGNOSTICO IOWA]: Intentando conectar a {IOWA_HOST}... ---")
    if not IOWA_PASS:
        print("❌ ERROR: DB_PASSWORD no encontrada en el entorno.")
        return

    try:
        conn = psycopg2.connect(
            host=IOWA_HOST,
            user=IOWA_USER,
            password=IOWA_PASS,
            dbname=IOWA_DB,
            sslmode='require',
            connect_timeout=5
        )
        print("✅ CONEXION EXITOSA.")
        
        cur = conn.cursor()
        
        # Check tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [t[0] for t in cur.fetchall()]
        print(f"Tablas encontradas: {tables}")
        
        if 'atenea_memory' in tables:
            print("\n--- Esquema de 'atenea_memory' ---")
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'atenea_memory'")
            for col in cur.fetchall():
                print(f"  {col[0]}: {col[1]}")
            
            # Check content types
            cur.execute("SELECT DISTINCT doc_type FROM atenea_memory")
            doc_types = [dt[0] for dt in cur.fetchall()]
            print(f"Tipos de documentos existentes: {doc_types}")
            
            # Count records
            cur.execute("SELECT count(*) FROM atenea_memory")
            count = cur.fetchone()[0]
            print(f"Total registros: {count}")
        else:
            print("❌ La tabla 'atenea_memory' no existe.")
            
        conn.close()
    except Exception as e:
        print(f"❌ FALLO DIAGNOSTICO: {e}")

if __name__ == "__main__":
    diagnose_iowa()
