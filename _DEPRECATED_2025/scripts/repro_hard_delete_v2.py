
import os
import sys
import uuid
# Add current directory to sys.path for backend imports
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, Base
from backend.auth.models import Usuario
from backend.clientes.models import Cliente, Domicilio
from backend.agenda.models import VinculoComercial, Persona
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Provincia, TipoContacto
from backend.pedidos.models import Pedido, PedidoItem
from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.productos.models import Producto
from backend.proveedores.models import Proveedor
from backend.clientes.service import ClienteService
from sqlalchemy.orm import Session

def simulate_hard_delete():
    db: Session = SessionLocal()
    try:
        # Create a test client
        test_id = uuid.uuid4()
        print(f"--- SIMULACION DE BAJA FISICA ---")
        print(f"Creando cliente de prueba con ID: {test_id}")
        
        test_client = Cliente(
            id=test_id,
            razon_social="CLIENTE PRUEBA ELIMINACION",
            cuit="99999999999",
            activo=False
        )
        db.add(test_client)
        db.commit()
        
        # Add a domicilio
        dom = Domicilio(cliente_id=test_id, calle="Calle Falsa", numero="123", es_fiscal=True)
        db.add(dom)
        
        # Add a vinculation (contact)
        persona = Persona(nombre_completo="Juan Perez Repro")
        db.add(persona)
        db.commit()
        db.refresh(persona)
        
        vinculo = VinculoComercial(cliente_id=test_id, persona_id=persona.id, tipo_contacto_id="VENTAS")
        db.add(vinculo)
        db.commit()
        
        print("Cliente y relaciones creadas con éxito.")
        
        # Now try to hard delete
        print(f"Intentando eliminar cliente ID: {test_id}")
        deleted = ClienteService.hard_delete_cliente(db, test_id)
        if deleted:
            print("✅ ELIMINACION EXITOSA")
        else:
            print("❌ CLIENTE NO ENCONTRADO")
            
    except Exception as e:
        print(f"🔥 ERROR DURANTE LA ELIMINACION: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_hard_delete()
