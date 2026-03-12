import psycopg2
from dotenv import dotenv_values
import os

# FORCE LOAD backend/.env
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
config = dotenv_values(env_path)

if "DATABASE_URL" not in config:
    print("❌ ERROR: DATABASE_URL not found in .env")
    exit(1)

IOWA_URL = config["DATABASE_URL"]

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

def drop_all():
    print("🔥 INICIANDO PROTOCOLO TOTAL WIPEOUT EN IOWA...")
    try:
        conn = psycopg2.connect(**pg_config)
        cursor = conn.cursor()
        
        # Drop all tables in public schema
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        conn.commit()
        print("✅ TODAS LAS TABLAS ELIMINADAS (Clean Slate).")
        conn.close()
    except Exception as e:
        print(f"❌ Error during wipeout: {e}")

if __name__ == "__main__":
    drop_all()
