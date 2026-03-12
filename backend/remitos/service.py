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
    def _resolve_iva_condition(db: Session, name: Optional[str]) -> Optional[str]:
        if not name: return None
        # Normalización para búsqueda
        lookup = name.strip()
        cond = db.query(CondicionIva).filter(CondicionIva.nombre.ilike(f"%{lookup}%")).first()
        return cond.id if cond else None

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
            
        # 1. FIND CLIENT (Anti-Duplication Strategy)
        payload_cuit = (payload.cliente.cuit or "").replace("-", "").strip()
        payload_name = (payload.cliente.razon_social or "").strip()
        
        cliente = None
        if payload_cuit and payload_cuit != "00000000000":
            # Primary search: CUIT (normalized)
            cliente = db.query(Cliente).filter(
                or_(
                    Cliente.cuit == payload_cuit,
                    Cliente.cuit == f"{payload_cuit[:2]}-{payload_cuit[2:10]}-{payload_cuit[10:]}" # Legacy dash support
                )
            ).first()
        
        if not cliente and payload_name:
            # Secondary search: Name (Fuzzy/ILike)
            # This prevents "Desconocido" duplicates when CUIT extraction fails
            cliente = db.query(Cliente).filter(Cliente.razon_social.ilike(f"%{payload_name}%")).first()
            if cliente:
                print(f"Ingestion: Client found by Name fallback: {cliente.razon_social}")
                # [V5 Healing] If we found it by name and it didn't have a CUIT (or had a dummy one), update it
                if not cliente.cuit or cliente.cuit == "00000000000":
                    if payload_cuit and payload_cuit != "00000000000":
                        cliente.cuit = payload_cuit
                        db.add(cliente)
                        print(f"Ingestion: Healing CUIT for client {cliente.razon_social} -> {payload_cuit}")

        if not cliente:
            # [V5 Robustness] TRUST THE PDF but handle missing data.
            print(f"Ingestion: Creating new client from PDF: {payload_name} ({payload_cuit})")
            
            # [V14 GENOMA] Target Level 13: EXISTENCE (1) | GOLD_ARCA (4) | V14_STRUCT (8)
            from backend.clientes.constants import ClientFlags
            gold_flags = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT
            
            iva_id = RemitosService._resolve_iva_condition(db, payload.cliente.condicion_iva)

            cliente = Cliente(
                razon_social=payload_name or "CLIENTE NUEVO (INGESTA)",
                cuit=payload_cuit or "00000000000",
                activo=True,
                flags_estado=gold_flags,
                estado_arca='PENDIENTE_AUDITORIA',
                condicion_iva_id=iva_id,
                lista_precios_id=None,
                fecha_alta=datetime.now()
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
        else:
            # [V5 Healing] Si el cliente existe, aprovechamos para actualizar su domicilio si vino en la factura
            # y el cliente no tiene domicilios activos, o el usuario lo desea.
            if payload.cliente.domicilio and payload.cliente.domicilio != "S/D":
                fiscal = next((d for d in cliente.domicilios if d.es_fiscal and d.activo), None)
                if fiscal and (not fiscal.calle or fiscal.calle == "S/D"):
                    fiscal.calle = payload.cliente.domicilio
                    db.add(fiscal)
                    print(f"Ingestion: Domicilio actualizado para {cliente.razon_social}")
            
            # [NUEVO] Sanación de IVA si está en blanco
            if not cliente.condicion_iva_id and payload.cliente.condicion_iva:
                 iva_id = RemitosService._resolve_iva_condition(db, payload.cliente.condicion_iva)
                 if iva_id:
                      cliente.condicion_iva_id = iva_id
                      db.add(cliente)
                      print(f"Ingestion: IVA sanado para {cliente.razon_social} -> {payload.cliente.condicion_iva}")

        # --- [NUEVO] OPCIÓN SOLO ACTUALIZAR CLIENTE ---
        if payload.solo_actualizar_cliente:
             db.commit()
             print(f"Ingestion: Se decidió solo actualizar el cliente {cliente.razon_social}. Finalizando.")
             return None # Retornamos None (el router debe manejar esto)

        # 2. RESOLVE LOGISTICS via Universal Vault (Vanguard V5)
        # Search for PRINCIPAL_ENTREGA (Bit 1 = 2) or FISCAL (Bit 0 = 1)
        from backend.contactos.models import VinculoGeografico
        
        vinculo = db.query(VinculoGeografico).filter(
            VinculoGeografico.entidad_tipo == 'CLIENTE',
            VinculoGeografico.entidad_id == cliente.id,
            VinculoGeografico.activo == True
        ).order_by(
            (VinculoGeografico.flags_relacion.op('&')(2)).desc(), # Prioritize Principal (Bit 1)
            (VinculoGeografico.flags_relacion.op('&')(1)).desc()  # Then Fiscal (Bit 0)
        ).first()
        
        domicilio = vinculo.domicilio if vinculo else None
        
        if not domicilio:
            # Deep Fallback (Legacy check)
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
            
        # 7. [VANGUARD CANON] Genoma 64-bit Evolution
        from backend.clientes.constants import ClientFlags
        
        current_flags = getattr(cliente, 'flags_estado', 0) or 0
        
        # Base: Existence (0) | Arca (2) | V14 (3)
        target_flags = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT
        
        # Sello de Vida: Ganar HISTORIA (13) y perder VIRGINITY (15)
        # un cliente de factura ya no es virgen.
        mutation_flags = (current_flags | target_flags | ClientFlags.HISTORIA) & ~ClientFlags.VIRGINITY
        
        # Sello de Revisión: Si falta Segmento o Lista de Precios, marcar PENDIENTE_REVISION (20)
        if not cliente.segmento_id or not cliente.lista_precios_id:
            mutation_flags |= ClientFlags.PENDIENTE_REVISION
        else:
            mutation_flags &= ~ClientFlags.PENDIENTE_REVISION

        # Sello de Logística: MULTI_DESTINO (16) if > 1 address in the Vault
        vinculos_count = db.query(VinculoGeografico).filter(
            VinculoGeografico.entidad_tipo == 'CLIENTE',
            VinculoGeografico.entidad_id == cliente.id,
            VinculoGeografico.activo == True
        ).count()
        if vinculos_count > 1:
            mutation_flags |= ClientFlags.MULTI_DESTINO
        else:
            mutation_flags &= ~ClientFlags.MULTI_DESTINO

        # Sello de Origen: Marketing DNA (30-34)
        if payload.cliente.canal == "MLIBRE":
            mutation_flags |= ClientFlags.CH_MLIBRE
        elif payload.cliente.canal == "TIENDANUBE":
            mutation_flags |= ClientFlags.CH_TIENDANUBE
        
        if current_flags != mutation_flags:
            cliente.flags_estado = mutation_flags
            cliente.estado_arca = 'VALIDADO' if (mutation_flags & ClientFlags.GOLD_ARCA) else 'PENDIENTE_AUDITORIA'
            db.add(cliente)
            print(f"Vanguard Canon: Cliente {cliente.razon_social} mutó a Flag {mutation_flags}")

        db.commit()
        db.refresh(remito)
        return remito
