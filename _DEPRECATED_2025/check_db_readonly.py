import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.productos.models import Producto

def check_counts():
    db = SessionLocal()
    try:
        c_count = db.query(Cliente).count()
        p_count = db.query(Producto).count()
        print(f"CLIENTES_COUNT: {c_count}")
        print(f"PRODUCTOS_COUNT: {p_count}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
