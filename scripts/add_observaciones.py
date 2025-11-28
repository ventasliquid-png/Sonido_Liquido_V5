from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

def get_database_url():
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
                result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clientes' AND column_name='observaciones'"))
                if result.fetchone():
                    print("Column 'observaciones' already exists.")
                    return
            except Exception as e:
                print(f"Check failed: {e}")

            print("Adding column 'observaciones'...")
            connection.execute(text("ALTER TABLE clientes ADD COLUMN observaciones TEXT"))
            connection.commit()
            print("Column added successfully.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
