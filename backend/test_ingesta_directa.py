import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal
from backend.remitos import service, schemas
from uuid import UUID

db = SessionLocal()

payload = schemas.IngestionPayload(
    cliente=schemas.IngestionCliente(
        id="2fbeb6ebffc649ff81d1e324f410eed6",
        cuit="20182604071",
        razon_social="BIO-LAB S.A."
    ),
    factura=schemas.IngestionFactura(
        numero="00001-00002531-DIRECT-TEST",
        cae="12345678901234",
        vto_cae="31/12/2026"
    ),
    items=[
        schemas.IngestionItem(
            descripcion="Cofias Descartables Plisadas bca x 100",
            cantidad=2000.0,
            precio_unitario=41.0,
            alicuota_iva=21.0
        )
    ],
    transporte_id=None,
    bultos=1,
    valor_declarado=0.0
)


try:
    print("--- INICIANDO INGESTA DIRECTA ---")
    remito = service.RemitosService.create_from_ingestion(db, payload)
    print(f"Remito creado: {remito.id} - Pedido: {remito.pedido_id}")
    db.commit()
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
