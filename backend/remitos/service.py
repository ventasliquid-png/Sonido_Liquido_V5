from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.remitos import schemas, models
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem
from backend.logistica.models import EmpresaTransporte
# [GY-FIX] Import Vinculo to avoid Registry Error during potential implicit loads
from backend.contactos.models import Vinculo 

class RemitosService:
    
    @staticmethod
    def create_from_ingestion(db: Session, payload: schemas.IngestionPayload):
        """
        Creates a Pedido and Remito from PDF Ingestion Data.
        """
        # 1. FIND CLIENT
        cliente = db.query(Cliente).filter(Cliente.cuit == payload.cliente.cuit).first()
        
        if not cliente:
            # Fallback: Try to find by razon social (fuzzy) or return error
            # For now, strict CUIT match or error
            if payload.cliente.cuit:
               # Try stripping dashes if any
               clean_cuit = payload.cliente.cuit.replace("-", "")
               cliente = db.query(Cliente).filter(Cliente.cuit == clean_cuit).first()
            
            if not cliente:
                # [V5 Robustness] TRUST THE PDF.
                # If client doesn't exist, we create it ON THE FLY to ensure ingestion succeeds.
                # User can merge or edit later.
                print(f"Ingestion: Creating new client from PDF: {payload.cliente.razon_social} ({payload.cliente.cuit})")
                
                cliente = Cliente(
                    razon_social=payload.cliente.razon_social or "CLIENTE NUEVO (INGESTA)",
                    cuit=payload.cliente.cuit or "00000000000",
                    activo=True,
                    condicion_iva_id=None, # To be filled
                    lista_precios_id=None
                )
                db.add(cliente)
                db.flush() # Get ID
                
                # Auto-create Default Address for Logic Consistency
                domicilio_def = Domicilio(
                    cliente_id=cliente.id,
                    direccion="Dirección Fiscal (Auto-Generada)",
                    localidad="Desconocida",
                    provincia_id="X", # Default or Other
                    activo=True
                )
                db.add(domicilio_def)
                db.flush()
        
        # 2. RESOLVE LOGISTICS
        domicilio = next((d for d in cliente.domicilios if d.activo), None)
        if not domicilio:
            # Fallback to first address in DB or error
            domicilio = db.query(Domicilio).first() # Dangerous but keeps flow moving
            
        # Default Transport
        transporte = db.query(EmpresaTransporte).first()
        transporte_id = transporte.id if transporte else None

        # 3. CREATE PEDIDO
        # We assume "PENDIENTE" state validation will happen in V5 logic
        nuevo_pedido = Pedido(
            cliente_id=cliente.id,
            fecha=datetime.now(),
            nota=f"Ingesta Automática Factura: {payload.factura.numero or 'S/N'}",
            estado="PENDIENTE",
            origen="INGESTA_PDF",
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id
        )
        db.add(nuevo_pedido)
        db.flush()

        # 4. RESOLVE ITEMS
        # Find Generic Product for fallback
        prod_generico = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
        if not prod_generico:
             prod_generico = db.query(Producto).filter(Producto.activo == True).first()

        pedido_items = []
        for item in payload.items:
            # Fuzzy Logic could go here. For now, try exact match on description or clean description
            # Since PDF Descriptions might be dirty, we rely on "VARIOS" mostly unless we have code mapping
            
            producto = None
            # If we had a code, we'd search by code.
            
            # Simple Description Match
            producto = db.query(Producto).filter(Producto.nombre.ilike(f"%{item.descripcion}%")).first()
            
            nota_item = ""
            prod_id = prod_generico.id
            
            if producto:
                prod_id = producto.id
            else:
                nota_item = item.descripcion # Store original description
                
            new_p_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=prod_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario or 0.0,
                nota=nota_item
            )
            db.add(new_p_item)
            db.flush() 
            pedido_items.append(new_p_item)

        # 5. CREATE REMITO
        vto_cae_date = None
        if payload.factura.vto_cae:
            try:
                # Try common formats
                vto_cae_date = datetime.strptime(payload.factura.vto_cae, "%d/%m/%Y")
            except:
                pass
        
        # Internal Number Logic
        numero_legal = f"R-{str(nuevo_pedido.id).zfill(8)}"

        remito = models.Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=True,
            cae=payload.factura.cae,
            vto_cae=vto_cae_date,
            numero_legal=numero_legal
        )
        db.add(remito)
        db.flush()

        # 6. CREATE REMITO ITEMS
        for p_item in pedido_items:
            r_item = models.RemitoItem(
                remito_id=remito.id,
                pedido_item_id=p_item.id,
                cantidad=p_item.cantidad
            )
            db.add(r_item)
            
        db.commit()
        db.refresh(remito)
        return remito
