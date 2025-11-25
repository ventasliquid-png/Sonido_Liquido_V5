import sqlalchemy
from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

# Hardcoded credentials from backend/core/database.py
DB_USER = "postgres"
DB_PASS = "e"
DB_HOST = "34.95.172.190"
DB_PORT = "5432"
DB_NAME = "postgres"

# Construct URL
password_escaped = quote_plus(DB_PASS)
DATABASE_URL = f"postgresql://{DB_USER}:{password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def add_column():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clientes' AND column_name='contador_uso'"))
            if result.fetchone():
                print("Column 'contador_uso' already exists.")
            else:
                print("Adding column 'contador_uso'...")
                connection.execute(text("ALTER TABLE clientes ADD COLUMN contador_uso INTEGER DEFAULT 0"))
                connection.commit()
                print("Column added successfully.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
