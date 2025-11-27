import sys
import os
from uuid import uuid4

# Add project root and backend to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.clientes.schemas import ClienteCreate, ClienteUpdate, DomicilioCreate
from backend.clientes.service import ClienteService
from backend.logistica.models import EmpresaTransporte

def reproduce():
    db = SessionLocal()
    try:
        print("--- Starting Reproduction Script ---")

        # 1. Create a Dummy Transport
        transporte = EmpresaTransporte(
            nombre=f"Transporte Test {uuid4().hex[:8]}",
            cuit="20123456789"
        )
        db.add(transporte)
        db.commit()
        db.refresh(transporte)
        print(f"Created Transport: {transporte.nombre} (ID: {transporte.id})")

        # 2. Create a Dummy Client
        cliente_in = ClienteCreate(
            razon_social=f"Cliente Test {uuid4().hex[:8]}",
            cuit="20111111112",
            domicilios=[
                DomicilioCreate(
                    calle="Calle Falsa 123",
                    localidad="Springfield",
                    es_fiscal=True,
                    es_entrega=True
                )
            ]
        )
        cliente = ClienteService.create_cliente(db, cliente_in)
        print(f"Created Cliente: {cliente.razon_social} (ID: {cliente.id})")
        
        # Verify initial state
        dom = cliente.domicilios[0]
        print(f"Initial Domicilio Transport ID: {dom.transporte_id}")

        # 3. Update Client with Transport
        print(f"Updating Cliente with Transport ID: {transporte.id}")
        update_data = ClienteUpdate(
            transporte_id=transporte.id
        )
        updated_cliente = ClienteService.update_cliente(db, cliente.id, update_data)
        
        # 4. Verify Update
        # Refresh from DB to be sure
        db.refresh(updated_cliente)
        # We need to refresh the domicile specifically or re-query
        dom_updated = db.query(Domicilio).filter(Domicilio.cliente_id == cliente.id).first()
        
        print(f"Updated Domicilio Transport ID: {dom_updated.transporte_id}")
        
        if dom_updated.transporte_id == transporte.id:
            print("✅ SUCCESS: Transport ID was saved correctly.")
        else:
            print("❌ FAILURE: Transport ID was NOT saved.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
