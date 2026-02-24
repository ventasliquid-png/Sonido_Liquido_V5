import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from database import SessionLocal
from remitos.service import RemitosService
from remitos import schemas

try:
    db = SessionLocal()
    print("Database connected")
    
    # Simulate the payload from frontend
    payload = schemas.IngestionPayload(
        cliente=schemas.IngestionCliente(
            cuit="20295915863", # Test CUIT
            razon_social="FERNANDEZ AGUSTIN TEST"
        ),
        factura=schemas.IngestionFactura(
            numero="0001-00000001",
            cae="1234567890",
            vto_cae="01/01/2026"
        ),
        items=[
            schemas.IngestionItem(
                descripcion="ITEM DEBUG",
                cantidad=1.0,
                precio_unitario=0.0,
                codigo="DEBUG-01"
            )
        ]
    )
    
    print("Payload prepared")
    print(f"Payload: {payload.dict()}")
    
    remito = RemitosService.create_from_ingestion(db, payload)
    print(f"SUCCESS: Remito created with ID {remito.id} and PDF URL {remito.pdf_url}")
    
except ValueError as ve:
    print(f"EXPECTED VALUE ERROR: {ve}")
except Exception as e:
    import traceback
    print("CRITICAL EXCEPTION:")
    traceback.print_exc()
finally:
    db.close()
