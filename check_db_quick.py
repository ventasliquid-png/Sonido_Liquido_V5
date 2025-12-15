
import sys
import os
from sqlalchemy import text

# Add root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine
# Correct Imports - LOAD EVERYTHING
from backend.auth.models import Usuario
from backend.maestros.models import Provincia, Localidad, CondicionIva, Segmento, Rubro, Unidad
from backend.agenda.models import VinculoComercial, Persona
from backend.logistica.models import EmpresaTransporte, Deposito
from backend.pedidos.models import Pedido, PedidoItem
from backend.clientes.models import Cliente
from backend.productos.models import Producto

def check_only():
    print(f"--- Checking DB: {engine.url} ---")
    
    db = SessionLocal()
    try:
        # Check connection
        db.execute(text("SELECT 1"))
        print("Connection: OK")

        # Counts
        try:
            c_count = db.query(Cliente).count()
            print(f"CLIENTES_COUNT: {c_count}")
        except Exception as e:
            print(f"Error querying Clientes: {e}")

        try:
            p_count = db.query(Producto).count()
            print(f"PRODUCTOS_COUNT: {p_count}")
        except Exception as e:
            print(f"Error querying Productos: {e}")
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_only()
