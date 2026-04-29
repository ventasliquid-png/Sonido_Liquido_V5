import sys
import os

# Add backend to path
sys.path.append('C:/dev/V5-LS/current')

# Set database URL to production explicitly
os.environ['DATABASE_URL'] = 'sqlite:///C:/dev/V5-LS/data/V5_LS_MASTER.db'

from backend.core.database import SessionLocal
# Import all models to satisfy SQLAlchemy relationships
from backend.logistica.models import EmpresaTransporte
from backend.pedidos.models import Pedido, PedidoItem
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro
from backend.contactos.models import VinculoGeografico
from backend.maestros.models import CondicionIva, Provincia, ListaPrecios, Segmento, Vendedor, TasaIVA, Unidad
from backend.remitos.models import Remito, RemitoItem

db = SessionLocal()
try:
    cliente = db.query(Cliente).filter(Cliente.cuit == '30699349603').first()
    if cliente:
        print(f"ID: {cliente.id}")
        print(f"Razon Social: {cliente.razon_social}")
    else:
        print("Cliente no encontrado")
finally:
    db.close()
