
import sys
import os
from datetime import datetime

# Force Local SQLite before importing database
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pilot_db_path = os.path.abspath(os.path.join(project_root, "pilot_v5x.db"))
os.environ["DATABASE_URL"] = f"sqlite:///{pilot_db_path}"

# Add backend to path
sys.path.append(project_root)

from backend.core.database import SessionLocal
from backend.remitos.service import RemitosService
from backend.remitos import schemas
from backend.clientes.models import Cliente

def test_manual_remito():
    db = SessionLocal()
    try:
        # 1. Find a test client
        cliente = db.query(Cliente).first()
        if not cliente:
            print("No clients found to test.")
            return

        print(f"Testing with client: {cliente.razon_social}")

        # 2. Create Manual Remito Payload
        payload = schemas.ManualRemitoPayload(
            cliente_id=str(cliente.id),
            items=[
                schemas.ManualRemitoItem(descripcion="ITEM PRUEBA 1", cantidad=5),
                schemas.ManualRemitoItem(descripcion="ITEM PRUEBA 2", cantidad=10)
            ],
            observaciones="TEST SISTEMA MANUAL 0015",
            domicilio_entrega_id=None,
            transporte_id=None,
            bultos=2,
            valor_declarado=1500.0
        )

        # 3. Execute Service
        print("Creating remito 1...")
        remito1 = RemitosService.create_manual(db, payload)
        print(f"Remito 1 Number: {remito1.numero_legal}")
        if remito1.numero_legal != "0015-00003001":
             print(f"ERROR: Expected 0015-00003001 but got {remito1.numero_legal}")

        print("Creating remito 2...")
        remito2 = RemitosService.create_manual(db, payload)
        print(f"Remito 2 Number: {remito2.numero_legal}")
        if remito2.numero_legal != "0015-00003002":
             print(f"ERROR: Expected 0015-00003002 but got {remito2.numero_legal}")

        if remito1.numero_legal == "0015-00003001" and remito2.numero_legal == "0015-00003002":
             print("Verification SUCCESS: Numbering sequence 0015-3001, 3002 works.")
        
        # 4. Check Persistence of new fields
        print(f"Checking persistence for Remito 1: Bultos={remito1.bultos}, Valor={remito1.valor_declarado}")
        if remito1.bultos == 2 and remito1.valor_declarado == 1500.0:
             print("Verification SUCCESS: Bultos and Valor Declarado persisted correctly.")
        else:
             print(f"ERROR: Persistence failed. Bultos:{remito1.bultos}, Valor:{remito1.valor_declarado}")
        
        # Cleanup
        # (Don't cleanup yet so we can see them in the DB if needed)
        # db.delete(remito1)
        # db.delete(remito2)
        # db.commit()
        # print("Cleanup done.")

    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_manual_remito()
