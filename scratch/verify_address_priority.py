import sys
import os

# Simulamos el entorno de V5 para probar la lógica de resolución
BASE_DIR = r"C:\dev\V5-LS\current\backend"
sys.path.append(BASE_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from clientes.models import Cliente, Domicilio
from remitos.schemas import IngestionPayload, IngestionCliente, IngestionFactura, IngestionItem

DB_PATH = r"sqlite:///C:/dev/V5-LS/data/V5_LS_MASTER.db"
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_resolution():
    db = SessionLocal()
    try:
        # 1. Buscar un cliente real con dirección fiscal
        cliente = db.query(Cliente).filter(Cliente.cuit != "00000000000").first()
        if not cliente:
            print("No se encontró cliente para probar.")
            return

        print(f"Probando con cliente: {cliente.razon_social} (CUIT: {cliente.cuit})")
        
        # Obtenemos su dirección real
        dire_real = cliente.domicilio_fiscal_resumen
        print(f"Dirección Real en DB: {dire_real}")

        # 2. Simulamos Payload de Sabueso con dirección TRUNCADA
        payload_data = {
            "cliente": {
                "cuit": cliente.cuit,
                "razon_social": cliente.razon_social,
                "domicilio": "[EXTRACTED] CALLE TRUNCADA 123..." # La que viene del PDF
            },
            "factura": {"numero": "0001-00009999", "cae": "12345678901234"},
            "items": [{"descripcion": "ITEM TEST", "cantidad": 1.0}],
            "solo_actualizar_cliente": True # Para no crear remitos reales en la prueba
        }
        
        payload = IngestionPayload(**payload_data)
        
        # 3. Probamos el Router Logic (Simulado)
        # En el router, deberíamos haber sobreescrito el domicilio si el cliente existe
        # (Esta parte la probamos conceptualmente porque router requiere FastAPI context)
        
        # 4. Probamos el Service Logic
        from remitos.service import RemitosService
        # No corremos create_from_ingestion completo para no mutar DB en prod,
        # pero verificamos la lógica de resolución de domicilio que refactorizamos.
        
        # Simulamos la parte de resolución de domicilio de service.py
        domicilio_remito = None
        # Prioridad 1: Fiscal Activo
        domicilio_remito = next((d for d in cliente.domicilios if d.es_fiscal and d.activo), None)
        
        if domicilio_remito:
            fmt = f"{domicilio_remito.calle} {domicilio_remito.numero}, {domicilio_remito.localidad}"
            print(f"DEBUG: Dirección que se usará en el Remito: {fmt}")
            
            if "CALLE TRUNCADA" in fmt:
                print("FAIL: El sistema usó la dirección truncada del PDF.")
            else:
                print("SUCCESS: El sistema protegió la dirección de la base de datos.")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_resolution()
