import sys
import os
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from backend.clientes.service import ClienteService
from backend.clientes.models import Cliente

# Hardcoded credentials
DB_USER = "postgres"
DB_PASS = "e"
DB_HOST = "34.95.172.190"
DB_PORT = "5432"
DB_NAME = "postgres"

# Construct URL
password_escaped = quote_plus(DB_PASS)
DATABASE_URL = f"postgresql://{DB_USER}:{password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_increment():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Find the client
        client = db.query(Cliente).filter(Cliente.razon_social.ilike('%Odontologia%')).first()
        if not client:
            print("Client not found.")
            return

        print(f"Client: {client.razon_social} (ID: {client.id})")
        print(f"Initial Count: {client.contador_uso}")
        
        # Increment
        print("Incrementing...")
        ClienteService.increment_usage(db, client.id)
        
        # Refresh
        db.refresh(client)
        print(f"New Count: {client.contador_uso}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_increment()
