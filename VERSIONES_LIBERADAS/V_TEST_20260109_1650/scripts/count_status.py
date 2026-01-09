
import sys
import os

# Add root to python path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.pedidos.models import Pedido
from backend.clientes.models import Cliente
from backend.productos.models import Producto

try:
    db = SessionLocal()
    c_pedidos = db.query(Pedido).count()
    c_clientes = db.query(Cliente).count()
    c_productos = db.query(Producto).count()
    
    print(f"PEDIDOS: {c_pedidos}")
    print(f"CLIENTES: {c_clientes}")
    print(f"PRODUCTOS: {c_productos}")
except Exception as e:
    print(f"ERROR: {e}")
