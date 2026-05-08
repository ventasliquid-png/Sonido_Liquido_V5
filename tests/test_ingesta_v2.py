# [IDENTIDAD] - tests/test_ingesta_v2.py
# Versión: V5.6 GOLD | Sincronización: 20260508194400
# ------------------------------------------
import sys
import os
import uuid
from datetime import datetime

# Agregar raíz al path antes de los imports del sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal

# [V14.12 GOLD] Mapeo Universal (Crítico para SQLAlchemy)
import backend.auth.models
import backend.maestros.models
import backend.logistica.models
import backend.contactos.models
import backend.clientes.models
import backend.productos.models
import backend.pedidos.models
import backend.proveedores.models
import backend.agenda.models
import backend.remitos.models
import backend.facturacion.models
import backend.ingesta.models
from sqlalchemy.orm import configure_mappers
try:
    configure_mappers()
except:
    pass

from backend.ingesta.service import IngestaService
from backend.ingesta.models import FacturasRaw, FacturasProcesadas
from backend.facturacion.models import Factura

def test_flow():
    db = SessionLocal()
    try:
        print("========================================================")
        print("   TEST INGESTA V2 - VERIFICACIÓN DE BUGS (SESION 800)")
        print("========================================================")
        
        # 1. Mock PDF Bytes (Básico para no romper el parser)
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        filename = "test_bug_fix.pdf"
        
        # 2. Store Raw
        print("[*] Paso 1: Almacenando Raw...")
        try:
            # Factura con punto de venta 00001 y secuencial 00002536
            raw = FacturasRaw(
                id=uuid.uuid4(),
                filename=filename, 
                pdf_bytes=dummy_pdf, 
                audit_status="RECIBIDO",
                parsed_data_raw={
                    "cliente": {"cuit": "20300000001", "razon_social": "TEST CLIENT V2"},
                    "factura": {"numero": "00001-00002536", "cae": "12345678901234", "vto_cae": "01/01/2027"},
                    "items": [{"descripcion": "ITEM TEST V2", "cantidad": 1, "precio_unitario": 100.0, "subtotal": 100.0}]
                }
            )
            db.add(raw)
            db.commit()
            db.refresh(raw)
            print(f" [OK] Raw ID: {raw.id}")
        except Exception as e:
            print(f" [X] Error en Paso 1: {e}")
            return
        
        # 3. Preview
        print("[*] Paso 2: Preview (Conserje V2)...")
        prev = IngestaService.preview(db, raw.id)
        print(f" [OK] Confianza Conserje: {prev['audit_log']['confidence']}%")
        
        # 4. Approve (Mirror Mode)
        print("[*] Paso 3: Approve (Impacto Bit 22)...")
        from backend.pedidos.models import Pedido
        pedido = db.query(Pedido).first()
        if not pedido:
            print(" [!] No hay pedidos en DB para vincular. Creando uno temporal...")
            from backend.clientes.models import Cliente
            cliente = db.query(Cliente).first()
            pedido = Pedido(cliente_id=cliente.id, estado="PENDIENTE", fecha=datetime.now())
            db.add(pedido)
            db.flush()

        edited_data = {
            "cliente": {"id": str(pedido.cliente_id), "cuit": "20300000001", "razon_social": "TEST CLIENT V2"},
            "factura": {"numero": "00001-00002536", "cae": "12345678901234", "vto_cae": "01/01/2027"},
            "items": [
                {"descripcion": "ITEM TEST V2", "cantidad": 1, "precio_unitario": 100.0, "subtotal": 100.0}
            ],
            "pedido_id_vinculado": pedido.id,
            "modo_ingesta": "VINCULAR_EXISTENTE",
            "valor_declarado": 121.0,
            "transporte_id": str(pedido.transporte_id) if pedido.transporte_id else None
        }
        
        res = IngestaService.approve(db, raw.id, edited_data)
        print(f" [OK] Procesada ID: {res['id']}")
        print(f" [OK] Remito ID: {res['remito_id']}")
        
        # 5. Verificación de BUGS
        # BUG 1: Numero Legal del Remito
        from backend.remitos.models import Remito
        remito = db.query(Remito).filter(Remito.id == res['remito_id']).first()
        if remito:
            print(f" [BUG 1] Remito Numero Legal: {remito.numero_legal}")
            if remito.numero_legal == "0016-00002536":
                print(" [GOLD] BUG 1 VALIDADO: El remito hereda el secuencial tal cual.")
            else:
                print(f" [X] BUG 1 FALLIDO: Obtenido {remito.numero_legal}, esperaba 0016-00002536")

        # BUG 2: Factura Vinculada (Propiedad numero_completo)
        # Buscamos la factura recién creada (vínculo real)
        from backend.facturacion.models import FacturaRemito
        vinculo = db.query(FacturaRemito).filter(FacturaRemito.remito_id == res['remito_id']).first()
        if vinculo:
            factura = vinculo.factura
            print(f" [BUG 2] Factura Numero Completo: {factura.numero_completo}")
            if factura.numero_completo == "0001-00002536":
                print(" [GOLD] BUG 2 VALIDADO: Propiedad numero_completo correcta.")
            else:
                print(f" [X] BUG 2 FALLIDO: Obtenido {factura.numero_completo}, esperaba 0001-00002536")

    except Exception as e:
        print(f" [CRITICAL ERROR]: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("========================================================")

if __name__ == "__main__":
    test_flow()
