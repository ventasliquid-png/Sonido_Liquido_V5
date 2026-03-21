import sys
import os
from sqlalchemy.orm import Session
from uuid import uuid4

# Setup paths
sys.path.append(os.getcwd())
os.environ["DATABASE_URL"] = "sqlite:///c:/dev/Sonido_Liquido_V5/pilot_v5x.db"

from backend.core.database import SessionLocal
from backend.remitos.service import RemitosService
from backend.remitos import schemas, models
from backend.clientes.models import Cliente

def test_total_sovereignty():
    db = SessionLocal()
    try:
        # 1. Setup
        print("Setup: Initial Client and Manual Remito...")
        client1 = db.query(Cliente).first()
        payload = schemas.ManualRemitoPayload(
            cliente_id=str(client1.id),
            items=[{"descripcion": "Item 1", "cantidad": 10}],
            bultos=1,
            valor_declarado=100.0
        )
        remito = RemitosService.create_manual(db, payload)
        remito_id = str(remito.id)
        item_id = remito.items[0].id
        print(f"Created Remito {remito_id}")

        # 2. Update
        print("\nTesting Update...")
        client2 = db.query(Cliente).filter(Cliente.id != client1.id).first()
        client2_id = str(client2.id) if client2 else str(client1.id)
        
        update_payload = schemas.RemitoUpdate(
            cliente_id=client2_id,
            nuevo_domicilio=schemas.ForcedAddress(calle="Calle Falsa", localidad="Springfield"),
            items=[
                schemas.RemitoItemUpdate(id=item_id, cantidad=20, descripcion="Item 1 Mod"),
                schemas.RemitoItemUpdate(cantidad=5, descripcion="Item 2 New")
            ],
            bultos=9,
            valor_declarado=999.0
        )
        RemitosService.update_remito(db, remito_id, update_payload)
        
        # 3. Verify (Fresh Query)
        db.expire_all()
        check = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
        
        print(f"Bultos: {check.bultos} (Expected 9)")
        print(f"Valor: {check.valor_declarado} (Expected 999)")
        print(f"Client: {check.pedido.cliente_id} (Expected {client2_id})")
        print(f"Items: {len(check.items)} (Expected 2)")
        
        success = (check.bultos == 9 and 
                   check.valor_declarado == 999.0 and 
                   len(check.items) == 2 and
                   check.domicilio_entrega.calle == "Calle Falsa")
        
        if success:
            print("\nFINAL STATUS: SUCCESS")
        else:
            print("\nFINAL STATUS: FAILED (Assertion Mismatch)")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_total_sovereignty()
