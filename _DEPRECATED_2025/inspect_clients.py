
import sys
import os
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.clientes.service import ClienteService
from backend.clientes.schemas import ClienteListResponse
from backend.auth.models import Usuario # Needed for relationship resolution
from backend.pedidos.models import Pedido # Needed for relationship resolution
from backend.logistica.models import NodoTransporte, EmpresaTransporte # Needed for relationship resolution
from backend.productos.models import Producto # Needed for PedidoItem resolution

def debug_clients():
    db = SessionLocal()
    try:
        print("Fetching clients from DB...")
        clients = ClienteService.get_clientes(db, limit=5)
        print(f"Fetched {len(clients)} raw objects.")
        
        print("Attempting validation/serialization...")
        for i, c in enumerate(clients):
            print(f"[{i}] {c.razon_social} (ID: {c.id})")
            # Try to convert to Pydantic
            try:
                dto = ClienteListResponse.model_validate(c)
                print("   -> Validated OK")
            except Exception as e:
                print(f"   -> VALIDATION ERROR: {e}")
                import traceback
                traceback.print_exc()
                break
                
    except Exception as e:
        print(f"Service Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_clients()
