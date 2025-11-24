import sys
import os
import uuid

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.maestros.models import CondicionIva, ListaPrecios
# import backend.agenda.models # Removed to isolate error

def debug_create_cliente():
    print("--- Debugging Create Cliente ---")
    db = SessionLocal()
    try:
        # Fetch FKs
        cond_iva = db.query(CondicionIva).first()
        lista_precio = db.query(ListaPrecios).first()
        
        if not cond_iva or not lista_precio:
            print("❌ Error: No hay condiciones de IVA o listas de precios.")
            return

        print(f"Using CondicionIva: {cond_iva.id}")
        print(f"Using ListaPrecios: {lista_precio.id}")

        # Create Cliente
        new_cliente = Cliente(
            razon_social="Debug Cliente Manual",
            cuit=f"20-{uuid.uuid4().int % 100000000}-9",
            condicion_iva_id=cond_iva.id,
            lista_precios_id=lista_precio.id,
            activo=True
        )
        
        print("Adding to session...")
        db.add(new_cliente)
        print("Committing...")
        db.commit()
        print("✅ Cliente created successfully!")
        db.refresh(new_cliente)
        print(f"ID: {new_cliente.id}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    debug_create_cliente()
