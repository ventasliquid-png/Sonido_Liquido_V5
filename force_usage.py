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

def force_usage():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Set count to 100 for UBA Fc de Psicología
            query = text("UPDATE clientes SET contador_uso = 100 WHERE razon_social ILIKE '%Psicología%' AND requiere_auditoria = TRUE")
            result = connection.execute(query)
            connection.commit()
            print(f"Updated {result.rowcount} rows.")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    force_usage()
