from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.remitos import schemas, models
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem
from backend.logistica.models import EmpresaTransporte
from backend.maestros.models import CondicionIva
from backend.contactos.models import Vinculo, VinculoGeografico
from backend.clientes.service import ClienteService # [V5.8] Para alta de sedes

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
            # [V5.4 Robustness] Use full invoice number instead of just suffix to avoid collisions
            # Example: 0001-12345678 -> 0016-0001-12345678
            inv_body = original_invoice.replace("-", "-") # Keep all parts
            numero_legal = f"0016-{inv_body}"
        
        if numero_legal:
            existing_remito = db.query(models.Remito).filter(models.Remito.numero_legal == numero_legal).first()
            if existing_remito:
                raise ValueError(f"Ya existe el Remito {numero_legal} asociado a esta Factura.")
            
        # 1. FIND CLIENT (Anti-Duplication Strategy)
        payload_cuit = (payload.cliente.cuit or "").replace("-", "").strip()
        payload_name = (payload.cliente.razon_social or "").strip()
        payload_id = getattr(payload.cliente, 'id', None)
        
        cliente = None
        if payload_id:
            cliente = db.query(Cliente).filter(Cliente.id == payload_id).first()
            
        if not cliente and payload_cuit and payload_cuit != "00000000000":
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
            # [V5.2 SOLIDITY] Priorizar datos de la Base de Datos (SSoT)
            # Solo actualizar el domicilio si el actual es Nulo o marcado como SIN DOMICILIO FISCAL
            # y el nuevo dato parece válido (no es S/D ni [EXTRACTED] vacío).
            if payload.cliente.domicilio and "[EXTRACTED]" not in payload.cliente.domicilio:
                fiscal = next((d for d in cliente.domicilios if d.es_fiscal and d.activo), None)
                if fiscal and (not fiscal.calle or "SIN DOMICILIO" in (fiscal.calle or "").upper()):
                    fiscal.calle = payload.cliente.domicilio.replace("[EXTRACTED] ", "").strip()
                    db.add(fiscal)
                    print(f"Ingestion: Domicilio sanado para {cliente.razon_social} con datos válidos.")
            
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
        # --- [ADDRESS RESOLUTION - SSoT] ---
        domicilio = None
        
        # [V5.8 GOLD] Alta de Nueva Sede directamente desde Ingesta
        if payload.nuevo_domicilio:
            from backend.clientes import schemas as cliente_schemas
            dom_in = cliente_schemas.DomicilioCreate(
                calle=payload.nuevo_domicilio.calle,
                numero=payload.nuevo_domicilio.numero,
                localidad=payload.nuevo_domicilio.localidad,
                provincia_id=payload.nuevo_domicilio.provincia_id or "X",
                es_entrega=True,
                activo=True
            )
            # Persistimos en Domicilios y vinculamos a Cliente
            domicilio = ClienteService.create_domicilio(db, cliente.id, dom_in)
            print(f"Ingesta: Creada nueva sede de entrega '{domicilio.calle}' para {cliente.razon_social}")

        if not domicilio and payload.domicilio_id:
            domicilio = db.query(Domicilio).get(payload.domicilio_id)
            
        if not domicilio:
            # Prioridad 1: Domicilio Fiscal Activo del Cliente
            domicilio = next((d for d in cliente.domicilios if d.es_fiscal and d.activo), None)
            
        if not domicilio:
            # Prioridad 2: Domicilio de Entrega Activo
            domicilio = next((d for d in cliente.domicilios if d.es_entrega and d.activo), None)

        if not domicilio:
            # Prioridad 3: Resolver vía VinculoGeografico (Universal Vault)
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
            # Prioridad 4: Cualquier domicilio activo o fallback absoluto
            domicilio = next((d for d in cliente.domicilios if d.activo), None)
            if not domicilio and cliente.domicilios:
                domicilio = cliente.domicilios[0]
            
        # Default Transport
        # --- [LOGISTICS RESOLUTION] ---
        transporte_id = payload.transporte_id
        if not transporte_id:
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
            numero_legal=numero_legal,
            bultos=payload.bultos,
            valor_declarado=payload.valor_declarado
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
            
        # 7. [VANGUARD CANON] Genoma 64-bit Evolution - PIN 1974
        from backend.clientes.constants import ClientFlags
        
        current_flags = getattr(cliente, 'flags_estado', 0) or 0
        
        # Base: Activo (1) | Arca (4) | V14 (8) -> Nivel 13
        # Si ya operó, pierde la Virginidad (~2)
        target_base = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT
        
        # Mutación Doctrinal: Forzar Nivel 13 (Apagar Bit 1)
        mutation_flags = (current_flags | target_base) & ~ClientFlags.VIRGINITY
        
        # Sello de Revisión: Si falta Segmento o Lista de Precios, marcar PENDIENTE_REVISION (Bit 20)
        if not cliente.segmento_id or not cliente.lista_precios_id:
            mutation_flags |= ClientFlags.PENDIENTE_REVISION
        else:
            mutation_flags &= ~ClientFlags.PENDIENTE_REVISION

        # [V5] Sello de Origen: Marketing DNA (30-31)
        if payload.cliente.canal == "MLIBRE":
            mutation_flags |= ClientFlags.CH_MLIBRE
        elif payload.cliente.canal == "TIENDANUBE":
            mutation_flags |= ClientFlags.CH_TIENDANUBE
        
        if current_flags != mutation_flags:
            cliente.flags_estado = mutation_flags
            # El estado_arca se sincroniza con el Bit Gold Arca (4)
            cliente.estado_arca = 'VALIDADO' if (mutation_flags & ClientFlags.GOLD_ARCA) else 'PENDIENTE_AUDITORIA'
            db.add(cliente)
            print(f"Vanguard Canon: Cliente {cliente.razon_social} evolucionó a Flag {mutation_flags} (Nivel 13)")


        db.commit()
        db.refresh(remito)
        return remito

    @staticmethod
    def create_manual(db: Session, payload: schemas.ManualRemitoPayload):
        """
        Creates a Manual Remito (Rosa/Blanco) from Frontend data.
        Serie 0015-00003001
        """
        # 1. RESOLVE CLIENT
        cliente = None
        if payload.cliente_id:
             cliente = db.query(Cliente).get(payload.cliente_id)
        
        if not cliente and payload.cliente_nuevo:
             # Create new client using similar logic to ingestion but allowing for "Rosa" status
             # In manual mode, the operator decides.
             from backend.clientes.constants import ClientFlags
             
             # Default Rosa Flags (Level 9/11): Existence (1) | V14 (8)
             # If user provides CUIT, we might treat as Blanco (Bit 4)
             has_cuit = payload.cliente_nuevo.cuit and payload.cliente_nuevo.cuit != "00000000000"
             
             # [DOCTRINA] Rosa = 9/11 (Bits 1, 8. Bit 2 off). Blanco = 13/15 (Bits 1, 4, 8).
             rosa_flags = ClientFlags.EXISTENCE | ClientFlags.V14_STRUCT
             if has_cuit:
                  rosa_flags |= ClientFlags.GOLD_ARCA # Becomes Blanco logic
             
             iva_id = RemitosService._resolve_iva_condition(db, payload.cliente_nuevo.condicion_iva)
             
             cliente = Cliente(
                 razon_social=payload.cliente_nuevo.razon_social or "CLIENTE MANUAL NUEVO",
                 cuit=payload.cliente_nuevo.cuit or "00000000000",
                 activo=True,
                 flags_estado=rosa_flags | ClientFlags.PENDIENTE_REVISION, # Always needs review if new manual
                 estado_arca='PENDIENTE_AUDITORIA',
                 condicion_iva_id=iva_id,
                 fecha_alta=datetime.now()
             )
             db.add(cliente)
             db.flush()
             
             # Auto-create Default Address
             domicilio_def = Domicilio(
                 cliente_id=cliente.id,
                 calle=payload.cliente_nuevo.domicilio or "Dirección Manual",
                 localidad="---",
                 provincia_id="X", 
                 es_fiscal=True,
                 activo=True
             )
             db.add(domicilio_def)
             db.flush()

        if not cliente:
             raise ValueError("Debe seleccionar o crear un cliente funcional para el remito.")

        # 2. CALCULATE NEXT 0015- NUMBER
        last_remito = db.query(models.Remito).filter(models.Remito.numero_legal.like("0015-%")).order_by(models.Remito.numero_legal.desc()).first()
        
        next_val = 3010
        if last_remito and last_remito.numero_legal:
             try:
                  # Expected format: 0015-00003010
                  current_str = last_remito.numero_legal.split("-")[-1]
                  next_val = int(current_str) + 1
             except:
                  next_val = 3010
        
        if next_val < 3010: next_val = 3010
        numero_legal = f"0015-{str(next_val).zfill(8)}"

        # 3. CREATE GHOST PEDIDO
        nuevo_pedido = Pedido(
            cliente_id=cliente.id,
            fecha=datetime.now(),
            nota=payload.observaciones or "Generación Manual de Remito",
            estado="CUMPLIDO", # Manual remitos are born fulfilled
            origen="MANUAL",
            domicilio_entrega_id=payload.domicilio_entrega_id,
            transporte_id=payload.transporte_id
        )
        db.add(nuevo_pedido)
        db.flush()

        # 4. RESOLVE ITEMS (Similar to ingestion but with different schema)
        from backend.productos.models import Producto
        pedido_items = []
        for item in payload.items:
             # Search by description if we don't have a product_id or specific sku
             # For manual remitos, we might just use a generic product or search
             producto = db.query(Producto).filter(Producto.nombre == item.descripcion).first()
             if not producto and item.codigo_visual:
                  producto = db.query(Producto).filter(Producto.codigo_visual == item.codigo_visual).first()
             
             if not producto:
                  # Use/Create generic if not found (Same logic as ingestion)
                  # For brevity, I'll assume many exist or use the existing ingestion-style auto-creation if requested
                  # But here I'll try to find a generic one first
                  producto = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
                  if not producto:
                       # Fallback to ingestion-style auto-creation
                       # [GY-CODE-REUSE] (Internal logic from ingestion)
                       last_vs = db.query(Producto).filter(Producto.codigo_visual.like('VS%')).order_by(Producto.id.desc()).first()
                       nv = 1
                       if last_vs: nv = int(last_vs.codigo_visual.replace("VS", "")) + 1
                       producto = Producto(
                           nombre=item.descripcion.upper(),
                           codigo_visual=f"VS{str(nv).zfill(4)}",
                           sku=85000 + nv, # Manual range
                           rubro_id=1, # Default rubro
                           activo=True
                       )
                       db.add(producto)
                       db.flush()

             new_p_item = PedidoItem(
                 pedido_id=nuevo_pedido.id,
                 producto_id=producto.id,
                 cantidad=item.cantidad,
                 precio_unitario=0.0, # Not usually relevant for manual transport remitos
                 nota="Ítem Manual"
             )
             db.add(new_p_item)
             db.flush()
             pedido_items.append(new_p_item)

        # 5. CREATE REMITO
        # [GY-FIX] Ensure mandatory fields are populated (nullable=False)
        resolved_domicilio_id = payload.domicilio_entrega_id
        if not resolved_domicilio_id:
             # Try to find a fiscal or any address for the client
             first_dom = db.query(Domicilio).filter(Domicilio.cliente_id == cliente.id).first()
             resolved_domicilio_id = first_dom.id if first_dom else None
        
        resolved_transporte_id = payload.transporte_id
        if not resolved_transporte_id:
             # Find first active transport
             from backend.logistica.models import EmpresaTransporte
             first_trans = db.query(EmpresaTransporte).filter(EmpresaTransporte.activo == True).first()
             if not first_trans:
                  # Fallback to any if none active (unlikely but safe)
                  first_trans = db.query(EmpresaTransporte).first()
             resolved_transporte_id = first_trans.id if first_trans else None

        if not resolved_domicilio_id or not resolved_transporte_id:
             raise ValueError("No se pudo determinar un domicilio de entrega o un transporte válido para el remito.")

        remito = models.Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=resolved_domicilio_id,
            transporte_id=resolved_transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=payload.aprobado_para_despacho,
            numero_legal=numero_legal,
            bultos=payload.bultos,
            valor_declarado=payload.valor_declarado
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
    @staticmethod
    def update_remito(db: Session, remito_id: str, payload: schemas.RemitoUpdate):
        """
        Actualiza un remito con soberanía total (V15.2).
        Permite cambiar cliente, forzar dirección y editar cuerpo de ítems.
        """
        remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
        if not remito:
            raise ValueError("Remito no encontrado")
        
        if remito.estado != "BORRADOR" and payload.estado is None:
            raise ValueError("No se puede editar un remito que ya no está en estado BORRADOR.")

        # 1. CAMBIO DE CLIENTE (Si se solicita)
        if payload.cliente_id:
            remito.pedido.cliente_id = payload.cliente_id
            db.add(remito.pedido)
            print(f"Update: Cambiando cliente del remito/pedido a {payload.cliente_id}")

        # 2. FORZADO DE DIRECCIÓN (Si se solicita)
        if payload.nuevo_domicilio:
            new_dom = Domicilio(
                cliente_id=remito.pedido.cliente_id,
                calle=payload.nuevo_domicilio.calle,
                numero=payload.nuevo_domicilio.numero,
                localidad=payload.nuevo_domicilio.localidad,
                provincia_id=payload.nuevo_domicilio.provincia_id,
                activo=True,
                es_fiscal=False
            )
            db.add(new_dom)
            db.flush()
            remito.domicilio_entrega_id = new_dom.id
            print(f"Update: Forzando nueva dirección {new_dom.calle}")

        # 3. ACTUALIZACIÓN DE ÍTEMS (Si se solicita)
        if payload.items is not None:
            # Sincronización de ítems
            existing_items_ids = [i.id for i in remito.items]
            payload_items_ids = [i.id for i in payload.items if i.id is not None]

            # A. Eliminar ítems que no están en el payload
            for r_item in remito.items:
                if r_item.id not in payload_items_ids:
                    print(f"Update: Eliminando ítem ID {r_item.id}")
                    db.delete(r_item)

            # B. Actualizar o Crear ítems
            for p_item_data in payload.items:
                if p_item_data.id:
                    # Actualizar existente
                    r_item = next((i for i in remito.items if i.id == p_item_data.id), None)
                    if r_item:
                        r_item.cantidad = p_item_data.cantidad
                        # Actualizar nota en el pedido_item si es manual
                        if p_item_data.descripcion and r_item.pedido_item:
                            r_item.pedido_item.nota = p_item_data.descripcion
                            db.add(r_item.pedido_item)
                        db.add(r_item)
                else:
                    # Crear nuevo ítem (Ghost Style)
                    from backend.productos.models import Producto
                    prod_v = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
                    
                    new_p_item = PedidoItem(
                        pedido_id=remito.pedido_id,
                        producto_id=prod_v.id if prod_v else 1,
                        cantidad=p_item_data.cantidad,
                        nota=p_item_data.descripcion or "Agregado en Edición",
                        precio_unitario=0.0
                    )
                    db.add(new_p_item)
                    db.flush()

                    new_r_item = models.RemitoItem(
                        remito_id=remito.id,
                        pedido_item_id=new_p_item.id,
                        cantidad=p_item_data.cantidad
                    )
                    db.add(new_r_item)

        # 4. Actualizar campos básicos
        exclude_fields = {"items", "nuevo_domicilio", "cliente_id"}
        update_data = payload.dict(exclude_unset=True, exclude=exclude_fields)
        for key, value in update_data.items():
            setattr(remito, key, value)
        
        db.add(remito)
        db.commit()
        db.refresh(remito)
        return remito
