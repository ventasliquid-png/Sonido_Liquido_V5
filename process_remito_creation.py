import sys
import os
import traceback
from datetime import datetime

# Force project root
sys.path.append(os.getcwd())

print("--- REMITO CREATION PROTOTYPE ---")

from dotenv import load_dotenv
load_dotenv(".env")
os.environ["DATABASE_URL"] = "sqlite:///./pilot.db" # [GY-FIX] Force Local SQLite

from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.contactos.models import Vinculo # [GY-FIX] Import Vinculo for Registry
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem
from backend.remitos.models import Remito, RemitoItem
from backend.logistica.models import EmpresaTransporte

# MOCK DATA from Ingestion
INGESTION_DATA = {
    "cliente": {
        "cuit": "30715603973", # LAVIMAR (Existing)
        "razon_social": "LAVIMAR S.A."
    },
    "factura": {
        "numero": "0001-00002489",
        "cae": "12345678901234",
        "vto_cae": "01/03/2026"
    },
    "items": [
        {"descripcion": "Surgibac - Detergente", "cantidad": 5.0},
        {"descripcion": "Item No Reconocido", "cantidad": 2.0}
    ]
}

def run_process():
    db = SessionLocal()
    try:
        # 1. FIND CLIENT
        print(f"Searching Client CUIT: {INGESTION_DATA['cliente']['cuit']}...")
        cliente = db.query(Cliente).filter(Cliente.cuit == INGESTION_DATA['cliente']['cuit']).first()
        
        if not cliente:
            print("Client NOT FOUND. Aborting (In real app, maybe create or error).")
            # For prototype, we might pick the first client
            cliente = db.query(Cliente).first()
            print(f"Fallback to Client: {cliente.razon_social}")
            
        print(f"Client: {cliente.razon_social} (ID: {cliente.id})")
        
        # 2. RESOLVE LOGISTICS (Address & Transport)
        domicilio = next((d for d in cliente.domicilios if d.activo), None)
        if not domicilio:
            print("Client has NO address. Aborting.")
            return

        # Default Transport (Or default from system)
        transporte = db.query(EmpresaTransporte).first()
        transporte_id = transporte.id if transporte else None

        # 3. CREATE PEDIDO
        print("Creating Pedido...")
        nuevo_pedido = Pedido(
            cliente_id=cliente.id,
            fecha=datetime.now(),
            nota=f"Ingesta Automática Factura: {INGESTION_DATA['factura']['numero']}",
            estado="PENDIENTE", # Or CUMPLIDO?
            origen="INGESTA_PDF",
            domicilio_entrega_id=domicilio.id,
            transporte_id=transporte_id
        )
        db.add(nuevo_pedido)
        db.flush()
        print(f"Pedido Created ID: {nuevo_pedido.id}")

        # 4. RESOLVE ITEMS (Product Matching)
        # Find Generic Product
        prod_generico = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
        if not prod_generico:
            prod_generico = db.query(Producto).filter(Producto.activo == True).first()
            print(f"Warn: 'VARIOS' not found. Using fallback: {prod_generico.nombre}")

        # Process Items
        pedido_items = []
        for item in INGESTION_DATA['items']:
            # Fuzzy match attempt (mocked here)
            producto = db.query(Producto).filter(Producto.nombre.ilike(f"%{item['descripcion']}%")).first()
            
            nota_item = ""
            if producto:
                print(f"Matched Product: {item['descripcion']} -> {producto.nombre}")
                prod_id = producto.id
            else:
                print(f"Unmatched Item: {item['descripcion']} -> Using Generic")
                prod_id = prod_generico.id
                nota_item = item['descripcion'] # Store original desc

            new_p_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=prod_id,
                cantidad=item['cantidad'],
                precio_unitario=0.0, # Unknown from PDF usually, or we parse it
                nota=nota_item
            )
            db.add(new_p_item)
            db.flush() # Need ID for RemitoItem
            pedido_items.append(new_p_item)

        # 5. CREATE REMITO
        print("Creating Remito...")
        
        # Parse Dates
        vto_cae_date = None
        try:
            vto_cae_date = datetime.strptime(INGESTION_DATA['factura']['vto_cae'], "%d/%m/%Y")
        except:
            pass

        remito = Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=domicilio.id,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=True,
            cae=INGESTION_DATA['factura']['cae'],
            vto_cae=vto_cae_date,
            numero_legal=f"R-{str(nuevo_pedido.id).zfill(8)}" # Mock Internal Number
        )
        db.add(remito)
        db.flush()
        print(f"Remito Created ID: {remito.id}")

        # 6. CREATE REMITO ITEMS
        for p_item in pedido_items:
            r_item = RemitoItem(
                remito_id=remito.id,
                pedido_item_id=p_item.id,
                cantidad=p_item.cantidad
            )
            db.add(r_item)

        db.commit()
        print("--- SUCCESS: TRANSACTION COMMITTED ---")
        print(f"Returning Remito ID: {remito.id}")

    except Exception:
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_process()
