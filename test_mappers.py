import sys
import os

# Insert backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.database import Base, engine
from sqlalchemy.orm import configure_mappers
import backend.auth.models as auth_models 
import backend.maestros.models as maestros_models
import backend.logistica.models as logistica_models
import backend.contactos.models as contactos_models 
import backend.clientes.models as clientes_models 
import backend.productos.models as productos_models
import backend.pedidos.models as pedidos_models 
import backend.proveedores.models as proveedores_models
import backend.agenda.models as agenda_models
import backend.remitos.models as remitos_models 
import backend.core.models as core_models 

try:
    configure_mappers()
    print("Mappers OK")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("EXACT ERROR:", repr(e))
