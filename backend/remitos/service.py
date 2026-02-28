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
        # [V5] Anti-Zombi: Verify if Remito already exists for this Invoice
        original_invoice = payload.factura.numero or ""
        numero_legal = ""
        if "-" in original_invoice:
            inv_body = original_invoice.split("-")[-1]
            numero_legal = f"0016-{inv_body}"
        
        if numero_legal:
            existing_remito = db.query(models.Remito).filter(models.Remito.numero_legal == numero_legal).first()
            if existing_remito:
                raise ValueError(f"Ya existe el Remito {numero_legal} asociado a esta Factura.")
            
        # 1. FIND CLIENT
        cliente = db.query(Cliente).filter(Cliente.cuit == payload.cliente.cuit).first()
        
        if not cliente:
            # [V5 Robustness] TRUST THE PDF.
            # If client doesn't exist, we create it ON THE FLY to ensure ingestion succeeds.
            # User can merge or edit later.
            print(f"Ingestion: Creating new client from PDF: {payload.cliente.razon_social} ({payload.cliente.cuit})")
            
            # [V14 GENOMA] Target Level 13: EXISTENCE (1) | GOLD_ARCA (4) | V14_STRUCT (8)
            from backend.clientes.constants import ClientFlags
            gold_flags = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT
            
            cliente = Cliente(
                razon_social=payload.cliente.razon_social or "CLIENTE NUEVO (INGESTA)",
                cuit=payload.cliente.cuit or "00000000000",
                activo=True,
                flags_estado=gold_flags,
                estado_arca='PENDIENTE_AUDITORIA',
                condicion_iva_id=None,
                lista_precios_id=None
            )
            db.add(cliente)
            db.flush() # Get ID
            
            # Auto-create Default Address for Logic Consistency
            domicilio_def = Domicilio(
                cliente_id=cliente.id,
                calle=payload.cliente.domicilio or "Dirección Fiscal (Auto-Generada)",
                localidad="Desconocida",
                provincia_id="X", 
                es_fiscal=True,
                activo=True
            )
            db.add(domicilio_def)
            db.flush()
        
        # 2. RESOLVE LOGISTICS
        domicilio = next((d for d in cliente.domicilios if d.activo), None)
        if not domicilio:
            # Fallback to first address in DB
            domicilio = db.query(Domicilio).filter(Domicilio.cliente_id == cliente.id).first()
            
        # Default Transport
        transporte = db.query(EmpresaTransporte).first()
        transporte_id = transporte.id if transporte else None

        # 3. CREATE PEDIDO
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
        from backend.productos.models import Producto, Rubro
        prod_generico = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
        if not prod_generico:
             prod_generico = db.query(Producto).filter(Producto.activo == True).first()
             
        # [GY-FIX] Prevenir Error 500 por base de datos vacía (0 SKUs)
        if not prod_generico:
             rubro = db.query(Rubro).first()
             if not rubro:
                 rubro = Rubro(codigo="GEN", nombre="Genérico Automático")
                 db.add(rubro)
                 db.flush()
             prod_generico = Producto(nombre="ÍTEM VARIOS (Auto-Ingesta)", sku=999999, codigo_visual="VAR-001", rubro_id=rubro.id, activo=True)
             db.add(prod_generico)
             db.flush()

        pedido_items = []
        for item in payload.items:
            producto = db.query(Producto).filter(Producto.nombre.ilike(f"%{item.descripcion}%")).first()
            
            if not producto:
                # [GY-FIX] Generación secuencial de SKUs VS0001-VS9999 para Ingesta
                last_vs = db.query(Producto).filter(Producto.codigo_visual.like('VS%')).order_by(Producto.id.desc()).first()
                next_code = 1
                if last_vs and last_vs.codigo_visual:
                    try:
                        next_code = int(last_vs.codigo_visual.replace("VS", "")) + 1
                    except:
                        next_code = 1
                
                codigo_vs = f"VS{str(next_code).zfill(4)}"
                nuevo_sku = 80000 + next_code # Para evitar colisiones con el constraint entero único
                
                rubro = db.query(Rubro).first()
                if not rubro:
                    rubro = Rubro(codigo="GEN", nombre="Genérico Automático")
                    db.add(rubro)
                    db.flush()
                
                producto = Producto(
                    nombre=item.descripcion.upper(),
                    codigo_visual=codigo_vs,
                    sku=nuevo_sku,
                    rubro_id=rubro.id,
                    activo=True,
                    tipo_producto='INSUMO'
                )
                db.add(producto)
                db.flush()
                print(f"[INGESTA] Producto auto-creado: {codigo_vs} - {producto.nombre}")
                
            new_p_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario or 0.0,
                nota=""
            )
            db.add(new_p_item)
            db.flush() 
            pedido_items.append(new_p_item)

        # 5. CREATE REMITO
        vto_cae_date = None
        if payload.factura.vto_cae:
            try:
                vto_cae_date = datetime.strptime(payload.factura.vto_cae, "%d/%m/%Y")
            except:
                pass
        
        # [V5] Mirror Numbering: Invoice XXXX-YYYYYYYY -> Remito 0016-YYYYYYYY
        # (Already calculated at the start of the function for anti-duplication)
        if not numero_legal:
            numero_legal = f"0016-{str(nuevo_pedido.id).zfill(8)}"

        if not domicilio:
            domicilio = db.query(Domicilio).first()

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
            
        # 7. [V14 GENOMA] EVO: Upgrade to Level 13
        from backend.clientes.constants import ClientFlags
        
        current_flags = getattr(cliente, 'flags_estado', 0) or 0
        # Build Level 13: Existence (1) | GOLD_ARCA (4) | V14_STRUCT (8)
        target_flags = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT
        
        # [V5] ABM Mutation (15 -> 13): 
        # Si el cliente era nivel 15 (target_flags + VIRGINITY), al emitir el primer remito
        # pierde la virginidad y baja/muta a 13 automáticamente.
        # Merge target flags into current, but ALWAYS remove VIRGINITY (2)
        new_flags = (current_flags | target_flags) & ~ClientFlags.VIRGINITY
        
        if current_flags != new_flags:
            cliente.flags_estado = new_flags
            cliente.estado_arca = 'PENDIENTE_AUDITORIA' # Re-audit if flags changed o se rompio el blanco
            db.add(cliente)
            print(f"Genoma EVO: Cliente {cliente.razon_social} evolucionó de Flag {current_flags} a Flag {new_flags} (Nivel 13)")

        db.commit()
        db.refresh(remito)
        return remito
