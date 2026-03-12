
import sys
import os
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
import backend.agenda.models # Fix ORM relationship
import backend.auth.models
import backend.logistica.models
import backend.maestros.models
from backend.clientes.models import Cliente
from backend.productos.models import Producto
from backend.pedidos.models import Pedido
from sqlalchemy import text

def count_iowa():
    print("--- [CONTEO DE TROPA - IOWA] ---")
    db = SessionLocal()
    try:
        # Verificar conexión
        db.execute(text("SELECT 1"))
        
        c_clientes = db.query(Cliente).count()
        c_productos = db.query(Producto).count()
        c_pedidos = db.query(Pedido).count()
        
        print(f"Clientes: {c_clientes}")
        print(f"Productos: {c_productos}")
        print(f"Pedidos: {c_pedidos}")
        
    except Exception as e:
        print(f"❌ Error conectando a IOWA: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    count_iowa()
