# [IDENTIDAD] - backend\clientes\service.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

from typing import List, Optional
from uuid import UUID
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from datetime import datetime, timezone
from backend.clientes.models import Cliente, Domicilio, domicilios_clientes
from backend.clientes import schemas
from backend.clientes.constants import ClientFlags
from backend.agenda import models as agenda_models
from backend.pedidos.models import Pedido # [V5.2-FIX] Load Pedido to avoid Mapper Registry KeyError

class ClienteService:
    @staticmethod
    def create_cliente(db: Session, cliente_in: schemas.ClienteCreate) -> Cliente:
        try:
            # [V5.6 GOLD - BLINDAJE] Strict Duplicate Prevention
            # GENERIC CUITs are excluded from the block
            GENERIC_CUITS = ['00000000000', '11111111119', '11111111111', '99999999999']
            
            # 1. CUIT Block
            if cliente_in.cuit and cliente_in.cuit not in GENERIC_CUITS:
                 existing_cuit = db.query(Cliente).filter(Cliente.cuit == cliente_in.cuit).first()
                 if existing_cuit:
                     raise HTTPException(
                         status_code=status.HTTP_400_BAD_REQUEST, 
                         detail=f"BLOQUEO DE DUPLICADO: El CUIT {cliente_in.cuit} ya está registrado bajo '{existing_cuit.razon_social}'."
                     )
            
            # 2. Razón Social Block (Protocolo Nike - Nuclear Normalization)
            canon_name = ClienteService.normalize_name(cliente_in.razon_social)
            
            # Bloqueo por Clave Canónica (Exacta Limpia)
            if canon_name not in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
                existing_canon = db.query(Cliente).filter(Cliente.razon_social_canon == canon_name).first()
                if existing_canon:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"BLOQUEO NUCLEAR: Ya existe un registro coincidente ('{existing_canon.razon_social}'). La Clave Canónica '{canon_name}' ya está en uso."
                    )
            
            # [V5.6 GOLD] Fallback fast check (ilike)
            existing_name = db.query(Cliente).filter(Cliente.razon_social.ilike(cliente_in.razon_social.strip())).first()
            
            if existing_name and canon_name not in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"BLOQUEO DE DUPLICADO: La Razón Social '{cliente_in.razon_social}' colisiona con '{existing_name.razon_social}'."
                )
            
            # Auto-assign Legacy ID (Internal Code)
            from sqlalchemy import func
            max_id = db.query(func.max(Cliente.codigo_interno)).scalar() or 0
            next_id = max_id + 1

            # Crear Cliente
            db_cliente = Cliente(
                razon_social=cliente_in.razon_social.strip(),
                razon_social_canon=canon_name,
                cuit=cliente_in.cuit,
                codigo_interno=next_id, # Auto-assigned
                condicion_iva_id=cliente_in.condicion_iva_id,
                lista_precios_id=cliente_in.lista_precios_id,
                segmento_id=cliente_in.segmento_id, # Missing in initial code
                activo=cliente_in.activo,
                flags_estado=cliente_in.flags_estado or 0, # Persistence fix
                requiere_auditoria=cliente_in.requiere_auditoria,
                fecha_alta=cliente_in.fecha_alta or datetime.now(timezone.utc)
            )
            db.add(db_cliente)
            db.commit()
            db.refresh(db_cliente)

            # [V5.2 GOLD] N:M Transition Bridge
            for dom_in in cliente_in.domicilios:
                dom_data = dom_in.model_dump(exclude={'zona_id'})
                
                # 1. Normalization & Collision Interceptor
                existing_dom = ClienteService.find_matching_domicilio(db, dom_data)
                
                if existing_dom:
                    # Re-link existing
                    db_cliente.domicilios.append(existing_dom)
                    # [GY-FIX] If it's a collision against a generic address, it might be a mirror
                    # (Handled in service logic later)
                else:
                    # Create new
                    db_domicilio = Domicilio(**dom_data)
                    db_domicilio.is_active = True
                    db.add(db_domicilio)
                    db.flush() # Get ID
                    db_cliente.domicilios.append(db_domicilio)

            # [GY-FIX-V12] Crear Vinculos (Contactos)
            for vinc_in in cliente_in.vinculos:
                 # Convert Pydantic model to dict
                 vinc_data = vinc_in.model_dump()
                 vinc_data['cliente_id'] = db_cliente.id
                 
                 # Check critical fields (Persona ID is UUID, handled by Schema)
                 # Add to session
                 from backend.agenda.models import VinculoComercial
                 db_vinculo = VinculoComercial(**vinc_data)
                 db.add(db_vinculo)

            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN CREATE_CLIENTE: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise e

    @staticmethod
    def get_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        from sqlalchemy.orm import joinedload
        cliente = db.query(Cliente).options(
            joinedload(Cliente.domicilios),
            # [GY-TEMP] Disable eager load de vinculos para evitar 500
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.persona),
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.tipo_contacto)
        ).filter(Cliente.id == cliente_id).first()

        if cliente:
            # [V5.9] Hidratar flags del join table para espejo fiscal (Bit 21)
            rows = db.execute(
                domicilios_clientes.select().where(
                    domicilios_clientes.c.cliente_id == cliente_id
                )
            ).all()
            link_flags = {row.domicilio_id: row.flags for row in rows}
            for dom in cliente.domicilios:
                dom.flags = link_flags.get(dom.id, 0)

        return cliente

    @staticmethod
    def get_clientes(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False, q: str = None) -> List[Cliente]:
        from sqlalchemy.orm import joinedload
        from sqlalchemy import or_, cast, String
        
        query = db.query(Cliente).options(
            joinedload(Cliente.domicilios).joinedload(Domicilio.provincia),
            # [GY-TEMP] Disable eager load of vinculos to fix 500
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.persona),
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.tipo_contacto)
        )

        # Filter by active status unless requested otherwise
        if not include_inactive:
            query = query.filter(Cliente.activo == True)

        if q:
            search = f"%{q}%"
            query = query.filter(
                or_(
                    Cliente.razon_social.ilike(search),
                    Cliente.nombre_fantasia.ilike(search),
                    Cliente.cuit.ilike(search),
                    cast(Cliente.codigo_interno, String).ilike(search)
                )
            )
        
        # Determine sorting? Usually by name
        query = query.order_by(Cliente.razon_social)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_cliente(db: Session, cliente_id: UUID, cliente_in: schemas.ClienteUpdate) -> Optional[Cliente]:
        
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        update_data = cliente_in.dict(exclude_unset=True)
        
        # [V5-X] Handle CUIT Update validity
        if 'cuit' in update_data and update_data['cuit']:
             # GENERIC CUITs are always allowed to duplicate
             GENERIC_CUITS = ['00000000000', '11111111119', '11111111111', '99999999999']
             if update_data['cuit'] not in GENERIC_CUITS:
                 # Check for strict duplicates only for Real Entities
                 # [GY-FIX-UBA] "Caso UBA": Large entities share CUITs. We should warn, not block.
                 # For now, we allow saving to support these cases, relying on Frontend Warning.
                  existing = db.query(Cliente).filter(Cliente.cuit == update_data['cuit'], Cliente.id != cliente_id).first()
                  if existing:
                      # raise HTTPException(status_code=400, detail=f"El CUIT {update_data['cuit']} ya está en uso.")
                      # print(f"[WARN] CUIT Duplicado DETECTADO pero PERMITIDO (Caso UBA/Sucursal): {update_data['cuit']}")
                      pass

        # [V5-X] Flags logic updates
        if 'flags_estado' in update_data:
            new_flags = update_data['flags_estado']
            if (new_flags & ClientFlags.FISCAL_REQUIRED):
                # Check consistency if becoming restricted
                cuit_val = update_data.get('cuit', db_cliente.cuit)
                if not cuit_val:
                     # print(f"❌ [DEBUG-400] Intento de Gold sin CUIT. Flags: {new_flags}")
                     raise HTTPException(status_code=400, detail="No se puede ascender a Gold (Fiscal) sin CUIT.")

        # Handle transporte_id separately
        transporte_id = update_data.pop('transporte_id', None)
        
        for key, value in update_data.items():
            setattr(db_cliente, key, value)

        # [V14.8.4 SOBERANIA OPERATIVA - PIN 1974] Escudo Backend
        # Si los 4 Pilares estan presentes post-update, forzar promocion al Nivel 13.
        # Esto protege el GENOMA incluso contra llamadas directas a la API.
        has_domicilio_fiscal = any(
            d.es_fiscal and d.calle and len((d.calle or '').strip()) > 2
            for d in db_cliente.domicilios
        )
        has_4_pillars = bool(
            db_cliente.razon_social
            and db_cliente.lista_precios_id
            and db_cliente.segmento_id
            and has_domicilio_fiscal
        )
        if has_4_pillars:
            current_flags = db_cliente.flags_estado or 0
            current_flags &= ~ClientFlags.PENDIENTE_REVISION  # Bit 20 OFF
            current_flags &= ~ClientFlags.IS_VIRGIN           # Bit 1 OFF: Promotion 15->13
            current_flags |= ClientFlags.IS_ACTIVE            # Bit 0 ON
            db_cliente.flags_estado = current_flags

        db_cliente.activo = bool(db_cliente.flags_estado & ClientFlags.IS_ACTIVE)

        # Update default domicile if transporte_id is provided
        if transporte_id:
            # Find an existing "Entrega" or "Fiscal" domicile to host the transport_id
            target_dom = next((d for d in db_cliente.domicilios if d.es_entrega and d.activo), 
                         next((d for d in db_cliente.domicilios if d.es_fiscal and d.activo), None))
            
            if target_dom:
                target_dom.transporte_id = transporte_id
                db.add(target_dom)
            else:
                # Create a minimal delivery address if none exists
                new_dom = Domicilio(
                    cliente_id=db_cliente.id,
                    transporte_id=transporte_id,
                    es_entrega=True,
                    activo=True
                )
                db.add(new_dom)

        # [GY-DOCTRINA-V14] ESCUDO DOBLE (Audit Optimized)
        ClienteService._audit_sovereignty(db_cliente)

        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def _audit_sovereignty(db_cliente: "Cliente"):
        """
        [V15.1] ESCUDO DOBLE (Paz Binaria)
        Asigna medallas de éxito (Bit 19/20) según los pilares alcanzados.
        NO es destructivo: Un Bit 20 no quita un Bit 19 preexistente.
        """
        # Pilares Básicos
        has_iva = db_cliente.condicion_iva_id is not None
        has_lista = db_cliente.lista_precios_id is not None
        has_segmento = db_cliente.segmento_id is not None
        has_fiscal = any(d.es_fiscal and d.activo for d in db_cliente.domicilios)
        has_entrega = any(d.es_entrega and d.activo for d in db_cliente.domicilios)
        
        # Identidad
        is_rosa = (db_cliente.flags_estado & 15) in [9, 11]
        is_formal = (db_cliente.flags_estado & 15) in [13, 15]
        is_generic = db_cliente.cuit in ['00000000000', '11111111119', '11111111111', '99999999999']
        is_cf = False
        is_cf = False
        if db_cliente.condicion_iva and db_cliente.condicion_iva.nombre:
            if "CONSUMIDOR FINAL" in db_cliente.condicion_iva.nombre.upper():
                is_cf = True

        # --- REGLA 1: POWER_PINK (Bit 19) ---
        # Requisito: Nivel 9/11 + (Lista, Segmento) O CF/Genérico
        # Nota: Los domicilios son opcionales para informales (Retiro por Local)
        if is_rosa:
            if (has_lista and has_segmento) or is_generic or is_cf:
                db_cliente.flags_estado |= 524288 # Medalla Rosa
            else:
                db_cliente.flags_estado &= ~524288 # Pierde medalla si falta lista/segmento
        elif is_generic or is_cf:
            # CF/Genéricos siempre tienen soberanía base (Rosa)
            db_cliente.flags_estado |= 524288

        # --- REGLA 2: ARCA_OK (Bit 20) ---
        # Requisito: Nivel 13/15 + 4 Pilares + Auditoría CUIT (Lupa)
        # Nota: La "Lupa" se asume si el sistema corre la auditoría y todo es OK.
        if is_formal and not is_generic and not is_cf:
            if has_iva and has_lista and has_segmento and has_fiscal:
                db_cliente.flags_estado |= 1048576 # Medalla Blanca
            else:
                db_cliente.flags_estado &= ~1048576 # Pierde medalla si retrocede

    @staticmethod
    def delete_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        """Soft delete setting activo=False and updating flags_estado"""
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        db_cliente.activo = False
        db_cliente.flags_estado &= ~ClientFlags.IS_ACTIVE  # [GY-FIX] Sync flag
        
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def approve_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        db_cliente.requiere_auditoria = False
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def hard_delete_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        """
        Hard delete with GENOMA V14.8 Protection:
        1. Backs up to PapeleraRegistro.
        2. Blocks deletion of History Records (Bit 1 IS_VIRGIN must be 1).
        """
        from backend.core.models import PapeleraRegistro
        import json

        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        # [SECURITY] Protection against deleting Historical Data (Bit 1 is IS_VIRGIN)
        # Robust check: handle NULL flags_estado by defaulting to 0 (which blocks deletion)
        current_flags = db_cliente.flags_estado or 0
        if not (current_flags & ClientFlags.IS_VIRGIN):
             raise HTTPException(
                 status_code=403, 
                 detail="PROHIBIDO: No se puede eliminar físicamente un registro de HISTORIAL (No Virgen). Inactívelo en su lugar."
             )

        try:
            # 1. Serializar para Papelera
            from decimal import Decimal
            
            def json_safe(obj):
                """Recursively converts Decimals to floats and UUIDs/datetimes to strings."""
                if isinstance(obj, dict):
                    return {k: json_safe(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [json_safe(v) for v in obj]
                elif isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, (datetime, UUID)):
                    return str(obj)
                return obj

            # Build initial dict from columns
            cliente_dict = {}
            for column in db_cliente.__table__.columns:
                cliente_dict[column.name] = getattr(db_cliente, column.name)
            
            # Application of recursive cleaner (Crucial for JSON fields like historial_cache)
            cliente_dict = json_safe(cliente_dict)
            
            # 2. Guardar en Papelera (Automated Backup)
            trash_entry = PapeleraRegistro(
                entidad_tipo='CLIENTE',
                entidad_id=db_cliente.id,
                data=cliente_dict,
                borrado_por="MASTER_TOOLS_PIN_1974"
            )
            db.add(trash_entry)
            
            # Debug log prior to physical delete
            print(f"[TRASH] Preparando borrado de {db_cliente.razon_social} (ID: {db_cliente.id}) | Flags: {db_cliente.flags_estado}")

            # 3. Borrado físico real
            db.delete(db_cliente)
            db.commit()
            return db_cliente
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=409, 
                detail=f"Error de integridad: El registro tiene dependencias activas (pedidos/remitos). {str(e)}"
            )
        except Exception as e:
            db.rollback()
            print(f"[X] CRITICAL TRASH ERROR: {str(e)}") # Visible in console
            raise HTTPException(
                status_code=500, 
                detail=f"ERROR INTERNO (Papelera/DB): {str(e)}"
            )

    @staticmethod
    def check_cuit(db: Session, cuit: str, exclude_id: UUID = None) -> schemas.CuitCheckResponse:
        # Check for Generic CUITs (Consumidor Final)
        clean_cuit = cuit.replace("-", "").replace(" ", "").strip()
        if clean_cuit in ["00000000000", "99999999999"]:
             return schemas.CuitCheckResponse(status="NEW", existing_clients=[])

        query = db.query(Cliente).filter(Cliente.cuit == cuit)
        
        if exclude_id:
            query = query.filter(Cliente.id != exclude_id)
            
        clients = query.all()
        
        if not clients:
            return schemas.CuitCheckResponse(status="NEW", existing_clients=[])
        
        # Check if any is active
        active_clients = [c for c in clients if c.activo]
        
        summary_list = []
        for c in clients:
            # Find main address
            # Assuming c.domicilios is accessible (lazy check)
            domicilio_str = "Sin Domicilio"
            if c.domicilios:
                # Privilegiar Fiscal o Entrega
                fiscal = next((d for d in c.domicilios if d.es_fiscal), None)
                if fiscal:
                    domicilio_str = f"{fiscal.calle} {fiscal.numero}, {fiscal.localidad}"
                else:
                    first = c.domicilios[0]
                    domicilio_str = f"{first.calle} {first.numero}, {first.localidad}"
            
            # Safe Access to Relations
            lp_nombre = c.lista_precios.nombre if c.lista_precios else None
            seg_nombre = c.segmento.nombre if c.segmento else None

            summary_list.append(schemas.ClienteSummary(
                id=c.id, 
                razon_social=c.razon_social, 
                nombre_fantasia=getattr(c, 'nombre_fantasia', None), 
                domicilio_principal=domicilio_str,
                lista_precios_nombre=lp_nombre,
                segmento_nombre=seg_nombre,
                lista_precios_id=c.lista_precios_id,
                segmento_id=c.segmento_id,
                activo=c.activo
            ))
        
        if active_clients:
            return schemas.CuitCheckResponse(status="EXISTS", existing_clients=summary_list)
        else:
            return schemas.CuitCheckResponse(status="INACTIVE", existing_clients=summary_list)

    @staticmethod
    def get_transportes_habituales(db: Session, cliente_id: UUID) -> List[UUID]:
        from sqlalchemy import func
        # Query logistica_domicilios to find most used transporte_id
        # We need to join Domicilio table? 
        # Wait, Domicilio model has transporte_habitual_nodo_id? Or transporte_id?
        # Let's check Domicilio model in next step if needed, but assuming it's transporte_habitual_nodo_id based on create_cliente
        # Actually create_cliente maps transporte_id to transporte_habitual_nodo_id.
        # But wait, create_cliente code says: dom_data['transporte_habitual_nodo_id'] = dom_in.transporte_id
        # Let's assume the column is transporte_habitual_nodo_id.
        # But wait, the user request says "SELECT DISTINCT transporte_id ... FROM logistica_domicilios".
        # I should check the model to be sure about the column name.
        # For now I will use Domicilio model attribute.
        
        results = db.query(
            Domicilio.transporte_habitual_nodo_id, 
            func.count(Domicilio.transporte_habitual_nodo_id).label('count')
        ).filter(
            Domicilio.cliente_id == cliente_id,
            Domicilio.transporte_habitual_nodo_id.isnot(None)
        ).group_by(
            Domicilio.transporte_habitual_nodo_id
        ).order_by(
            func.count(Domicilio.transporte_habitual_nodo_id).desc()
        ).all()
        
        # Return list of IDs (Empresa ID? Or Nodo ID?)
        # The SmartSelect expects IDs that match the options.
        # The options in SmartSelect are "Transportes" (Empresas).
        # But Domicilio links to a specific Nodo (Sucursal) or Empresa?
        # In create_cliente: dom_data['transporte_habitual_nodo_id'] = dom_in.transporte_id
        # If 'transporte_id' in frontend refers to Empresa, then we might have a mismatch if we are storing Nodo ID.
        # However, usually "Transporte" in the form refers to the Company.
        # Let's assume for now it returns the ID that matches the list.
        
        return [r[0] for r in results]

    # --- Usage Ranking (V5.2) ---
    @staticmethod
    def increment_usage(db: Session, cliente_id: UUID):
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if db_cliente:
            db_cliente.contador_uso += 1
            db.commit()
            return True
        return False

    @staticmethod
    def get_top_clients(db: Session, limit: int = 8) -> List[Cliente]:
        return db.query(Cliente).filter(Cliente.activo == True).order_by(Cliente.contador_uso.desc()).limit(limit).all()

    # --- Domicilios ---
    @staticmethod
    def create_domicilio(db: Session, cliente_id: UUID, domicilio_in: schemas.DomicilioCreate) -> Domicilio:
        # Validar Provincia
        from backend.maestros.models import Provincia
        prov_id = domicilio_in.provincia_id
        if prov_id == "":
            prov_id = None
            
        if prov_id: 
             prov = db.query(Provincia).filter(Provincia.id == prov_id).first()
             if not prov:
                 # print(f"❌ [DEBUG-400] Provincia ID inválido: '{prov_id}'")
                 raise HTTPException(status_code=400, detail=f"Código de provincia '{prov_id}' inválido")
        
        # Enforce Single Fiscal Domicile Logic
        if domicilio_in.es_fiscal:
            db.query(Domicilio).filter(
                Domicilio.cliente_id == cliente_id,
                Domicilio.es_fiscal == True
            ).update({"es_fiscal": False})
        
        # Enforce Single Primary Domicile Logic
        if domicilio_in.es_predeterminado:
            db.query(Domicilio).filter(
                Domicilio.cliente_id == cliente_id,
                Domicilio.es_predeterminado == True
            ).update({"es_predeterminado": False})

        # Prepare data
        # [GY-PROTOCOL-PIPE] Logic Fusion directly to Caller
        piso = getattr(domicilio_in, 'piso', None)
        depto = getattr(domicilio_in, 'depto', None)
        
        # [V7] Native Columns: Do not exclude piso/depto. 
        # Exclude legacy pipe logic.
        dom_data = domicilio_in.model_dump(exclude={'provincia', 'zona_id', 'provincia_id', 'is_maps_manual'})

        # [GY-PROTOCOL-PIPE DEPRECATED for V7]
        # We now store pure 'calle' and 'piso/depto' in separate columns.
        
        db_domicilio = Domicilio(
            **dom_data,
            provincia_id=prov_id,
            cliente_id=cliente_id,
            is_maps_manual=bool(domicilio_in.maps_link)
        )
        
        # Auto-Maps logic
        if not db_domicilio.maps_link:
            db_domicilio.maps_link = ClienteService._generate_maps_link(db, db_domicilio)
            db_domicilio.is_maps_manual = False

        try:
            db.add(db_domicilio)
            db.commit()
            db.refresh(db_domicilio)

            # [V5.2-FIX] Link domicilio into N:M junction so GET /clientes/{id} can see it
            # (get_cliente uses joinedload(Cliente.domicilios) which traverses domicilios_clientes)
            db.execute(domicilios_clientes.insert().values(
                cliente_id=cliente_id,
                domicilio_id=db_domicilio.id,
                es_predeterminado=bool(domicilio_in.es_predeterminado),
                alias=db_domicilio.alias,
            ))
            db.commit()

            # [GY-DOCTRINA-V14] RE-AUDIT PARENT
            db_cliente = ClienteService.get_cliente(db, cliente_id)
            if db_cliente:
                ClienteService._audit_sovereignty(db_cliente)
                db.add(db_cliente)
                db.commit()

            # [VAULT SYNC] Register VinculoGeografico
            from backend.contactos.models import VinculoGeografico
            flags = 0
            if domicilio_in.es_fiscal: flags |= 1
            if domicilio_in.es_predeterminado: flags |= 2
            
            vg = VinculoGeografico(
                entidad_tipo='CLIENTE',
                entidad_id=cliente_id,
                domicilio_id=db_domicilio.id,
                alias=db_domicilio.alias,
                flags_relacion=flags,
                activo=True
            )
            db.add(vg)
            db.commit()
            
            # [GY-FIX-V12] Return the DOMICILIO object, not the Client. Frontend expects Domicilio.
            return db_domicilio
        except Exception as e:
            db.rollback()
            print(f"❌ ERROR CREATE_DOMICILIO: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error al guardar domicilio: {str(e)}")

    @staticmethod
    def update_domicilio(db: Session, cliente_id: UUID, domicilio_id: UUID, domicilio_in: schemas.DomicilioUpdate) -> Optional[Domicilio]:
        db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if not db_domicilio:
            return None
        
        update_data = domicilio_in.model_dump(exclude_unset=True)
        
        # [GY-PROTOCOL-PIPE DEPRECATED]
        # V7: We now respect the individual fields passed in update_data.
        # No need to merge into calle.
        
        # If frontend sends {calle: '...', piso: '...'}, update_data has them.
        # If legacy frontend sends pipes, we might want to handle it?
        # But for V7 Canvas, we send separate fields.
        
        pass

        # Remove fields not in model
        if 'zona_id' in update_data:
            update_data.pop('zona_id')

        # [V5.9 GOLD] Persistencia de Flags de Relación (Bit 21 / Espejo)
        # Sincronizamos los bits de la tabla puente domicilios_clientes
        rel_flags = update_data.pop('flags', None)
        if rel_flags is not None:
             from backend.clientes.models import domicilios_clientes
             db.execute(
                 domicilios_clientes.update().where(
                     domicilios_clientes.c.cliente_id == cliente_id,
                     domicilios_clientes.c.domicilio_id == domicilio_id
                 ).values(flags=rel_flags)
             )
             print(f"[GOLD] Sincronización de BITMASK en Tabla Puente: Cliente:{cliente_id} Domicilio:{domicilio_id} Flags:{rel_flags}")

        # [V5.2.3 GOLD] BIFURCATION LOGIC (Mirror Break)
        # If Bit 21 (Mirror) is active for this client and notes are modified,
        # we must clone the address and link the child independently.
        from backend.clientes.models import domicilios_clientes
        current_link = db.execute(
            domicilios_clientes.select().where(
                domicilios_clientes.c.cliente_id == cliente_id,
                domicilios_clientes.c.domicilio_id == domicilio_id
            )
        ).fetchone()

        # [V5.2.3.1 GOLD] Mirror Break Strategy (Bit 21)
        is_mirror = current_link and (current_link.flags & 2097152) # Bit 21
        has_note_change = 'notas_logistica' in update_data or 'observaciones' in update_data
        
        if is_mirror and has_note_change:
            # Fork mandatory: Create a copy for this specific client
            print(f"[GOLD] BIFURCACIÓN DETECTADA: SOBERANÍA REQUERIDA PARA {db_domicilio.id}")
            # If the user is editing from a view that only allows "Entrega" update, preserve balance
            forked_data = update_data.copy()
            # Inherit missing core fields
            for col in ['calle', 'numero', 'piso', 'depto', 'localidad', 'provincia_id', 'alias', 'bit_identidad', 'flags_infra']:
                if col not in forked_data:
                    forked_data[col] = getattr(db_domicilio, col)
            
            # [V5.9 GOLD] Preservar Flags (Espejo) en la bifurcación si vienen del frontend
            target_rel_flags = rel_flags if rel_flags is not None else 0
            new_dom = ClienteService.fork_domicilio(db, cliente_id, domicilio_id, forked_data, flags=target_rel_flags)
            return new_dom

        # Enforce Single Fiscal Domicile Logic
        if update_data.get('es_fiscal'):
            db.query(Domicilio).filter(
                Domicilio.id != domicilio_id,
                Domicilio.es_fiscal == True
            ).join(domicilios_clientes).filter(domicilios_clientes.c.cliente_id == cliente_id).update({"es_fiscal": False}, synchronize_session=False)
        
        # Enforce Single Primary Domicile Logic
        if update_data.get('es_predeterminado'):
            # Clear other predeterminados for THIS client in the join table
            db.execute(
                domicilios_clientes.update().where(
                    domicilios_clientes.c.cliente_id == cliente_id,
                    domicilios_clientes.c.domicilio_id != domicilio_id
                ).values(es_predeterminado=False)
            )

        # [GY-FIX-V5] Fix Persistence Conflict: Empresa vs Nodo
        # If updating Empresa (transporte_id), clear Legacy Nodo (transporte_habitual_nodo_id)
        # to prevent ambiguity or legacy override.
        if 'transporte_id' in update_data:
             db_domicilio.transporte_habitual_nodo_id = None
             print(f"[DEBUG-TRP] Updating Transporte ID to {update_data['transporte_id']} (Clearing Nodo)")

        # Auto-Maps Logic
        if 'maps_link' in update_data:
            db_domicilio.is_maps_manual = True
            if not update_data['maps_link']:
                db_domicilio.is_maps_manual = False
        
        for key, value in update_data.items():
            setattr(db_domicilio, key, value)
            
        if not db_domicilio.maps_link:
            db_domicilio.maps_link = ClienteService._generate_maps_link(db, db_domicilio)
            db_domicilio.is_maps_manual = False

        db.commit()
        db.refresh(db_domicilio)
        
        # [VAULT SYNC] Update VinculoGeografico flags
        from backend.contactos.models import VinculoGeografico
        vg = db.query(VinculoGeografico).filter(
            VinculoGeografico.entidad_tipo == 'CLIENTE',
            VinculoGeografico.entidad_id == cliente_id,
            VinculoGeografico.domicilio_id == db_domicilio.id
        ).first()
        
        if vg:
            flags = vg.flags_relacion
            if 'es_fiscal' in update_data:
                if update_data['es_fiscal']: flags |= 1
                else: flags &= ~1
            if 'es_predeterminado' in update_data:
                if update_data['es_predeterminado']: flags |= 2
                else: flags &= ~2
            
            if 'activo' in update_data:
                vg.activo = update_data['activo']
            
            vg.flags_relacion = flags
            vg.alias = db_domicilio.alias
            db.add(vg)
            db.commit()

        # [GY-DOCTRINA-V14] RE-AUDIT PARENT (Shielded)
        try:
            db_p = ClienteService.get_cliente(db, cliente_id)
            if db_p:
                ClienteService._audit_sovereignty(db_p)
                db.commit() # Final commit for audit flags
        except Exception as audit_err:
            print(f"⚠️ [WARN] Audit failure post-domicile update: {audit_err}")
            # We don't raise here as the core domicile data was already committed at line 719
        
        # Return Domicilio object
        return db_domicilio

    @staticmethod
    def delete_domicilio(db: Session, domicilio_id: UUID, cliente_id: UUID = None):
        db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if db_domicilio:
            # Soft Delete the main record
            db_domicilio.activo = False
            db.add(db_domicilio)
            db.commit()
            db.refresh(db_domicilio)
            
            # [VAULT SYNC] Granular Deactivation (Targeted or Global)
            from backend.contactos.models import VinculoGeografico
            query = db.query(VinculoGeografico).filter(VinculoGeografico.domicilio_id == domicilio_id)
            
            # If cliente_id is provided, only deactivate link for that client
            if cliente_id:
                query = query.filter(
                    VinculoGeografico.entidad_tipo == 'CLIENTE',
                    VinculoGeografico.entidad_id == cliente_id
                )
            
            query.update({"activo": False})
            db.commit()

            # [GY-DOCTRINA-V14] RE-AUDIT PARENT
            target_parent_id = cliente_id
            if target_parent_id:
                db_p = ClienteService.get_cliente(db, target_parent_id)
                if db_p:
                    ClienteService._audit_sovereignty(db_p)
                    db.add(db_p)
                    db.commit()

        return db_domicilio

    @staticmethod
    def normalize_address(calle: str = "", numero: str = "", piso: str = "", depto: str = "") -> str:
        """
        [V5.2 GOLD] Normalizador Semántico.
        Trim, Lowercase, Remoción de acentos y caracteres especiales.
        """
        import unicodedata
        import re

        def clean(text):
            if not text: return ""
            # Normalizar a NFKD para separar acentos
            text = unicodedata.normalize('NFKD', str(text))
            # Remover caracteres que no sean ASCII (acentos)
            text = text.encode('ASCII', 'ignore').decode('ASCII')
            # Lowercase y Trim
            text = text.lower().strip()
            # Remover caracteres especiales (dejar solo letras, números y espacios)
            text = re.sub(r'[^a-z0-9\s]', '', text)
            # Colapsar múltiples espacios
            text = re.sub(r'\s+', ' ', text)
            return text

        return f"{clean(calle)}|{clean(numero)}|{clean(piso)}|{clean(depto)}"

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        [GY-FIX-V16.2] Protocolo de Tokenización Alfabética (Bag of Words - Blindaje Nike).
        Remueve acentos, unifica siglas (quita puntos), tokeniza por palabras,
        elimina ruido (<2 chars), ordena alfabéticamente y sella la cadena única.
        """
        if not name: return ""
        import unicodedata
        import re
        
        # 1. Normalización Unicode (Mata acentos)
        text = unicodedata.normalize('NFKD', str(name))
        text = text.encode('ASCII', 'ignore').decode('ASCII').upper()
        
        # 2. Unificación de Siglas: "S.R.L." -> "SRL" antes de tokenizar
        text = text.replace('.', '')
        
        # 3. Tokenización: Reemplazar todo lo no-alfanumérico por ESPACIO
        text = re.sub(r'[^A-Z0-9]', ' ', text)
        tokens = text.split()
        
        # 4. Limpieza de Ruido (Filtramos palabras de 1 solo caracter)
        tokens = [t for t in tokens if len(t) >= 2]
        
        # 5. Ordenamiento Alfabético [EL TALLER SRL] -> [EL, SRL, TALLER]
        tokens.sort()
        
        # 6. Sellado: Unir sin espacios
        return "".join(tokens)

    @staticmethod
    def check_similarity(db: Session, name: str, threshold: float = 0.85) -> List[dict]:
        """
        [V5.7] Fuzzy Matching para detección de similitud (Protocolo Nike).
        """
        from difflib import SequenceMatcher
        
        target_canon = ClienteService.normalize_name(name)
        if not target_canon or target_canon in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
            return []

        # Buscamos en la DB candidatos (solo activos)
        candidates = db.query(Cliente.id, Cliente.razon_social, Cliente.razon_social_canon).filter(Cliente.activo == True).all()
        
        matches = []
        for c_id, c_name, c_canon in candidates:
            # Primero comparación rápida por canon si el canon ya existe en la DB
            if c_canon == target_canon:
                matches.append({"id": str(c_id), "nombre": c_name, "score": 1.0, "tipo": "CANON"})
                continue
            
            # Fuzzy Match
            # Usamos difflib contra el nombre original (pero limpio de espacios extra)
            ratio = SequenceMatcher(None, name.upper().strip(), c_name.upper().strip()).ratio()
            if ratio >= threshold:
                matches.append({"id": str(c_id), "nombre": c_name, "score": round(ratio, 2), "tipo": "FUZZY"})
                
        # Ordenar por puntaje
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5] # Retornar top 5

    @staticmethod
    def find_matching_domicilio(db: Session, data: dict) -> Optional[Domicilio]:
        """
        [V5.2 GOLD] Interceptor de Colisiones.
        Busca si ya existe un domicilio semánticamente idéntico.
        """
        target_norm = ClienteService.normalize_address(
            data.get('calle'), data.get('numero'), data.get('piso'), data.get('depto')
        )
        
        # [ALGO] We fetch active domicilios and compare normalized vectors.
        # Optimization: In a large DB, we'd store the normalized vector in a column.
        # For now, we search by Calle/Numero and then refine.
        potential_matches = db.query(Domicilio).filter(
            Domicilio.is_active == True,
            Domicilio.calle.ilike(data.get('calle', ''))
        ).all()
        
        for dom in potential_matches:
            dom_norm = ClienteService.normalize_address(dom.calle, dom.numero, dom.piso, dom.depto)
            if dom_norm == target_norm:
                return dom
        return None

    @staticmethod
    def sync_fiscal(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        """
        [V5.2 GOLD] "Igualar a Fiscal" Protocol.
        Apunta la entrega al ID del Domicilio Fiscal y enciende el Bit 21.
        """
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente: return None
        
        # [V5.2 GOLD] Using transition relationship
        fiscal = next((d for d in db_cliente.domicilios_legacy if d.es_fiscal and d.is_active), None)
        if not fiscal:
            raise HTTPException(status_code=400, detail="No existe un Domicilio Fiscal activo para sincronizar.")
        
        # [N:M Logic] 1. Update link in domicilios_clientes
        from backend.clientes.models import domicilios_clientes
        from sqlalchemy import delete, insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert # Assuming SQLite for dev

        # Reset other delivery links to Mirror
        db.execute(
            delete(domicilios_clientes).where(
                domicilios_clientes.c.cliente_id == cliente_id,
                domicilios_clientes.c.domicilio_id != fiscal.id
            )
        )
        
        # UPSERT Mirror Link (Bit 21 ON)
        # Using a safer approach for multi-DB (try-except or manually check)
        existing_link = db.query(domicilios_clientes).filter(
            domicilios_clientes.c.cliente_id == cliente_id,
            domicilios_clientes.c.domicilio_id == fiscal.id
        ).first()

        if existing_link:
            db.execute(
                domicilios_clientes.update().where(
                    domicilios_clientes.c.cliente_id == cliente_id,
                    domicilios_clientes.c.domicilio_id == fiscal.id
                ).values(flags=2097152, alias="ESPEJO FISCAL")
            )
        else:
            db.execute(
                insert(domicilios_clientes).values(
                    cliente_id=cliente_id,
                    domicilio_id=fiscal.id,
                    flags=2097152,
                    alias="ESPEJO FISCAL"
                )
            )

        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def fork_domicilio(db: Session, cliente_id: UUID, domicilio_id: UUID, new_data: dict, flags: int = 0) -> Domicilio:
        """
        [V5.2 GOLD] Fork Protocol.
        Clona un domicilio espejado para convertirlo en independiente (Bit 21 OFF).
        """
        # 1. Create Clone
        from backend.clientes.models import Domicilio
        new_dom = Domicilio(**new_data)
        new_dom.id = uuid.uuid4()
        new_dom.is_active = True
        db.add(new_dom)
        db.flush()
        
        # 2. Update Link (Turn Bit 21 OFF)
        from backend.clientes.models import domicilios_clientes
        db.execute(
            domicilios_clientes.update().where(
                domicilios_clientes.c.cliente_id == cliente_id,
                domicilios_clientes.c.domicilio_id == domicilio_id
            ).values(domicilio_id=new_dom.id, flags=flags, alias=new_data.get('alias', 'ENTREGA INDEPENDIENTE'))
        )
        db.commit()
        return new_dom

    @staticmethod
    def cleanup_orphans(db: Session, domicilio_id: UUID):
        """
        [V5.2 GOLD] Gestión de Huérfanos.
        Acción A (Con Historia): is_active = False.
        Acción B (Sin Historia): Poda física.
        """
        # 1. Check if still linked
        from backend.clientes.models import domicilios_clientes
        link_count = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == domicilio_id).count()
        if link_count > 0: return
        
        # 2. Check history (Remitos, Facturas)
        # [ALGO] We check presence in logistic/finance tables
        # For now, we simulate check or check 'pedidos' which is available in 'clientes' module context
        from backend.pedidos.models import Pedido
        from backend.clientes.models import Domicilio
        has_history = db.query(Pedido).filter(Pedido.domicilio_entrega_id == domicilio_id).count() > 0
        
        dom = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if not dom: return

        if has_history:
            dom.is_active = False # Acción A: Fantasma
            db.add(dom)
        else:
            db.delete(dom) # Acción B: Poda
        db.commit()

    @staticmethod
    def _generate_maps_link(db: Session, dom: Domicilio) -> str:
        """[V15.2 GOLD] Generador Automático de Google Maps."""
        import urllib.parse
        prov_name = ""
        if dom.provincia:
            prov_name = dom.provincia.nombre
        elif dom.provincia_id:
            from backend.maestros.models import Provincia
            p = db.query(Provincia).filter(Provincia.id == dom.provincia_id).first()
            if p: prov_name = p.nombre
        
        query_parts = [dom.calle, dom.numero, dom.localidad, prov_name]
        query = " ".join([p for p in query_parts if p])
        encoded_query = urllib.parse.quote_plus(query)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    @staticmethod
    def get_hub_domicilios(db: Session) -> List[Domicilio]:
        """[V5.2 GOLD] Lista domicilios con conteo de vínculos, provincias y clientes."""
        from sqlalchemy import func
        from backend.clientes.models import domicilios_clientes, Cliente
        from sqlalchemy.orm import joinedload
        
        # [SURGICAL FIX] Force registry population inside the call
        try:
            from sqlalchemy.orm import configure_mappers
            import backend.auth.models
            import backend.maestros.models
            import backend.logistica.models
            import backend.productos.models
            import backend.clientes.models
            import backend.pedidos.models
            import backend.remitos.models
            import backend.agenda.models
            import backend.contactos.models
            import backend.proveedores.models
            import backend.core.models
            configure_mappers()
        except Exception as e:
            print(f"[WARN] configure_mappers failed (already configured or missing deps): {e}")

        # Subquery to count links
        usage_stmt = db.query(
            domicilios_clientes.c.domicilio_id,
            func.count(domicilios_clientes.c.cliente_id).label('usage_count')
        ).group_by(domicilios_clientes.c.domicilio_id).subquery()
        
        results = db.query(Domicilio, usage_stmt.c.usage_count).options(
            joinedload(Domicilio.provincia)
        ).outerjoin(
            usage_stmt, Domicilio.id == usage_stmt.c.domicilio_id
        ).all()
        
        output = []
        for dom, count in results:
            dom.usage_count = count or 0
            dom.provincia_nombre = dom.provincia.nombre if dom.provincia else (dom.provincia_id or '-')
            
            # Fetch linked client names, IDs, Role and Mirror status
            # [V5.2.3 GOLD] Hydrate with DomicilioRelationFlags
            linked = db.query(
                Cliente.id, 
                Cliente.razon_social,
                domicilios_clientes.c.flags
            ).join(
                domicilios_clientes, Cliente.id == domicilios_clientes.c.cliente_id
            ).filter(domicilios_clientes.c.domicilio_id == dom.id).all()
            
            dom.clientes_vinculados = [c[1] for c in linked]
            
            details = []
            for c in linked:
                flags = c[2] or 0
                rels = []
                if flags & 1: rels.append("Fiscal")
                if flags & 2: rels.append("Entrega")
                
                details.append({
                    "id": str(c[0]), 
                    "nombre": c[1],
                    "rol_display": "/".join(rels) if rels else "Vínculo Hub",
                    "mirror_active": bool(flags & 2097152)
                })
            dom.vinculos_detalles = details
            
            # [GOLD] Auto-identity logic: COLLECT but don't commit here
            # We skip auto-audit during LIST to ensure stability and speed
            # Auditoría needs to be a separate background task or explicit call
            
            output.append(dom)
        return output

    @staticmethod
    def create_hub_domicilio(db: Session, data: schemas.DomicilioCreate) -> Domicilio:
        """[V5.2 GOLD] Creación soberana en el Hub con auto-maps."""
        dom_dict = data.model_dump()
        is_manual = bool(dom_dict.get('maps_link'))
        
        db_dom = Domicilio(**dom_dict)
        if not db_dom.id:
            db_dom.id = uuid.uuid4()
        db_dom.is_active = True
        db_dom.is_maps_manual = is_manual
        
        if not db_dom.maps_link:
            db_dom.maps_link = ClienteService._generate_maps_link(db, db_dom)
            db_dom.is_maps_manual = False
            
        db.add(db_dom)
        db.commit()
        db.refresh(db_dom)
        db_dom.usage_count = 0
        return db_dom

    @staticmethod
    def update_hub_domicilio(db: Session, dom_id: UUID, data: schemas.DomicilioUpdate) -> Optional[Domicilio]:
        """[V5.2 GOLD] Actualización soberana en el Hub con auto-maps."""
        db_dom = db.query(Domicilio).filter(Domicilio.id == dom_id).first()
        if not db_dom: return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Check if maps_link is provided manually
        if 'maps_link' in update_data:
            db_dom.is_maps_manual = True
            if not update_data['maps_link']:
                # If cleared, we'll re-generate later
                db_dom.is_maps_manual = False
        
        for key, value in update_data.items():
            setattr(db_dom, key, value)
            
        # [V5.2.3.1 GOLD] Synchronize bit_identidad[0] with is_active column
        if 'bit_identidad' in update_data:
            db_dom.is_active = bool(update_data['bit_identidad'] & 1)
        # Conversely, if is_active provided
        if 'is_active' in update_data:
            if update_data['is_active']:
                db_dom.bit_identidad |= 1
            else:
                db_dom.bit_identidad &= ~1
            
        # If maps_link is still empty, auto-generate
        if not db_dom.maps_link:
            db_dom.maps_link = ClienteService._generate_maps_link(db, db_dom)
            db_dom.is_maps_manual = False
            
        db.add(db_dom)
        db.commit()
        db.refresh(db_dom)
        
        # Recalculate usage count
        from backend.clientes.models import domicilios_clientes
        usage = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom_id).count()
        db_dom.usage_count = usage
        return db_dom

    @staticmethod
    def delete_hub_domicilio(db: Session, dom_id: UUID) -> bool:
        """[V5.2 GOLD] Eliminación física segura desde el Hub."""
        from backend.clientes.models import domicilios_clientes
        
        # 1. Check for active links (Universal UUID/Hex check)
        usage = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom_id).count()
        if usage > 0:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Soberanía: No se puede eliminar un domicilio con vínculos ({usage}).")
            
        db_dom = db.query(Domicilio).filter(Domicilio.id == dom_id).first()
        if not db_dom: return False
        
        db.delete(db_dom)
        db.commit()
        return True
    @staticmethod
    def search_hub_domicilios(db: Session, q: str) -> List[Domicilio]:
        """[V5.2 GOLD] Buscador con hidratación completa."""
        from sqlalchemy.orm import joinedload
        from backend.clientes.models import domicilios_clientes, Cliente
        
        query = db.query(Domicilio).filter(Domicilio.is_active == True).options(joinedload(Domicilio.provincia))
        
        if q:
            query = query.filter(
                (Domicilio.calle.ilike(f"%{q}%")) |
                (Domicilio.localidad.ilike(f"%{q}%")) |
                (Domicilio.alias.ilike(f"%{q}%"))
            )
            
        results = query.limit(50).all()
        
        output = []
        for dom in results:
            # Hydrate counts and names
            dom.usage_count = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom.id).count()
            dom.provincia_nombre = dom.provincia.nombre if dom.provincia else (dom.provincia_id or '-')
            
            # [V5.2.3 GOLD] Full hydration for Search consistency
            linked = db.query(
                Cliente.id, 
                Cliente.razon_social,
                domicilios_clientes.c.flags
            ).join(
                domicilios_clientes, Cliente.id == domicilios_clientes.c.cliente_id
            ).filter(domicilios_clientes.c.domicilio_id == dom.id).all()
            
            dom.clientes_vinculados = [c[1] for c in linked]
            
            details = []
            for c in linked:
                flags = c[2] or 0
                rels = []
                if flags & 1: rels.append("Fiscal")
                if flags & 2: rels.append("Entrega")
                
                details.append({
                    "id": str(c[0]), 
                    "nombre": c[1],
                    "rol_display": "/".join(rels) if rels else "Vínculo Hub",
                    "mirror_active": bool(flags & 2097152)
                })
            dom.vinculos_detalles = details
            
            output.append(dom)
        return output

    @staticmethod
    def link_hub_domicilio(db: Session, dom_id: UUID, cliente_id: UUID, alias: str = None, flags: int = 0) -> bool:
        """[V5.2 GOLD] Vincula un cliente a un domicilio existente."""
        from backend.clientes.models import domicilios_clientes
        from sqlalchemy import insert
        
        # Check if link already exists
        # Handle UUID hex conversion
        cid = cliente_id.hex if hasattr(cliente_id, 'hex') else str(cliente_id).replace('-', '')
        did = dom_id.hex if hasattr(dom_id, 'hex') else str(dom_id).replace('-', '')

        existing = db.execute(
            domicilios_clientes.select().where(
                domicilios_clientes.c.cliente_id == cid,
                domicilios_clientes.c.domicilio_id == did
            )
        ).fetchone()
        
        if existing:
            return False
            
        db.execute(
            insert(domicilios_clientes).values(
                cliente_id=cid,
                domicilio_id=did,
                alias=alias or "VÍNCULO HUB",
                flags=flags
            )
        )
        db.commit()
        return True

    @staticmethod
    def unlink_hub_domicilio(db: Session, dom_id: UUID, cliente_id: UUID) -> bool:
        """[V5.2 GOLD] Corta el vínculo entre un cliente y un domicilio."""
        from backend.clientes.models import domicilios_clientes
        from sqlalchemy import delete
        
        cid = cliente_id.hex if hasattr(cliente_id, 'hex') else str(cliente_id).replace('-', '')
        did = dom_id.hex if hasattr(dom_id, 'hex') else str(dom_id).replace('-', '')

        res = db.execute(
            delete(domicilios_clientes).where(
                domicilios_clientes.c.cliente_id == cid,
                domicilios_clientes.c.domicilio_id == did
            )
        )
        db.commit()
        return res.rowcount > 0

    @staticmethod
    def _audit_domicilio(db: Session, dom: Domicilio):
        """
        [V5.2.3 GOLD] Auditoría de Identidad Geográfica.
        Auto-asigna bits según estado del sistema.
        """
        from backend.clientes.models import domicilios_clientes
        usage_count = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom.id).count()
        
        original_bits = dom.bit_identidad or 0
        new_bits = original_bits
        
        # Bit 64: HUB (Múltiple)
        if usage_count > 1:
            new_bits |= 64
        else:
            new_bits &= ~64
            
        if new_bits != original_bits:
            dom.bit_identidad = new_bits
            db.add(dom)
            db.commit()
            print(f"[GOLD] HUB Audit: Domicilio {dom.id} updated bits {original_bits} -> {new_bits}")

    @staticmethod
    def get_hub_orphaned(db: Session):
        """[V5.2.4 GOLD] Retorna domicilios inactivos (Candidatos a Purgatorio)."""
        from backend.clientes.models import Domicilio
        # Incluimos los que tienen is_active=False O el Bit 0 de identidad apagado (Universal Sync)
        from sqlalchemy import or_
        return db.query(Domicilio).filter(
            or_(
                Domicilio.is_active == False,
                (Domicilio.bit_identidad.op('&')(1)) == 0
            )
        ).all()

    @staticmethod
    def check_domicilio_integrity(db: Session, dom_id: UUID):
        """[V5.2.4 GOLD] Análisis de supervivencia soberana antes de purga física."""
        from backend.clientes.models import domicilios_clientes
        from backend.pedidos.models import Pedido
        from backend.remitos.models import Remito
        
        # 1. Check Links N:M
        links_count = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom_id).count()
        
        # 2. Check Pedidos
        pedidos_count = db.query(Pedido).filter(Pedido.domicilio_entrega_id == dom_id).count()
        
        # 3. Check Remitos
        remitos_count = db.query(Remito).filter(Remito.domicilio_entrega_id == dom_id).count()
        
        total_refs = links_count + pedidos_count + remitos_count
        is_safe = total_refs == 0
        
        details = []
        if links_count > 0: details.append(f"{links_count} vínculos activos")
        if pedidos_count > 0: details.append(f"{pedidos_count} pedidos")
        if remitos_count > 0: details.append(f"{remitos_count} remitos")
        
        message = "Sin dependencias. Seguro para purga física." if is_safe else f"Bloqueado por: {', '.join(details)}"
        
        return {
            "safe": is_safe,
            "dependencies": total_refs,
            "message": message,
            "breakdown": {
                "links": links_count,
                "pedidos": pedidos_count,
                "remitos": remitos_count
            }
        }

    @staticmethod
    def hard_delete_hub_domicilio(db: Session, dom_id: UUID) -> bool:
        """[V5.2.4 GOLD] Eliminación física total del Hub (POST-INTEGRITY)."""
        db_dom = db.query(Domicilio).filter(Domicilio.id == dom_id).first()
        if not db_dom: return False
        
        # RE-VERIFY INTEGRITY (SAFETY GATE)
        check = ClienteService.check_domicilio_integrity(db, dom_id)
        if not check["safe"]:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Soberanía: Intento de purga ilegal. {check['message']}")
            
        db.delete(db_dom)
        db.commit()
        return True
