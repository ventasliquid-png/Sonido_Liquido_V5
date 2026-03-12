import sys
import os

# Añadir el path del proyecto para importar los modelos
sys.path.append(os.getcwd())

from backend.core.database import engine, Base
# Importar todos los modelos necesarios para que SQLAlchemy resuelva las llaves foráneas
from backend.clientes.models import Cliente
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem

def tabula_rasa():
    print("🚀 Iniciando Protocolo TABULA RASA (Intento 2 - Resolución de FKs)...")
    
    # Intentamos crear solo las tablas que nos interesan, pero asegurando que los modelos están cargados
    try:
        # Drop en orden
        PedidoItem.__table__.drop(engine, checkfirst=True)
        Pedido.__table__.drop(engine, checkfirst=True)
        print("✅ Tablas viejas eliminadas.")
        
        # Create en orden
        Pedido.__table__.create(engine)
        PedidoItem.__table__.create(engine)
        print("✅ Tablas recreadas con éxito (Pedidos y PedidosItems).")
        print("✨ Schema sincronizado con precisión 4-decimal y descuentos.")
    except Exception as e:
        print(f"❌ Error durante la recreación: {e}")

if __name__ == "__main__":
    tabula_rasa()
