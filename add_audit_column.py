import sqlalchemy
from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

# Hardcoded credentials from backend/core/database.py
DB_USER = "postgres"
DB_PASS = "e"
DB_HOST = "34.95.172.190"
DB_PORT = "5432"
DB_NAME = "postgres" # Defaulting to postgres as per database.py logic if path is empty, but let's try 'postgres' or check if there's a specific DB name. 
# database.py uses: database = parsed.path.lstrip("/") or "postgres"
# The error message showed: connection to server at "34.95.172.190", port 5432 failed: FATAL:  password authentication failed for user "postgres"
# This suggests the password 'e' might be correct but maybe the DB name is different? 
# The original script used 'sonido_liquido_v5'. 
# Let's try to connect to 'postgres' first as it's the default maintenance DB.

# Construct URL
password_escaped = quote_plus(DB_PASS)
DATABASE_URL = f"postgresql://{DB_USER}:{password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def add_column():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Check if column exists
            # Note: We need to check in the 'public' schema of the connected DB.
            # If the tables are in a specific DB 'sonido_liquido_v5', we must connect to THAT DB.
            # But database.py defaults to 'postgres'. Let's assume the tables are in 'postgres' DB for now based on the file content.
            
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clientes' AND column_name='requiere_auditoria'"))
            if result.fetchone():
                print("Column 'requiere_auditoria' already exists.")
            else:
                print("Adding column 'requiere_auditoria'...")
                connection.execute(text("ALTER TABLE clientes ADD COLUMN requiere_auditoria BOOLEAN DEFAULT FALSE"))
                connection.commit()
                print("Column added successfully.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
