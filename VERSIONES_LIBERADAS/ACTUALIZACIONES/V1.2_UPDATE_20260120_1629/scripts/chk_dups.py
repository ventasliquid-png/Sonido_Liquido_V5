import sys
import os
sys.path.append(os.getcwd())
from backend.core.database import SessionLocal
import backend.pedidos.models
import backend.clientes.models
import backend.agenda.models
import backend.logistica.models
import backend.maestros.models
import backend.auth.models
import backend.productos.models
from backend.pedidos.schemas import PedidoResponse

db = SessionLocal()

# Get Last Order
last_pedido = db.query(backend.pedidos.models.Pedido).order_by(backend.pedidos.models.Pedido.id.desc()).first()

if last_pedido:
    print(f"=== LAST PEDIDO ID: {last_pedido.id} ===")
    
    # Test Pydantic Serialization using the updated schema
    try:
        schema = PedidoResponse.model_validate(last_pedido)
        print("Pydantic Serialization: OK")
        if schema.cliente:
            print(f"Serialized Cliente CUIT: '{schema.cliente.cuit}'")
            print(f"Serialized Cliente Address: '{schema.cliente.domicilio_fiscal_resumen}'")
        else:
            print("Serialized Cliente is None!")
    except Exception as e:
        print(f"Pydantic Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No hay pedidos.")
