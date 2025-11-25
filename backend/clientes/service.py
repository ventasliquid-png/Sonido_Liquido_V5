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
                        dom_data['transporte_habitual_nodo_id'] = dom_in.transporte_id
                    
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
        # Modified to allow fetching inactive clients if needed, or by default just return all and let frontend filter
        # User requested: "SI un cliente está de baja lógica, no es mostrado en el listado cuando se one 'todos' en el encabezado"
        # So we should probably return ALL clients by default or have a flag.
        # The prompt said: "Verifica que el filtro 'Todos' en la lista traiga también a los inactivos."
        # So I will remove the filter(Cliente.activo == True).
        return db.query(Cliente).offset(skip).limit(limit).all()

    @staticmethod
    def update_cliente(db: Session, cliente_id: UUID, cliente_in: schemas.ClienteUpdate) -> Optional[Cliente]:
        db_cliente = ClienteService.get_cliente(db, cliente_id)
        if not db_cliente:
            return None
        
        update_data = cliente_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_cliente, key, value)
        
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
    def check_cuit(db: Session, cuit: str) -> schemas.CuitCheckResponse:
        clients = db.query(Cliente).filter(Cliente.cuit == cuit).all()
        
        if not clients:
            return schemas.CuitCheckResponse(status="NEW", existing_clients=[])
        
        # Check if any is active
        active_clients = [c for c in clients if c.activo]
        
        if active_clients:
            summary_list = [
                schemas.ClienteSummary(
                    id=c.id, 
                    razon_social=c.razon_social, 
                    nombre_fantasia=getattr(c, 'nombre_fantasia', None), 
                    activo=c.activo
                ) for c in clients
            ]
            return schemas.CuitCheckResponse(status="EXISTS", existing_clients=summary_list)
        else:
            summary_list = [
                schemas.ClienteSummary(
                    id=c.id, 
                    razon_social=c.razon_social, 
                    nombre_fantasia=getattr(c, 'nombre_fantasia', None),
                    activo=c.activo
                ) for c in clients
            ]
            return schemas.CuitCheckResponse(status="INACTIVE", existing_clients=summary_list)

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
        if domicilio_in.provincia: # Schema uses 'provincia' string, model uses 'provincia_id'
             prov = db.query(Provincia).filter(Provincia.id == domicilio_in.provincia).first()
             if not prov:
                 raise HTTPException(status_code=400, detail="Código de provincia inválido")

        db_domicilio = Domicilio(
            **domicilio_in.model_dump(exclude={'provincia'}), # Exclude to map manually
            provincia_id=domicilio_in.provincia,
            cliente_id=cliente_id
        )
        db.add(db_domicilio)
        db.commit()
        db.refresh(db_domicilio)
        return db_domicilio

    @staticmethod
    def update_domicilio(db: Session, domicilio_id: UUID, domicilio_in: schemas.DomicilioUpdate) -> Optional[Domicilio]:
        db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if not db_domicilio:
            return None
        
        update_data = domicilio_in.model_dump(exclude_unset=True)
        if 'provincia' in update_data:
             update_data['provincia_id'] = update_data.pop('provincia')

        for key, value in update_data.items():
            setattr(db_domicilio, key, value)
        
        db.add(db_domicilio)
        db.commit()
        db.refresh(db_domicilio)
        return db_domicilio

    @staticmethod
    def delete_domicilio(db: Session, domicilio_id: UUID):
        db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
        if db_domicilio:
            db.delete(db_domicilio)
            db.commit()
        return db_domicilio
