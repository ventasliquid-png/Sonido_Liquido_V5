from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.clientes.models import Cliente, Domicilio, Contacto
from backend.clientes.schemas import ClienteCreate, ClienteUpdate

class ClienteService:
    @staticmethod
    def create_cliente(db: Session, cliente_in: ClienteCreate) -> Cliente:
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
        for dom_in in cliente_in.domicilios:
            db_domicilio = Domicilio(
                **dom_in.model_dump(),
                cliente_id=db_cliente.id
            )
            db.add(db_domicilio)
        
        # Crear Contactos
        for cont_in in cliente_in.contactos:
            db_contacto = Contacto(
                **cont_in.model_dump(),
                cliente_id=db_cliente.id
            )
            db.add(db_contacto)

        db.commit()
        db.refresh(db_cliente)
        return db_cliente

    @staticmethod
    def get_cliente(db: Session, cliente_id: UUID) -> Optional[Cliente]:
        return db.query(Cliente).filter(Cliente.id == cliente_id).first()

    @staticmethod
    def get_clientes(db: Session, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return db.query(Cliente).filter(Cliente.activo == True).offset(skip).limit(limit).all()

    @staticmethod
    def update_cliente(db: Session, cliente_id: UUID, cliente_in: ClienteUpdate) -> Optional[Cliente]:
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
