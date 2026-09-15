from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from backend.remitos import schemas, models
from backend.remitos.constants import RemitoFlags
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
    def _recalcular_bits_entrega(db: Session, pedido) -> None:
        """Recalcula Bits 20/21 en el pedido según estado real de entregas.
        OFF/OFF si ninguna entrega, Bit20 si parcial, Bit21 si completa."""
        from backend.pedidos.constants import PedidoFlags
        db.flush()
        # [Card #136] El guard de la Card #125 (RENGLON_AJENO_AL_PEDIDO/CANTIDAD_EXCEDE_PEDIDO)
        # lee cantidad_entregada (-> item.remitos_items) ANTES de crear el remito nuevo, y
        # SQLAlchemy cachea esa relación vacía en el objeto. El RemitoItem se crea con
        # pedido_item_id a mano (no vía la relación), así que ese cache nunca se actualiza, y
        # db.flush() no lo expira. Sin este expire_all(), la consulta de abajo devuelve el
        # mismo PedidoItem ya cacheado -- cantidad_entregada da 0 y los Bits 20/21 nunca prenden.
        db.expire_all()
        items = db.query(PedidoItem).filter(PedidoItem.pedido_id == pedido.id).all()
        if not items:
            return
        has_any = any(item.cantidad_entregada > 0 for item in items)
        is_full = has_any and all(item.cantidad_entregada >= item.cantidad for item in items)
        has_partial = has_any and not is_full
        flags = pedido.flags_estado or 0
        if is_full:
            flags |= int(PedidoFlags.FULL_DELIVERED)
            flags &= ~int(PedidoFlags.HAS_PARTIAL_DELIVERY)
            if flags & int(PedidoFlags.ES_NO_COMERCIAL):
                flags |= int(PedidoFlags.FULL_INVOICED)
        else:
            flags &= ~int(PedidoFlags.FULL_DELIVERED)
            if has_partial:
                flags |= int(PedidoFlags.HAS_PARTIAL_DELIVERY)
            else:
                flags &= ~int(PedidoFlags.HAS_PARTIAL_DELIVERY)
        pedido.flags_estado = flags
        db.add(pedido)

    @staticmethod
    def create_from_ingestion(db: Session, payload: schemas.IngestionPayload):
        """
        Creates a Pedido and Remito from PDF Ingestion Data.
        """
        # [V5.2 OMEGA] Anti-Zombi: Verify if Remito OR Pedido already exists
        original_invoice = (payload.factura.numero or "").strip()
        print(f"[DEBUG INGESTA] Original Invoice from Payload: '{original_invoice}'")
        
        numero_legal = ""
        # [V5.7 Robustness] Handle both "XXXX-YYYYYYYY" and "XXXX YYYYYYYY" or just "YYYYYYYY"
        if "-" in original_invoice:
            parts = original_invoice.split("-")
            if len(parts) >= 2:
                nc_f = str(parts[1]).strip().zfill(8)
                numero_legal = f"0016-{nc_f}"
                print(f"[DEBUG INGESTA] Resolved Numero Legal (Dash Path): {numero_legal}")
        elif " " in original_invoice:
            parts = original_invoice.split()
            if len(parts) >= 2:
                nc_f = str(parts[-1]).strip().zfill(8)
                numero_legal = f"0016-{nc_f}"
                print(f"[DEBUG INGESTA] Resolved Numero Legal (Space Path): {numero_legal}")
        elif original_invoice and original_invoice.isdigit():
             # Pure number - likely just the sequential part
             numero_legal = f"0016-{original_invoice.strip().zfill(8)}"
             print(f"[DEBUG INGESTA] Resolved Numero Legal (Digit Path): {numero_legal}")
        
        if not numero_legal:
            print(f"[DEBUG INGESTA] No valid pattern found in invoice '{original_invoice}'")
        
        # Guard 1: Existing Remito (Committed)
        if numero_legal:
            existing_remito = db.query(models.Remito).filter(models.Remito.numero_legal == numero_legal).first()
            if existing_remito:
                print(f"[INGESTA] Bloqueo: Remito {numero_legal} ya existe.")
                raise HTTPException(status_code=409, detail=f"FACTURA_DUPLICADA: El remito {numero_legal} ya existe.")
        
        # Guard 2: Existing Pedido (Prevent Ghosting during slow transactions)
        if original_invoice:
            note_search = f"Ingesta Automática Factura: {original_invoice}"
            existing_pedido = db.query(Pedido).filter(Pedido.nota == note_search).first()
            if existing_pedido:
                print(f"[INGESTA] Bloqueo OMEGA: Pedido {existing_pedido.id} detectado para factura {original_invoice}.")
                raise HTTPException(status_code=409, detail=f"FACTURA_DUPLICADA: La factura {original_invoice} ya está vinculada al pedido #{existing_pedido.id}.")

        # Guard 3: Existing Factura (Fiscal Mirror)
        if original_invoice and "-" in original_invoice:
            try:
                parts = original_invoice.split("-")
                pv, nc = int(parts[0]), int(parts[1])
                from backend.facturacion.models import Factura
                existing_factura = db.query(Factura).filter(
                    Factura.punto_venta == pv,
                    Factura.numero_comprobante == nc
                ).first()
                if existing_factura:
                    raise HTTPException(status_code=409, detail=f"FACTURA_DUPLICADA: La factura fiscal {original_invoice} ya existe en el sistema.")
            except HTTPException:
                raise
            except (ValueError, IndexError):
                pass

            
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
             db.flush()
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

        # [V5-FLUJO-C] Modo ingesta inteligente
        goto_remito = False
        pedido_items = [] # [GY-FIX] Garantizar inicialización limpia
        
        if payload.modo_ingesta == "VINCULAR_EXISTENTE" and payload.pedido_id_vinculado:
            from backend.pedidos.models import Pedido as PedidoModel
            pedido_existente = db.query(PedidoModel).filter(
                PedidoModel.id == payload.pedido_id_vinculado
            ).first()
            if not pedido_existente:
                # [FIX Bloque 1, doctrina "Remitos Chequeables"] rollback explícito --
                # ver AUDITORIA_REMITOS_CHEQUEABLES_S865.md §3. Sin esto, el llamador
                # real (IngestaService.approve) comitea la misma sesión al marcar el
                # raw como ERROR, arrastrando Cliente/Domicilio nuevos ya flusheados.
                db.rollback()
                raise ValueError(f"Pedido {payload.pedido_id_vinculado} no encontrado")
            nuevo_pedido = pedido_existente
            nuevo_pedido.estado = "FACTURADO"
            db.add(nuevo_pedido)
            db.flush()
            pedido_items = db.query(PedidoItem).filter(
                PedidoItem.pedido_id == nuevo_pedido.id
            ).all()
            goto_remito = True
        elif payload.modo_ingesta == "VINCULAR_PARCIAL" and payload.pedido_id_vinculado:
            from backend.pedidos.models import Pedido as PedidoModel
            pedido_existente = db.query(PedidoModel).filter(
                PedidoModel.id == payload.pedido_id_vinculado
            ).first()
            if not pedido_existente:
                db.rollback()  # [FIX Bloque 1] ver §3 de la auditoría -- misma razón que arriba
                raise ValueError(f"Pedido {payload.pedido_id_vinculado} no encontrado")

            # [DOCTRINA PARCIAL] No cambiamos el estado del pedido, asume que sigue PENDIENTE.
            nuevo_pedido = pedido_existente
            # Se pasará un flag a la seccion de items
            goto_remito = True
        elif payload.modo_ingesta == "VINCULAR_CUMPLIDO" and payload.pedido_id_vinculado:
            from backend.pedidos.models import Pedido as PedidoModel
            pedido_existente = db.query(PedidoModel).filter(
                PedidoModel.id == payload.pedido_id_vinculado
            ).first()
            if not pedido_existente:
                db.rollback()  # [FIX Bloque 1] ver §3 de la auditoría -- misma razón que arriba
                raise ValueError(f"Pedido {payload.pedido_id_vinculado} no encontrado")

            # [V5.9 GOLD] In VINCULAR_CUMPLIDO we just acknowledge the invoice linkage
            # and potentially create a remito if requested, but for now we follow legacy closure.
            # However, we MUST NOT return None if the user expects a remito.
            # Assuming VINCULAR_CUMPLIDO also wants a remito record:
            nuevo_pedido = pedido_existente
            pedido_items = db.query(PedidoItem).filter(PedidoItem.pedido_id == nuevo_pedido.id).all()
            goto_remito = True

        # [Card #125 -- Doctrina Pedido Soberano a nivel renglon] Ningun renglon de la
        # ingesta puede ser ajeno al Pedido vinculado ni exceder lo que todavia tiene
        # pendiente de entrega. Aplica a los 3 modos VINCULAR_* -- modo_cuarentena queda
        # afuera porque genera su propio Pedido a medida de la factura, sin margen de
        # desvio. Antes de esta guarda, un renglon podia facturarse/remitirse de mas (o
        # un producto ajeno al Pedido) sin ningun aviso ni bloqueo (caso real: Pedido #98,
        # factura 2600, guantes veterinarios).
        if goto_remito:
            pedido_items_check = db.query(PedidoItem).filter(
                PedidoItem.pedido_id == nuevo_pedido.id
            ).all()
            for p_item in payload.items:
                target = next(
                    (pi for pi in pedido_items_check if str(pi.producto_id) == str(p_item.producto_id)),
                    None
                )
                if not target:
                    # [FIX Bloque 1] rollback explícito -- sin esto, para VINCULAR_EXISTENTE
                    # el Pedido ya quedaba mutado a estado="FACTURADO" (línea de arriba, ya
                    # flusheado) pese al 409. Probado en vivo, ver §3 de la auditoría.
                    db.rollback()
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"RENGLON_AJENO_AL_PEDIDO: '{p_item.descripcion}' no está cargado en "
                            f"el Pedido #{nuevo_pedido.id}. Actualice el Pedido antes de continuar."
                        )
                    )
                pendiente = target.cantidad - target.cantidad_entregada
                if p_item.cantidad > pendiente + 0.001:  # tolerancia de redondeo flotante
                    db.rollback()  # [FIX Bloque 1] misma razón que arriba
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            f"CANTIDAD_EXCEDE_PEDIDO: '{p_item.descripcion}' trae {p_item.cantidad}, "
                            f"pero el Pedido #{nuevo_pedido.id} solo tiene {pendiente} pendiente. "
                            f"Actualice el Pedido antes de continuar."
                        )
                    )

        if not goto_remito:
            if getattr(payload, 'modo_cuarentena', False):
                # Crear pedido "fantasma" en cuarentena (para cumplir fk del remito)
                from backend.pedidos.models import Pedido as PedidoModel
                nuevo_pedido = PedidoModel(
                    cliente_id=cliente.id,
                    fecha=datetime.now(),
                    nota=f"Ingesta en Cuarentena Factura: {original_invoice}" if original_invoice else "Ingesta en Cuarentena",
                    estado="PENDIENTE",
                    origen="INGESTA_PDF",
                    domicilio_entrega_id=domicilio.id if domicilio else None,
                    transporte_id=transporte_id
                )
                db.add(nuevo_pedido)
                db.flush()
                
                # Crear los items del pedido en base a los items de la ingesta
                for it in payload.items:
                    # Buscar producto por código o descripción
                    producto = None
                    if it.codigo:
                        producto = db.query(Producto).filter(Producto.codigo_visual == it.codigo).first()
                    if not producto:
                        producto = db.query(Producto).filter(Producto.nombre == it.descripcion).first()
                    if not producto:
                        producto = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
                    if not producto:
                        # Fallback a VS9999 / Rubro 1
                        producto = Producto(
                            nombre=it.descripcion.upper(),
                            codigo_visual="VS9999",
                            sku=99999,
                            rubro_id=1,
                            activo=True
                        )
                        db.add(producto)
                        db.flush()
                    
                    new_p_item = PedidoItem(
                        pedido_id=nuevo_pedido.id,
                        producto_id=producto.id,
                        cantidad=it.cantidad,
                        precio_unitario=it.precio_unitario or 0.0,
                        nota="Ítem de Ingesta en Cuarentena"
                    )
                    db.add(new_p_item)
                    db.flush()
                    pedido_items.append(new_p_item)
                
                goto_remito = True
            else:
                # [ARLEQUÍN V2 — DOCTRINA SOLO LECTURA]
                # Una factura sin pedido vinculado no puede procesarse.
                # El operador debe crear o identificar el pedido antes de reintentar.
                db.rollback()  # [FIX Bloque 1] ver §3 de la auditoría
                raise HTTPException(
                    status_code=409,
                    detail="PEDIDO_REQUERIDO: Esta factura no tiene un pedido vinculado. Identifique o cree el pedido correspondiente."
                )

        # 5. CREATE REMITO
        vto_cae_date = None
        if payload.factura.vto_cae:
            try:
                vto_cae_date = datetime.strptime(payload.factura.vto_cae, "%d/%m/%Y")
            except:
                pass
        
        # [V5] Mirror Numbering: Strict AFIP Compliance (Doctrina)
        if not numero_legal:
            # Si llegamos aquí sin numero_legal, el OCR falló y es un error crítico.
            print(f"[DEBUG INGESTA] Numero Legal was empty. Raising explicit error.")
            # [FIX Bloque 1] rollback explícito -- este es justo el punto donde, en
            # modo_cuarentena, ya se habían creado y flusheado el Pedido fantasma,
            # sus PedidoItem y hasta Productos VS9999 nuevos. Sin esto, el 400
            # "OCR falló" dejaba igual toda esa basura persistida. Ver §3 auditoría.
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="NUMERO_COMPROBANTE_REQUERIDO: No se pudo extraer el número de factura del PDF. Verifique el archivo."
            )
        
        print(f"[DEBUG INGESTA] Final Numero Legal from Parser: {numero_legal}")

        if not domicilio:
            domicilio = db.query(Domicilio).first()

        is_cuarentena = getattr(payload, 'modo_cuarentena', False)
        remito = models.Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=False if is_cuarentena else True,
            cae=payload.factura.cae,
            vto_cae=vto_cae_date,
            numero_legal=numero_legal,
            bultos=payload.bultos,
            valor_declarado=payload.valor_declarado
        )
        db.add(remito)
        db.flush()

        # 6. CREATE REMITO ITEMS (GY-TRACE)
        print(f"[REMITO-TRACE] Procesando items para Remito {remito.id} (Pedido {nuevo_pedido.id})")
        remito_items_creados = 0
        if payload.modo_ingesta == "VINCULAR_PARCIAL":
            # Para despachos parciales, construimos los RemitoItem basados en payload.items
            pedido_items = db.query(PedidoItem).filter(PedidoItem.pedido_id == nuevo_pedido.id).all()
            for p_item in payload.items:
                # Buscar el PedidoItem que corresponde a este producto
                target_p_item = next((pi for pi in pedido_items if str(pi.producto_id) == str(p_item.producto_id)), None)
                if not target_p_item:
                    print(f"[REMITO-CRITICAL] ERROR DE INTEGRIDAD: Producto {p_item.producto_id} no pertenece al Pedido Original. Omitiendo asociación.")
                    continue

                r_item = models.RemitoItem(
                    remito_id=remito.id,
                    pedido_item_id=target_p_item.id,
                    cantidad=p_item.cantidad
                )
                db.add(r_item)
                remito_items_creados += 1
                print(f"[REMITO-TRACE] Item parcial vinculado: Remito {remito.id} -> PedidoItem {target_p_item.id} ({p_item.cantidad} uds)")

            # Encender VINCULAR_PARCIAL (Bit 11) en el Remito
            remito.flags_estado = (remito.flags_estado or 0) | int(RemitoFlags.VINCULAR_PARCIAL)
            db.add(remito)

        else:
            # Flujo Total / Existente
            for p_item in pedido_items:
                # [GY-FIX] Verificación estricta de pertenencia: 1 Remito = 1 Pedido
                if p_item.pedido_id != nuevo_pedido.id:
                    print(f"[REMITO-CRITICAL] ERROR DE INTEGRIDAD: PedidoItem {p_item.id} (Pedido {p_item.pedido_id}) no coincide con el Pedido del Remito ({nuevo_pedido.id}). Omitiendo asociación.")
                    continue

                r_item = models.RemitoItem(
                    remito_id=remito.id,
                    pedido_item_id=p_item.id,
                    cantidad=p_item.cantidad
                )
                db.add(r_item)
                remito_items_creados += 1
                print(f"[REMITO-TRACE] Item vinculado: Remito {remito.id} -> PedidoItem {p_item.id}")

        # [Doctrina "Remitos Chequeables", Carlos 2026-09-15] Renglón cero es
        # imposible: ni 0015 ni 0016 pueden existir sin al menos un ítem. Cubre
        # tanto la ingesta en cuarentena con PDF sin ítems parseables como el
        # caso (más raro) de que ningún ítem de VINCULAR_PARCIAL matcheara
        # contra el Pedido.
        # [FIX] db.rollback() explícito, NO alcanza con "no hacer commit acá":
        # el llamador real (IngestaService.approve) atrapa esta excepción y
        # comitea la MISMA sesión para marcar el raw como ERROR -- sin este
        # rollback, ese commit arrastra también el Pedido fantasma y el Remito
        # que ya estaban flusheados (probado en vivo: quedaban persistidos
        # pese al 409).
        if remito_items_creados == 0:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="RENGLON_CERO: La ingesta no generó ningún ítem de remito (factura sin renglones reconocibles). Cargue los ítems a mano o vincule un Pedido existente antes de continuar."
            )

        # 7. [VANGUARD CANON] Genoma 64-bit Evolution - PIN 1974
        from backend.clientes.constants import ClientFlags
        
        current_flags = getattr(cliente, 'flags_estado', 0) or 0
        
        # Base: Activo (1) | Arca (4) | V14 (8) -> Nivel base
        target_base = ClientFlags.EXISTENCE | ClientFlags.GOLD_ARCA | ClientFlags.V14_STRUCT

        # Mutación Doctrinal: Forzar bits base (Bit 1 se preserva — solo se apaga en CUMPLIDO)
        mutation_flags = current_flags | target_base
        
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

        # --- [MODO ESPEJO V5.5] ---
        # Si hay remito y datos de factura, cerramos el loop fiscal (Bit 22 transitorio)
        if remito and payload.factura.numero:
            from backend.facturacion.models import Factura, FacturaItem, FacturaRemito
            
            # Flags: 4227083 (EXISTENCE + IS_VIRGIN + ACTIVE + PASADO_A_PEDIDO + PRE_MODULO_FACTURACION)
            # Semántica sellada en Sesión 800-OF
            mirror_flags = 4227083

            # Extraer punto venta y numero (Formato XXXX-YYYYYYYY)
            pv = 0
            nc = 0
            try:
                parts = payload.factura.numero.split("-")
                if len(parts) == 2:
                    pv = int(parts[0])
                    nc = int(parts[1])
            except: pass

            # Determinar tipo comprobante preliminar
            cond_iva = (payload.cliente.condicion_iva or "").upper()
            tipo = "FACTURA_B"
            if "INSCRIPTO" in cond_iva: tipo = "FACTURA_A"
            elif "MONOTRIBUTO" in cond_iva: tipo = "FACTURA_C"

            # Crear Factura Espejo
            factura_mirror = Factura(
                cliente_id=cliente.id,
                pedido_id=nuevo_pedido.id,
                tipo_comprobante=tipo,
                estado="BORRADOR", 
                punto_venta=pv,
                numero_comprobante=nc,
                fecha_emision=datetime.now().date(),
                total=payload.valor_declarado or 0.0,
                cae=payload.factura.cae,
                cae_vencimiento=vto_cae_date,
                flags_estado=mirror_flags,
                notas_auditoria="GENERADA POR MODO ESPEJO - INGESTA V2"
            )
            db.add(factura_mirror)
            db.flush()
            
            # Vincular N:M (Factura <-> Remito)
            db.add(FacturaRemito(
                factura_id=factura_mirror.id,
                remito_id=remito.id,
                flags_estado=1 # EXISTENCE
            ))
            
            # Ítems (Copia Fiel del PDF/Conserje)
            total_items_mirror = 0.0
            for it in payload.items:
                sub = it.subtotal or (it.cantidad * (it.precio_unitario or 0.0))
                db.add(FacturaItem(
                    factura_id=factura_mirror.id,
                    descripcion=it.descripcion,
                    cantidad=it.cantidad,
                    precio_unitario_neto=it.precio_unitario,
                    alicuota_iva=getattr(it, 'alicuota_iva', 21.0),
                    subtotal_neto=sub
                ))
                total_items_mirror += sub
            
            # Sanación de Totales: Si el total es 0, usamos el acumulado de ítems
            if not factura_mirror.total or factura_mirror.total == 0:
                factura_mirror.total = total_items_mirror
                # Heurística simple para neto gravado si no hay desglose
                factura_mirror.neto_gravado = total_items_mirror / 1.21 
                factura_mirror.iva_21 = total_items_mirror - factura_mirror.neto_gravado
            
            print(f"[MODO ESPEJO] Factura {payload.factura.numero} creada y vinculada con flag {mirror_flags}. Total: {factura_mirror.total}")

        # 8. EVALUAR BITS 20/21 (Edge Case B: R16 cubre entrega completa sin R15 previo)
        RemitosService._recalcular_bits_entrega(db, nuevo_pedido)

        try:
            db.flush()
            db.refresh(remito)
            return remito
        except IntegrityError as ie:
            db.rollback()
            print(f"[INGESTA ERROR] IntegrityError detectado: {str(ie)}")
            # [V5.2] Traducir error técnico a 409 para el Frontend
            raise HTTPException(
                status_code=409,
                detail="FACTURA_DUPLICADA: El registro fiscal ya existe o hay un conflicto de integridad en la base de datos."
            )
        except Exception as ex:
            db.rollback()
            print(f"[INGESTA ERROR] Error inesperado: {str(ex)}")
            raise HTTPException(status_code=500, detail=f"Error interno en el procesamiento: {str(ex)}")

    @staticmethod
    def create_manual(db: Session, payload: schemas.ManualRemitoPayload):
        """
        Creates a Manual Remito (Rosa/Blanco) from Frontend data.
        Standardized to Serie 0015- (Manual, sin CAE)
        """
        # [Bloque 2, doctrina "Remitos Chequeables"] Renglón cero imposible --
        # ver AUDITORIA_REMITOS_CHEQUEABLES_S865.md §2.1. Antes de este chequeo,
        # items: [] pasaba de largo y creaba un remito 0015 (y su Pedido fantasma
        # si tampoco había pedido_id) totalmente vacío, HTTP 200. Probado en vivo.
        if not payload.items:
            raise ValueError("RENGLON_CERO: El remito debe tener al menos un ítem.")

        nuevo_pedido = None
        cliente = None
        
        # 0. RESOLVE PEDIDO EXISTENTE
        if payload.pedido_id:
             from backend.pedidos.models import Pedido
             nuevo_pedido = db.query(Pedido).filter(Pedido.id == payload.pedido_id).first()
             if not nuevo_pedido:
                  raise ValueError(f"No se encontró el pedido {payload.pedido_id}")
             cliente = nuevo_pedido.cliente
             print(f"Manual Remito: Usando pedido existente #{nuevo_pedido.id}")

        # 1. RESOLVE CLIENT (Si no hay pedido existente)
        if not nuevo_pedido:
             if payload.cliente_id:
                  cliente = db.query(Cliente).get(payload.cliente_id)
             
             if not cliente and payload.cliente_nuevo:
                  from backend.clientes.constants import ClientFlags
                  has_cuit = payload.cliente_nuevo.cuit and payload.cliente_nuevo.cuit != "00000000000"
                  rosa_flags = ClientFlags.EXISTENCE | ClientFlags.V14_STRUCT
                  if has_cuit:
                       rosa_flags |= ClientFlags.GOLD_ARCA
                  
                  iva_id = RemitosService._resolve_iva_condition(db, payload.cliente_nuevo.condicion_iva)
                  
                  cliente = Cliente(
                      razon_social=payload.cliente_nuevo.razon_social or "CLIENTE MANUAL NUEVO",
                      cuit=payload.cliente_nuevo.cuit or "00000000000",
                      activo=True,
                      flags_estado=rosa_flags | ClientFlags.PENDIENTE_REVISION,
                      estado_arca='PENDIENTE_AUDITORIA',
                      condicion_iva_id=iva_id,
                      fecha_alta=datetime.now()
                  )
                  db.add(cliente)
                  db.flush()
                  
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
                  raise ValueError(f"No se encontró/creó cliente.")

        # 2. CALCULATE NEXT 0015- NUMBER
        last_remito = db.query(models.Remito).filter(models.Remito.numero_legal.like("0015-%")).order_by(models.Remito.numero_legal.desc()).first()

        next_val = 3010
        if last_remito and last_remito.numero_legal:
             try:
                  current_str = last_remito.numero_legal.split("-")[-1]
                  next_val = int(current_str) + 1
             except:
                  next_val = 3010

        if next_val < 3010: next_val = 3010
        numero_legal = f"0015-{str(next_val).zfill(8)}"


        # 3. CREATE GHOST PEDIDO (Solo si no existe)
        if not nuevo_pedido:
             from backend.pedidos.models import Pedido
             nuevo_pedido = Pedido(
                 cliente_id=cliente.id,
                 fecha=datetime.now(),
                 nota=payload.observaciones or "Generación Manual de Remito",
                 estado="PENDIENTE",
                 origen="MANUAL",
                 domicilio_entrega_id=payload.domicilio_entrega_id,
                 transporte_id=payload.transporte_id
             )
             db.add(nuevo_pedido)
             db.flush()

        # 4. RESOLVE ITEMS
        from backend.productos.models import Producto
        pedido_items_mapped = []
        is_partial = False
        
        if payload.pedido_id:
             # Asociar a items de pedido existente
             original_items = db.query(PedidoItem).filter(PedidoItem.pedido_id == nuevo_pedido.id).all()
             for item in payload.items:
                  # Matching by description or cod_visual
                  target_pi = next((pi for pi in original_items if pi.producto.nombre == item.descripcion or (item.codigo_visual and pi.producto.codigo_visual == item.codigo_visual)), None)
                  
                  if target_pi:
                       if item.cantidad < target_pi.cantidad:
                            is_partial = True
                       pedido_items_mapped.append({"pi_id": target_pi.id, "cantidad": item.cantidad})
                  else:
                       # Agregado manualmente en remito
                       producto = db.query(Producto).filter(Producto.nombre == item.descripcion).first()
                       if not producto and item.codigo_visual:
                            producto = db.query(Producto).filter(Producto.codigo_visual == item.codigo_visual).first()
                       if not producto:
                            producto = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
                       
                       new_p_item = PedidoItem(
                           pedido_id=nuevo_pedido.id,
                           producto_id=producto.id if producto else 1,
                           cantidad=item.cantidad,
                           precio_unitario=0.0,
                           nota="Agregado en Remito Manual"
                       )
                       db.add(new_p_item)
                       db.flush()
                       pedido_items_mapped.append({"pi_id": new_p_item.id, "cantidad": item.cantidad})

             # Revisar si quedaron items fuera (envío parcial)
             enviados_ids = [pi["pi_id"] for pi in pedido_items_mapped]
             missing = [pi for pi in original_items if pi.id not in enviados_ids]
             if missing:
                  is_partial = True

             if is_partial:
                  nota_existente = nuevo_pedido.nota or ""
                  msg = f"\n[SISTEMA] Remito Parcial {numero_legal} generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}."
                  if msg not in nota_existente:
                       nuevo_pedido.nota = nota_existente + msg
                  db.add(nuevo_pedido)
        else:
             # Ghost Pedido logic
             for item in payload.items:
                  producto = db.query(Producto).filter(Producto.nombre == item.descripcion).first()
                  if not producto and item.codigo_visual:
                       producto = db.query(Producto).filter(Producto.codigo_visual == item.codigo_visual).first()
                   
                  if not producto:
                       producto = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
                       if not producto:
                            last_vs = db.query(Producto).filter(Producto.codigo_visual.like('VS%')).order_by(Producto.id.desc()).first()
                            nv = 1
                            if last_vs: nv = int(last_vs.codigo_visual.replace("VS", "")) + 1
                            producto = Producto(
                                nombre=item.descripcion.upper(),
                                codigo_visual=f"VS{str(nv).zfill(4)}",
                                sku=85000 + nv,
                                rubro_id=1,
                                activo=True
                            )
                            db.add(producto)
                            db.flush()

                  new_p_item = PedidoItem(
                      pedido_id=nuevo_pedido.id,
                      producto_id=producto.id,
                      cantidad=item.cantidad,
                      precio_unitario=0.0,
                      nota="Ítem Manual"
                  )
                  db.add(new_p_item)
                  db.flush()
                  pedido_items_mapped.append({"pi_id": new_p_item.id, "cantidad": item.cantidad})

        # 5. CREATE REMITO
        resolved_domicilio_id = payload.domicilio_entrega_id
        if not resolved_domicilio_id:
             first_dom = db.query(Domicilio).filter(Domicilio.cliente_id == cliente.id).first()
             resolved_domicilio_id = first_dom.id if first_dom else None
        
        resolved_transporte_id = payload.transporte_id
        if not resolved_transporte_id:
             from backend.logistica.models import EmpresaTransporte
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
        print(f"[REMITO-TRACE] Procesando {len(pedido_items_mapped)} items para Remito {remito.id} (Pedido {nuevo_pedido.id})")
        for p_item in pedido_items_mapped:
            r_item = models.RemitoItem(
                remito_id=remito.id,
                pedido_item_id=p_item["pi_id"],
                cantidad=p_item["cantidad"]
            )
            db.add(r_item)

        # 7. EVALUAR HAS_PARTIAL_DELIVERY (Bit 20) + FULL_DELIVERED (Bit 21)
        RemitosService._recalcular_bits_entrega(db, nuevo_pedido)

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

        # [Bloque 2, doctrina "Remitos Chequeables"] Renglón cero imposible --
        # ver AUDITORIA_REMITOS_CHEQUEABLES_S865.md §2.1. Antes de este chequeo,
        # un PATCH con items: [] vaciaba el remito a cero renglones, HTTP 200,
        # sin borrar el remito en sí. Probado en vivo. Si la intención es
        # eliminar el remito, existe DELETE /remitos/{id}.
        if payload.items is not None and len(payload.items) == 0:
            raise ValueError("RENGLON_CERO: Un remito no puede quedar sin ítems. Para eliminarlo, use la opción de borrar el remito.")

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

        if remito.pedido and (payload.items is not None or getattr(payload, 'estado', None) == "ANULADO"):
            RemitosService._recalcular_bits_entrega(db, remito.pedido)

        db.add(remito)
        db.commit()
        db.refresh(remito)
        return remito

    @staticmethod
    def create_puente_factura(db: Session, factura_id: str):
        """
        Crea o vincula un remito logístico a partir de una Factura sellada.
        Diseñado para el flujo: Sellar Factura AFIP -> Asistir Logística.
        """
        import uuid as _uuid
        from backend.facturacion.models import Factura, FacturaRemito
        from backend.logistica.models import EmpresaTransporte

        factura = db.query(Factura).filter(Factura.id == _uuid.UUID(factura_id)).first()
        if not factura:
            raise ValueError("Factura no encontrada para el puente logístico.")

        pedido = factura.pedido
        if not pedido:
            raise ValueError("Factura sin pedido táctico origen.")

        def _numero_legal_arca(factura):
            if factura.numero_comprobante is not None:
                # [V5.2 OMEGA] Estandarización a 2 partes (Prefix 0016- para automático)
                nc = str(factura.numero_comprobante).zfill(8)
                return f"0016-{nc}"
            
            raise ValueError("NUMERO_COMPROBANTE_REQUERIDO: La factura fiscal no tiene número asignado.")


        def _vincular_factura_remito(db, factura, remito):
            vinculo = db.query(FacturaRemito).filter(
                FacturaRemito.factura_id == factura.id,
                FacturaRemito.remito_id == remito.id
            ).first()
            if not vinculo:
                db.add(FacturaRemito(
                    factura_id=factura.id,
                    remito_id=remito.id,
                    flags_estado=1
                ))

        # 1. Si ya existe un remito en el pedido, inyectar CAE y vincular N:M
        remito_existente = db.query(models.Remito).filter(models.Remito.pedido_id == pedido.id).first()
        if remito_existente:
            remito_existente.cae = factura.cae
            remito_existente.vto_cae = factura.cae_vencimiento
            if not remito_existente.numero_legal or "0015" in remito_existente.numero_legal:
                remito_existente.numero_legal = _numero_legal_arca(factura)
            db.add(remito_existente)
            _vincular_factura_remito(db, factura, remito_existente)
            # [Bloque 3, doctrina "Remitos Chequeables"] Esta rama no cambia
            # cantidades del remito, pero recalcular acá es barato e idempotente
            # -- si el remito ya venía con los bits desalineados por otra causa,
            # esto lo autocorrige de paso. Ver AUDITORIA_REMITOS_CHEQUEABLES_S865.md.
            RemitosService._recalcular_bits_entrega(db, pedido)
            db.commit()
            db.refresh(remito_existente)
            return remito_existente

        # 2. Si no existe, crearlo fresco (Flujo RAR Asíncrono)
        transporte_id = pedido.transporte_id
        if not transporte_id:
            transporte = db.query(EmpresaTransporte).filter(EmpresaTransporte.flags_estado.op('&')(2) != 0).first()
            transporte_id = transporte.id if transporte else None

        domicilio_id = pedido.domicilio_entrega_id
        if not domicilio_id:
            d_fiscal = next((d for d in pedido.cliente.domicilios if d.es_fiscal and d.activo), None)
            domicilio_id = d_fiscal.id if d_fiscal else (pedido.cliente.domicilios[0].id if pedido.cliente.domicilios else None)

        remito = models.Remito(
            pedido_id=pedido.id,
            domicilio_entrega_id=domicilio_id,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=True,
            cae=factura.cae,
            vto_cae=factura.cae_vencimiento,
            numero_legal=_numero_legal_arca(factura),
            bultos=int(pedido.bultos) if hasattr(pedido, 'bultos') and pedido.bultos else 1,
            valor_declarado=factura.total or 0.0
        )
        db.add(remito)
        db.flush()

        for p_item in pedido.items:
            db.add(models.RemitoItem(
                remito_id=remito.id,
                pedido_item_id=p_item.id,
                cantidad=p_item.cantidad
            ))

        _vincular_factura_remito(db, factura, remito)

        # [Bloque 3, doctrina "Remitos Chequeables"] Quinta ruta sin cobertura de
        # Bits 20/21 (ver AUDITORIA_REMITOS_CHEQUEABLES_S865.md §2.2/§5-ter): esta
        # función existe desde 67b06853 (22/04) y crea un Remito con TODA la
        # cantidad del Pedido copiada -- sin esto, un pedido cubierto al 100% por
        # este camino nunca encendía Bit 21 (mismo bug que Card #81/S839, en una
        # ruta que esa auditoría no vio).
        RemitosService._recalcular_bits_entrega(db, pedido)

        db.commit()
        db.refresh(remito)
        print(f"Logística Asíncrona: Remito {remito.numero_legal} generado y vinculado a Factura #{factura.id}")
        return remito

    @staticmethod
    def get_entregas(
        db: Session,
        cliente_id: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        producto_id: Optional[int] = None,
        oc: Optional[str] = None,
        incluir_anulados: bool = False,
    ) -> dict:
        """
        [Reporte de Entregas — Zona Verde] Filas planas: una por renglón de remito
        (más un placeholder por renglón de pedido sin ninguna entrega), para poder
        reconstruir "qué remitos cubrieron esta OC/pedido" — hoy inexistente en el
        sistema. Diseño consolidado en Q:/.../MAPA_TRABAJO_TRAZABILIDAD_REMITOS_S864.md.

        Solo lectura: consultas batched (sin N+1), no toca schema/genoma/ciclo de vida.
        """
        from sqlalchemy.orm import joinedload
        from backend.facturacion.models import Factura, FacturaRemito

        def _norm_oc(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            return " ".join(value.strip().upper().split())

        # 1) PedidoItems candidatos (filtros SQL-level: baratos y selectivos).
        item_query = (
            db.query(PedidoItem)
            .join(Pedido, PedidoItem.pedido_id == Pedido.id)
            .options(
                joinedload(PedidoItem.pedido).joinedload(Pedido.cliente),
                joinedload(PedidoItem.producto),
            )
        )
        if cliente_id:
            item_query = item_query.filter(Pedido.cliente_id == cliente_id)
        if producto_id:
            item_query = item_query.filter(PedidoItem.producto_id == producto_id)
        if oc:
            item_query = item_query.filter(Pedido.oc.ilike(f"%{oc.strip()}%"))

        pedido_items = item_query.all()
        pedido_item_ids = [pi.id for pi in pedido_items]

        # 2) RemitoItems de esos renglones (batched, sin N+1).
        remito_items_by_pedido_item_id: dict = {}
        remito_ids = set()
        if pedido_item_ids:
            ri_query = (
                db.query(models.RemitoItem)
                .filter(models.RemitoItem.pedido_item_id.in_(pedido_item_ids))
                .options(joinedload(models.RemitoItem.remito))
            )
            for ri in ri_query.all():
                if not ri.remito:
                    continue
                if not incluir_anulados and ri.remito.estado == "ANULADO":
                    continue
                remito_items_by_pedido_item_id.setdefault(ri.pedido_item_id, []).append(ri)
                remito_ids.add(ri.remito_id)

        # 3) Facturas vinculadas a esos remitos — TODAS, no vinculos_facturas[0]
        # (ver "Foco: Factura 1:N Remitos" en el mapa de trabajo).
        facturas_by_remito_id: dict = {}
        if remito_ids:
            fr_query = (
                db.query(FacturaRemito)
                .filter(FacturaRemito.remito_id.in_(remito_ids))
                .options(joinedload(FacturaRemito.factura))
            )
            for fr in fr_query.all():
                if not fr.factura:
                    continue
                facturas_by_remito_id.setdefault(fr.remito_id, []).append(fr.factura)

        def _facturas_str(remito_id) -> str:
            facturas = facturas_by_remito_id.get(remito_id) or []
            return ", ".join(f.numero_completo for f in facturas)

        # 4) Ensamblado de filas planas.
        filas = []
        oc_por_pedido: dict = {}  # pedido_id -> oc normalizada (para OC_EN_VARIOS_PEDIDOS)
        for p_item in pedido_items:
            pedido = p_item.pedido
            cliente = pedido.cliente if pedido else None
            producto = p_item.producto
            nombre_producto = producto.nombre if producto else (p_item.nota or "Ítem")
            codigo_producto = producto.codigo_visual if producto else None
            if pedido:
                oc_por_pedido[pedido.id] = _norm_oc(pedido.oc)

            r_items = remito_items_by_pedido_item_id.get(p_item.id, [])
            fila_base = {
                "cliente_id": str(cliente.id) if cliente else None,
                "cliente": cliente.razon_social if cliente else None,
                "oc": pedido.oc if pedido else None,
                "pedido_id": pedido.id if pedido else None,
                "fecha_pedido": pedido.fecha.isoformat() if pedido and pedido.fecha else None,
                "pedido_item_id": p_item.id,
                "producto_id": producto.id if producto else None,
                "producto": f"{codigo_producto} - {nombre_producto}" if codigo_producto else nombre_producto,
                "cantidad_pedida": p_item.cantidad,
            }

            if not r_items:
                fila = dict(fila_base)
                fila.update({
                    "remito": None, "fecha_documento": None,
                    "cantidad_remitida": 0.0, "factura": None,
                })
                filas.append(fila)
                continue

            for ri in r_items:
                remito = ri.remito
                fecha_doc = remito.fecha_creacion
                facturas = facturas_by_remito_id.get(remito.id) or []
                if facturas and facturas[0].fecha_emision:
                    fecha_doc = facturas[0].fecha_emision
                fila = dict(fila_base)
                fila.update({
                    "remito": remito.numero_legal,
                    "remito_id": str(remito.id),
                    "remito_estado": remito.estado,
                    "fecha_documento": fecha_doc.isoformat() if fecha_doc else None,
                    "cantidad_remitida": ri.cantidad,
                    "factura": _facturas_str(remito.id) or None,
                })
                filas.append(fila)

        # 5) Filtro de fecha — sobre la fecha efectiva de cada fila (fecha_documento
        # si hay entrega, si no fecha_pedido), aplicado en Python: la consulta de
        # arriba ya viene acotada por cliente/oc/producto y no vale la pena partir
        # en dos queries SQL distintas (con entrega / sin entrega) por esto.
        if desde or hasta:
            def _en_rango(fila) -> bool:
                raw = fila["fecha_documento"] or fila["fecha_pedido"]
                if not raw:
                    return False
                fecha = datetime.fromisoformat(raw)
                if desde and fecha < desde:
                    return False
                if hasta and fecha > hasta:
                    return False
                return True
            filas = [f for f in filas if _en_rango(f)]

        # 6) Anomalías.
        anomalias = []

        # SOBRE_ENTREGA y OC_EN_VARIOS_PEDIDOS — derivadas del set ya filtrado por
        # cliente/producto/oc (tiene sentido acotarlas al mismo universo de la consulta).
        for p_item in pedido_items:
            entregado = sum(ri.cantidad for ri in remito_items_by_pedido_item_id.get(p_item.id, []))
            if entregado > p_item.cantidad:
                anomalias.append({
                    "tipo": "SOBRE_ENTREGA",
                    "pedido_id": p_item.pedido_id,
                    "pedido_item_id": p_item.id,
                    "detalle": f"Entregado {entregado} sobre pedido {p_item.cantidad}",
                })

        oc_a_pedidos: dict = {}
        for pedido_id, oc_norm in oc_por_pedido.items():
            if not oc_norm:
                continue
            oc_a_pedidos.setdefault(oc_norm, set()).add(pedido_id)
        for oc_norm, pedido_ids in oc_a_pedidos.items():
            if len(pedido_ids) > 1:
                anomalias.append({
                    "tipo": "OC_EN_VARIOS_PEDIDOS",
                    "oc": oc_norm,
                    "pedido_ids": sorted(pedido_ids),
                })

        # REMITO_SIN_RENGLONES, REMITO_SIN_PEDIDO, NUMERO_LEGAL_DUPLICADO — son
        # anomalías estructurales globales (no dependen de los filtros de cliente/
        # producto/OC: un remito huérfano no tiene pedido del cual heredar cliente).
        remitos_globales_query = db.query(models.Remito).options(joinedload(models.Remito.items))
        if not incluir_anulados:
            remitos_globales_query = remitos_globales_query.filter(models.Remito.estado != "ANULADO")
        remitos_globales = remitos_globales_query.all()
        pedido_ids_existentes = {p.id for p in db.query(Pedido.id).all()}
        numero_legal_count: dict = {}
        for remito in remitos_globales:
            if not remito.items:
                anomalias.append({
                    "tipo": "REMITO_SIN_RENGLONES",
                    "remito_id": str(remito.id),
                    "remito": remito.numero_legal,
                })
            if remito.pedido_id not in pedido_ids_existentes:
                anomalias.append({
                    "tipo": "REMITO_SIN_PEDIDO",
                    "remito_id": str(remito.id),
                    "remito": remito.numero_legal,
                    "pedido_id": remito.pedido_id,
                })
            if remito.numero_legal:
                numero_legal_count.setdefault(remito.numero_legal, []).append(str(remito.id))
        for numero_legal, ids in numero_legal_count.items():
            if len(ids) > 1:
                anomalias.append({
                    "tipo": "NUMERO_LEGAL_DUPLICADO",
                    "numero_legal": numero_legal,
                    "remito_ids": ids,
                })

        return {"filas": filas, "anomalias": anomalias}

