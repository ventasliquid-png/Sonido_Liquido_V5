import sys
import os

# Add root to credentials
sys.path.append(os.getcwd())

from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import configure_mappers
try:
    from backend.core.database import Base, engine
except ImportError:
    from backend.database import Base, engine

# Import models to register them
from backend.clientes.models import Domicilio
from backend.maestros.models import Provincia
from backend.auth.models import Usuario
from backend.pedidos.models import Pedido
from backend.contactos.models import Vinculo
from backend.logistica.models import NodoTransporte, EmpresaTransporte
# Import other models if necessary to trigger the whole graph
from backend.productos.models import Producto

try:
    print("🔵 Attempting to configure mappers...")
    configure_mappers()
    print("✅ Mappers configured successfully!")
except Exception as e:
    print(f"❌ Mapper Configuration Failed: {e}")
    import traceback
    traceback.print_exc()
