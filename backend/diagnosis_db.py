
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.maestros.models import Vendedor

def diagnose():
    db = SessionLocal()
    try:
        print("Checking DB connection...")
        clients = db.query(Cliente).limit(1).all()
        print(f"Clients OK: {len(clients)}")
        
        vendedores = db.query(Vendedor).limit(1).all()
        print(f"Vendedores OK: {len(vendedores)}")
        
        print("DIAGNOSIS SUCCESSFUL")
    except Exception as e:
        print(f"DIAGNOSIS FAILED: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
