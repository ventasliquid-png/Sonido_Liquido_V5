import sys
import os
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.productos.models import Producto

def inspect_products():
    print("--- INSPECCION DE PRODUCTOS (LOCAL SQLITE) ---")
    
    # 1. Connect to DB
    db_path = "sqlite:///pilot.db"
    if not os.path.exists("pilot.db"):
        print("ALERT: pilot.db file does not exist in current directory!")
    else:
        print(f"pilot.db exists. Size: {os.path.getsize('pilot.db')} bytes.")

    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Raw SQL check first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM productos"))
            count = result.scalar()
            print(f"Total rows in 'productos' table (Raw SQL): {count}")

        # ORM Check
        products = session.execute(select(Producto)).scalars().all()
        print(f"Total products (ORM): {len(products)}")
        
        print("\n--- SAMPLE PRODUCTS (SKU | Cod.Visual | Nombre) ---")
        for p in products[:20]:
            print(f"SKU: {p.sku} | Visual: {p.codigo_visual} | {p.nombre}")

    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    inspect_products()
