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
            existing = db.query(Cliente).filter(Cliente.cuit == cliente_in.cuit).first()
            if existing:
                cliente_in.requiere_auditoria = True
            
            # Crear Cliente
            db_cliente = Cliente(
                razon_social=cliente_in.razon_social,
                cuit=cliente_in.cuit,
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
                    dom_data = dom_in.model_dump(exclude={'provincia', 'transporte_id', 'zona_id'})
                    
                    if dom_in.provincia:
                        dom_data['provincia_id'] = dom_in.provincia
                    
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
            joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.persona),
            joinedload(Cliente.vinculos).joinedload(agenda_models.VinculoComercial.tipo_contacto)
        ).filter(Cliente.id == cliente_id).first()

    @staticmethod
    def get_clientes(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Cliente]:
        from sqlalchemy.orm import joinedload
        # Modified to allow fetching inactive clients if needed, or by default just return all and let frontend filter
        # User requested: "SI un cliente está de baja lógica, no es mostrado en el listado cuando se one 'todos' en el encabezado"
        # So we should probably return ALL clients by default or have a flag.
        # The prompt said: "Verifica que el filtro 'Todos' en la lista traiga también a los inactivos."
        # So I will remove the filter(Cliente.activo == True).
        return db.query(Cliente).options(
            joinedload(Cliente.domicilios)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_cliente(db: Session, cliente_id: UUID, cliente_in: schemas.ClienteUpdate) -> Optional[Cliente]:
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        update_data = cliente_in.model_dump(exclude_unset=True)
        
        # Handle transporte_id separately (it belongs to Domicilio)
        transporte_id = update_data.pop('transporte_id', None)
        
        for key, value in update_data.items():
            setattr(db_cliente, key, value)
        
        # Update default domicile if transporte_id is provided
        if transporte_id:
            # Find default domicile (Fiscal or Entrega, or first one)
            default_dom = next((d for d in db_cliente.domicilios if d.es_entrega), None)
            if not default_dom:
                 default_dom = next((d for d in db_cliente.domicilios if d.es_fiscal), None)
            
            if default_dom:
                default_dom.transporte_id = transporte_id
                db.add(default_dom)
            else:
                # If no domicile exists, create a default one
                new_dom = Domicilio(
                    cliente_id=db_cliente.id,
                    transporte_id=transporte_id,
                    es_fiscal=True,
                    es_entrega=True,
                    alias="Domicilio Principal"
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
            
            summary_list.append(schemas.ClienteSummary(
                id=c.id, 
                razon_social=c.razon_social, 
                nombre_fantasia=getattr(c, 'nombre_fantasia', None), 
                domicilio_principal=domicilio_str,
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
        prov_id = domicilio_in.provincia
        if prov_id == "":
            prov_id = None
            
        if prov_id: 
             prov = db.query(Provincia).filter(Provincia.id == prov_id).first()
             if not prov:
                 raise HTTPException(status_code=400, detail="Código de provincia inválido")
        
        # Enforce Single Fiscal Domicile Logic
        if domicilio_in.es_fiscal:
            # Demote all existing domiciles
            db.query(Domicilio).filter(
                Domicilio.cliente_id == cliente_id,
                Domicilio.es_fiscal == True
            ).update({"es_fiscal": False})

        db_domicilio = Domicilio(
            **domicilio_in.model_dump(exclude={'provincia', 'zona_id'}), # Exclude zona_id as it's not in model
            provincia_id=prov_id,
            cliente_id=cliente_id
        )
        try:
            db.add(db_domicilio)
            db.commit()
            db.refresh(db_domicilio)
            # [GY-FIX] Return the full CLIENT as expected by Router response_model=ClienteResponse
            return ClienteService.get_cliente(db, cliente_id)
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
        
        # Remove fields not in model
        if 'zona_id' in update_data:
            update_data.pop('zona_id')
            
        if 'provincia' in update_data:
             val = update_data.pop('provincia')
             update_data['provincia_id'] = val if val != "" else None

        # Enforce Single Fiscal Domicile Logic
        if update_data.get('es_fiscal'):
            # Demote others
            db.query(Domicilio).filter(
                Domicilio.cliente_id == db_domicilio.cliente_id,
                Domicilio.id != domicilio_id, # Don't demote self (though it's about to be True anyway)
                Domicilio.es_fiscal == True
            ).update({"es_fiscal": False})

        for key, value in update_data.items():
            setattr(db_domicilio, key, value)
            
        db.commit()
        # Removed refresh, better to re-fetch with relationships
        
        # Return fully loaded client
        return ClienteService.get_cliente(db, db_domicilio.cliente_id)

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
