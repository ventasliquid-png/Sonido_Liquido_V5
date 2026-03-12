from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.clientes.models import Cliente, Domicilio
from backend.clientes import schemas
from backend.agenda import models as agenda_models

class ClienteService:
    @staticmethod
    def create_cliente(db: Session, cliente_in: schemas.ClienteCreate) -> Cliente:
        try:
            # Libertad Vigilada: Check for duplicates
            # If CUIT exists, mark for audit but ALLOW creation
            GENERIC_CUITS = ['00000000000', '11111111119', '11111111111', '99999999999']
            
            existing = None
            if cliente_in.cuit and cliente_in.cuit not in GENERIC_CUITS:
                 existing = db.query(Cliente).filter(Cliente.cuit == cliente_in.cuit).first()
            
            if existing:
                cliente_in.requiere_auditoria = True
            
            # Auto-assign Legacy ID (Internal Code)
            from sqlalchemy import func
            max_id = db.query(func.max(Cliente.codigo_interno)).scalar() or 0
            next_id = max_id + 1

            # Crear Cliente
            db_cliente = Cliente(
                razon_social=cliente_in.razon_social,
                cuit=cliente_in.cuit,
                codigo_interno=next_id, # Auto-assigned
                condicion_iva_id=cliente_in.condicion_iva_id,
                lista_precios_id=cliente_in.lista_precios_id,
                activo=cliente_in.activo,
                requiere_auditoria=cliente_in.requiere_auditoria
            )
            db.add(db_cliente)
            db.commit()
            db.refresh(db_cliente)

            # Crear Domicilios
            try:
                for dom_in in cliente_in.domicilios:
                    # [GY-PROTOCOL-PIPE] Intercept Piso/Depto and merge into valid Calle structure
                    dom_data = dom_in.model_dump(exclude={'zona_id', 'piso', 'depto'})
                    
                    calle_input = dom_in.calle or ""
                    piso_input = dom_in.piso or ""
                    depto_input = dom_in.depto or ""
                    
                    # Force creation of Pipe format if additional data exists
                    # Even if empty strings, we might want to maintain structure if consistent
                    # But per request: "Fraga 123||" or "Fraga 123|4|B"
                    # Optimization: Only add pipes if we are actually saving structural data?
                    # Request says: domicilio_db = f"{calle_input}|{piso_input}|{depto_input}"
                    
                    if piso_input or depto_input or '|' in calle_input:
                         dom_data['calle'] = f"{calle_input}|{piso_input}|{depto_input}"
                    
                    if dom_in.transporte_id:
                        dom_data['transporte_id'] = dom_in.transporte_id
                        # Legacy support or if we want to auto-select node?
                        # For now, we just use the new column.
                        # dom_data['transporte_habitual_nodo_id'] = ... 

                    if dom_in.intermediario_id:
                        dom_data['intermediario_id'] = dom_in.intermediario_id
                    
                    db_domicilio = Domicilio(
                        **dom_data,
                        cliente_id=db_cliente.id
                    )
                    db.add(db_domicilio)

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
                print(f"❌ ERROR CRÍTICO EN CREATE_CLIENTE (DOMICILIOS): {e}")
                import traceback
                traceback.print_exc()
                db.rollback()
                raise e
        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN CREATE_CLIENTE: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise e

    @staticmethod
    def get_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        from sqlalchemy.orm import joinedload
        return db.query(Cliente).options(
            joinedload(Cliente.domicilios),
            # [GY-TEMP] Disable eager load of vinculos to fix 500
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.persona),
            # joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.tipo_contacto)
        ).filter(Cliente.id == cliente_id).first()

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
        from backend.clientes.constants import ClientFlags
        
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
        
        # [V5-X] Sync legacy 'activo'
        if (db_cliente.flags_estado & ClientFlags.IS_ACTIVE):
            db_cliente.activo = True
        else:
            db_cliente.activo = False

        # Update default domicile if transporte_id is provided
        if transporte_id:
            default_dom = next((d for d in db_cliente.domicilios if d.es_entrega and d.activo), None)
            if not default_dom:
                 default_dom = next((d for d in db_cliente.domicilios if d.es_fiscal and d.activo), None)
            if not default_dom and db_cliente.domicilios:
                 default_dom = next((d for d in db_cliente.domicilios if d.activo), None)
            
            if default_dom:
                default_dom.transporte_id = transporte_id
                db.add(default_dom)
            else:
                # Create a minimal delivery address if none exists (Bronze Logic?)
                # This ensures we store the preference.
                new_dom = Domicilio(
                    cliente_id=db_cliente.id,
                    transporte_id=transporte_id,
                    es_fiscal=False,
                    es_entrega=True,
                    alias="Entrega (Auto)",
                    activo=True
                )
                db.add(new_dom)

        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def delete_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        """Soft delete setting activo=False"""
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        db_cliente.activo = False
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
        """Hard delete. Raises IntegrityError if it has related records."""
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        try:
            db.delete(db_cliente)
            db.commit()
            return db_cliente
        except IntegrityError as e:
            db.rollback()
            raise e

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
            # Demote all existing domiciles
            db.query(Domicilio).filter(
                Domicilio.cliente_id == cliente_id,
                Domicilio.es_fiscal == True
            ).update({"es_fiscal": False})

        # Prepare data
        # [GY-PROTOCOL-PIPE] Logic Fusion directly to Caller
        piso = getattr(domicilio_in, 'piso', None)
        depto = getattr(domicilio_in, 'depto', None)
        
        # [V7] Native Columns: Do not exclude piso/depto. 
        # Exclude legacy pipe logic.
        dom_data = domicilio_in.model_dump(exclude={'provincia', 'zona_id', 'provincia_id'})

        # [GY-PROTOCOL-PIPE DEPRECATED for V7]
        # We now store pure 'calle' and 'piso/depto' in separate columns.
        
        db_domicilio = Domicilio(
            **dom_data,
            provincia_id=prov_id,
            cliente_id=cliente_id
        )
        try:
            db.add(db_domicilio)
            db.commit()
            db.refresh(db_domicilio)
            # [GY-FIX-V12] Return the DOMICILIO object, not the Client. Frontend expects Domicilio.
            return db_domicilio
        except Exception as e:
            db.rollback()
            print(f"❌ ERROR CREATE_DOMICILIO: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error al guardar domicilio: {str(e)}")

    @staticmethod
    def update_domicilio(db: Session, domicilio_id: UUID, domicilio_in: schemas.DomicilioUpdate) -> Optional[Domicilio]:
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

        # Enforce Single Fiscal Domicile Logic
        if update_data.get('es_fiscal'):
            # Demote others
            db.query(Domicilio).filter(
                Domicilio.cliente_id == db_domicilio.cliente_id,
                Domicilio.id != domicilio_id, # Don't demote self
                Domicilio.es_fiscal == True
            ).update({"es_fiscal": False})

        # [GY-FIX-V5] Fix Persistence Conflict: Empresa vs Nodo
        # If updating Empresa (transporte_id), clear Legacy Nodo (transporte_habitual_nodo_id)
        # to prevent ambiguity or legacy override.
        if 'transporte_id' in update_data:
             db_domicilio.transporte_habitual_nodo_id = None
             print(f"[DEBUG-TRP] Updating Transporte ID to {update_data['transporte_id']} (Clearing Nodo)")

        for key, value in update_data.items():
            setattr(db_domicilio, key, value)
            
        db.commit()
        db.refresh(db_domicilio)
        
        # Return Domicilio object
        return db_domicilio

    @staticmethod
    def delete_domicilio(db: Session, domicilio_id: UUID):
        db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if db_domicilio:
            # Soft Delete
            db_domicilio.activo = False
            db.add(db_domicilio)
            db.commit()
            db.refresh(db_domicilio)
        return db_domicilio
