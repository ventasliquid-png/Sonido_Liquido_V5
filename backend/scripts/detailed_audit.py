import os
import sys

# Setup environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(BASE_DIR))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# FORCE SQLITE
os.environ["DATABASE_URL"] = "sqlite:///c:/dev/Sonido_Liquido_V5/pilot_v5x.db"

from backend.core.database import SessionLocal
# BOOT ALL MODELS for registry
from backend.auth import models as auth_models
from backend.maestros import models as maestros_models
from backend.logistica import models as logistica_models
from backend.agenda import models as agenda_models
from backend.contactos import models as contactos_models
from backend.productos import models as productos_models
from backend.clientes import models as clientes_models
from backend.pedidos import models as pedidos_models
from backend.proveedores import models as proveedores_models
from backend.remitos import models as remitos_models

from backend.clientes.models import Cliente
from backend.clientes.constants import ClientFlags

def detailed_audit():
    db = SessionLocal()
    try:
        print("--- AUDITORÍA DE SELLOS Y COLORES (V14) ---")
        clients = db.query(Cliente).all()
        
        for c in clients:
            f = c.flags_estado
            is_azul = bool(f & ClientFlags.MULTI_CUIT)
            is_rosa = bool(f & ClientFlags.OPERATOR_OK)
            is_blanco = bool((f & ClientFlags.EXISTENCE) and (f & ClientFlags.V14_STRUCT))
            no_cuit = not c.cuit or c.cuit in ["00000000000", ""]
            
            # Logic for Lilas/Rosa/Azul according to Carlos
            color = "BLANCO"
            if is_azul: color = "AZUL (Multi-Sede)"
            elif is_rosa: color = "ROSA (Validado)"
            elif no_cuit: color = "LILA (Sin CUIT)"
            
            sedes = len(c.domicilios)
            print(f"[{color}] {c.razon_social} | CUIT: {c.cuit} | Flags: {f} | Sedes: {sedes}")
            
    except Exception as e:
         print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    detailed_audit()
