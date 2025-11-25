# backend/maestros/service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.maestros import models, schemas

class MaestrosService:
    # --- Read Only ---
    @staticmethod
    def get_provincias(db: Session) -> List[models.Provincia]:
        return db.query(models.Provincia).all()

    @staticmethod
    def get_tipos_contacto(db: Session) -> List[models.TipoContacto]:
        return db.query(models.TipoContacto).all()

    @staticmethod
    def get_condiciones_iva(db: Session) -> List[models.CondicionIva]:
        return db.query(models.CondicionIva).all()

    # --- Listas de Precios ---
    @staticmethod
    def get_listas_precios(db: Session) -> List[models.ListaPrecios]:
        return db.query(models.ListaPrecios).filter(models.ListaPrecios.activo == True).all()

    @staticmethod
    def get_lista_precios(db: Session, id: UUID) -> Optional[models.ListaPrecios]:
        return db.query(models.ListaPrecios).filter(models.ListaPrecios.id == id).first()

    @staticmethod
    def create_lista_precios(db: Session, lista: schemas.ListaPreciosCreate) -> models.ListaPrecios:
        db_lista = models.ListaPrecios(**lista.model_dump())
        db.add(db_lista)
        db.commit()
        db.refresh(db_lista)
        return db_lista

    @staticmethod
    def update_lista_precios(db: Session, id: UUID, lista: schemas.ListaPreciosUpdate) -> Optional[models.ListaPrecios]:
        db_lista = MaestrosService.get_lista_precios(db, id)
        if not db_lista:
            return None
        
        update_data = lista.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lista, key, value)
        
        db.add(db_lista)
        db.commit()
        db.refresh(db_lista)
        return db_lista

    # --- Ramos ---
    @staticmethod
    def get_ramos(db: Session) -> List[models.Ramo]:
        return db.query(models.Ramo).filter(models.Ramo.activo == True).all()

    @staticmethod
    def get_ramo(db: Session, id: UUID) -> Optional[models.Ramo]:
        return db.query(models.Ramo).filter(models.Ramo.id == id).first()

    @staticmethod
    def create_ramo(db: Session, ramo: schemas.RamoCreate) -> models.Ramo:
        db_ramo = models.Ramo(**ramo.model_dump())
        db.add(db_ramo)
        db.commit()
        db.refresh(db_ramo)
        return db_ramo

    @staticmethod
    def update_ramo(db: Session, id: UUID, ramo: schemas.RamoUpdate) -> Optional[models.Ramo]:
        db_ramo = MaestrosService.get_ramo(db, id)
        if not db_ramo:
            return None
        
        update_data = ramo.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ramo, key, value)
        
        db.add(db_ramo)
        db.commit()
        db.refresh(db_ramo)
        return db_ramo

    # --- Vendedores ---
    @staticmethod
    def get_vendedores(db: Session) -> List[models.Vendedor]:
        return db.query(models.Vendedor).filter(models.Vendedor.activo == True).all()

    @staticmethod
    def get_vendedor(db: Session, id: UUID) -> Optional[models.Vendedor]:
        return db.query(models.Vendedor).filter(models.Vendedor.id == id).first()

    @staticmethod
    def create_vendedor(db: Session, vendedor: schemas.VendedorCreate) -> models.Vendedor:
        db_vendedor = models.Vendedor(**vendedor.model_dump())
        db.add(db_vendedor)
        db.commit()
        db.refresh(db_vendedor)
        return db_vendedor

    @staticmethod
    def update_vendedor(db: Session, id: UUID, vendedor: schemas.VendedorUpdate) -> Optional[models.Vendedor]:
        db_vendedor = MaestrosService.get_vendedor(db, id)
        if not db_vendedor:
            return None
        
        update_data = vendedor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_vendedor, key, value)
        
        db.add(db_vendedor)
        db.commit()
        db.refresh(db_vendedor)
        return db_vendedor
