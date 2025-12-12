import sys
import os
from sqlalchemy import text

# Add root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine, Base
# Import all models to ensure registry is populated
from backend.clientes.models import Cliente
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem

def check_and_fix():
    print("--- Checking DB and Schema ---")
    
    # 1. Drop Pedidos tables to ensure fresh schema with UUID
    try:
        with engine.connect() as conn:
            print("Dropping 'pedidos_items' and 'pedidos' to force schema update...")
            conn.execute(text("DROP TABLE IF EXISTS pedidos_items CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS pedidos CASCADE"))
            conn.commit()
            print("Tables dropped.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # 2. Re-create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # 3. Check Counts
    db = SessionLocal()
    try:
        c_count = db.query(Cliente).count()
        p_count = db.query(Producto).count()
        print(f"CLIENTES_COUNT: {c_count}")
        print(f"PRODUCTOS_COUNT: {p_count}")
        
        if c_count == 0 or p_count == 0:
            print("WARNING: Master data is empty!")
            
    except Exception as e:
        print(f"ERROR querying data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix()
