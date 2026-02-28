import sys
import os
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('C:\\dev\\Sonido_Liquido_V5')
os.environ["DATABASE_URL"] = "sqlite:///C:\\dev\\Sonido_Liquido_V5\\pilot_v5x.db"

from backend.core.database import SessionLocal
from backend.remitos.service import RemitosService
from backend.remitos.schemas import IngestionPayload, IngestionCliente, IngestionFactura, IngestionItem

def main():
    db = SessionLocal()
    try:
        # Simulate payload
        from backend.remitos import schemas
        payload = schemas.IngestionPayload(
            cliente=schemas.IngestionCliente(cuit="30-71084734-3", razon_social="L EPI S.R.L."),
            factura=schemas.IngestionFactura(numero="S/N", cae="86084584082811", vto_cae="02/03/2026"),
            items=[schemas.IngestionItem(descripcion="Alcohol 70% bidon por 5 Lts", cantidad=4.0, precio_unitario=0.0)]
        )
        print("Tratando de crear remito en BD...")
        remito = RemitosService.create_from_ingestion(db, payload)
        print(f"Éxito: Remito {remito.id} creado.")
        db.rollback()
    except Exception as e:
        print("❌ CAPTURADO ERROR 500 LOG:")
        traceback.print_exc()
        db.rollback()

if __name__ == "__main__":
    main()
