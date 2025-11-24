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
            # Verificar duplicados (CUIT)
            existing_cliente = db.query(Cliente).filter(Cliente.cuit == cliente_in.cuit).first()
            if existing_cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un cliente con este CUIT."
                )

            # Crear Cliente
            db_cliente = Cliente(
                razon_social=cliente_in.razon_social,
                cuit=cliente_in.cuit,
                condicion_iva_id=cliente_in.condicion_iva_id,
                lista_precios_id=cliente_in.lista_precios_id,
                activo=cliente_in.activo
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
    def get_clientes(db: Session, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return db.query(Cliente).filter(Cliente.activo == True).offset(skip).limit(limit).all()

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

    # --- Domicilios ---
    @staticmethod
    def create_domicilio(db: Session, cliente_id: UUID, domicilio_in: schemas.DomicilioCreate) -> Domicilio:
        # Validar Provincia
        from backend.maestros.models import Provincia
        if domicilio_in.provincia: # Schema uses 'provincia' string, model uses 'provincia_id'
             # Map schema 'provincia' to model 'provincia_id' if needed, or assume schema sends ID
             # The schema has 'provincia: Optional[str]'. The model has 'provincia_id'.
             # I should probably check if the schema field is meant to be the ID.
             # User said: "Al crear un Domicilio, valida que la Provincia sea correcta."
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
