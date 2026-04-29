import sys
import os
from datetime import datetime

# Add backend to path (Production) - Insert at 0 to override development folder
sys.path.insert(0, 'C:/dev/V5-LS/current')

# Set database URL to production explicitly
os.environ['DATABASE_URL'] = 'sqlite:///C:/dev/V5-LS/data/V5_LS_MASTER.db'

from backend.core.database import SessionLocal
from backend.remitos.service import RemitosService
from backend.remitos.schemas import IngestionPayload, IngestionCliente, IngestionFactura, IngestionItem

# Import all models to satisfy SQLAlchemy relationships
from backend.logistica.models import EmpresaTransporte
from backend.pedidos.models import Pedido, PedidoItem
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro
from backend.contactos.models import VinculoGeografico
from backend.maestros.models import CondicionIva, Provincia, ListaPrecios, Segmento, Vendedor, TasaIVA, Unidad
from backend.remitos.models import Remito, RemitoItem

def test_ingestion():
    db = SessionLocal()
    try:
        # Check Client Info
        cliente = db.query(Cliente).get("2fbeb6eb-ffc6-49ff-81d1-e324f410eed6")
        print(f"Cliente: {cliente.razon_social}")
        print(f"Condicion IVA ID: {cliente.condicion_iva_id}")
        if cliente.condicion_iva_id:
            cond = db.query(CondicionIva).get(cliente.condicion_iva_id)
            print(f"Condicion IVA Nombre: {cond.nombre}")

        # Factura 2531 Data (Extracted from pdf_debug.txt)
        payload = IngestionPayload(
            cliente=IngestionCliente(
                id="2fbeb6eb-ffc6-49ff-81d1-e324f410eed6",
                cuit="30699349603",
                razon_social="GELATO SA"
            ),
            factura=IngestionFactura(
                numero="00001-00002531-V2", 
                cae="86173197020623",
                vto_cae="07/05/2026"
            ),
            items=[
                IngestionItem(
                    descripcion="COFIAS",
                    cantidad=2000.0,
                    precio_unitario_neto=41.0,
                    alicuota_iva=21.0
                )
            ],
            bultos=10,
            valor_declarado=99220.0,
            modo_ingesta="NUEVO"
        )

        print("\n--- INICIANDO TEST DE INGESTA FACTURA 2531 ---")
        remito = RemitosService.create_from_ingestion(db, payload)
        
        print("\n--- RESULTADO DE LA OPERACIÓN ---")
        print(f"Remito ID: {remito.id}")
        print(f"Remito Número Legal: {remito.numero_legal}")
        print(f"Pedido Asociado ID: {remito.pedido_id}")
        
        # Verify Items
        print(f"Items en el Remito: {len(remito.items)}")
        for item in remito.items:
            print(f"  - Item ID: {item.id}, PedidoItem ID: {item.pedido_item_id}, Cantidad: {item.cantidad}")
            p_item = db.query(PedidoItem).get(item.pedido_item_id)
            print(f"    - Precio Unitario: {p_item.precio_unitario}")
            print(f"    - Subtotal: {p_item.subtotal}")
            print(f"    - Pertenencia Pedido: {p_item.pedido_id} (Debería ser {remito.pedido_id})")

        # Verify Totals
        pedido = db.query(Pedido).get(remito.pedido_id)
        print(f"Total Pedido: ${pedido.total} (Esperado: $99220.0)")

        print("\n--- TEST FINALIZADO ---")

    except Exception as e:
        print(f"\n!!! ERROR DURANTE EL TEST !!!\n{str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ingestion()
