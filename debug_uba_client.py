import sqlalchemy
from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

# Hardcoded credentials
DB_USER = "postgres"
DB_PASS = "e"
DB_HOST = "34.95.172.190"
DB_PORT = "5432"
DB_NAME = "postgres"

# Construct URL
password_escaped = quote_plus(DB_PASS)
DATABASE_URL = f"postgresql://{DB_USER}:{password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def debug_clients():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            query = text("SELECT id, razon_social, activo, requiere_auditoria, contador_uso FROM clientes WHERE requiere_auditoria = TRUE AND contador_uso = 0")
            result = connection.execute(query)
            
            print("\n=== AUDITED CLIENTS WITH ZERO USAGE ===")
            found = False
            for row in result:
                found = True
                print(f"ID: {row.id}")
                print(f"Name: {row.razon_social}")
                print(f"Active: {row.activo}")
                print("-------------------")
            
            if not found:
                print("None found.")
            print("=======================================\n")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_clients()
