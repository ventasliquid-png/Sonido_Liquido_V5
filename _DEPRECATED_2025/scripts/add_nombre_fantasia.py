from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

def get_database_url():
    # Replicating logic from backend/core/database.py
    DEFAULT_PASSWORD = "e"
    user = os.environ.get("DB_USER", "postgres")
    host = os.environ.get("DB_HOST", "34.95.172.190")
    port = os.environ.get("DB_PORT", "5432")
    database = os.environ.get("DB_NAME", "postgres")
    
    password_escaped = quote_plus(DEFAULT_PASSWORD)
    return f"postgresql://{user}:{password_escaped}@{host}:{port}/{database}"

def add_column():
    url = get_database_url()
    print(f"Connecting to {url}...")
    engine = create_engine(url)
    
    try:
        with engine.connect() as connection:
            # Check if column exists
            try:
                # Postgres specific check
                result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clientes' AND column_name='nombre_fantasia'"))
                if result.fetchone():
                    print("Column 'nombre_fantasia' already exists.")
                    return
            except Exception as e:
                print(f"Check failed: {e}")

            print("Adding column 'nombre_fantasia'...")
            connection.execute(text("ALTER TABLE clientes ADD COLUMN nombre_fantasia VARCHAR"))
            connection.commit() # Important for some drivers
            print("Column added successfully.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
