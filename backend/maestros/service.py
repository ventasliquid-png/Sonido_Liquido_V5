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
    def get_listas_precios(db: Session, status: str = "active") -> List[models.ListaPrecios]:
        query = db.query(models.ListaPrecios)
        if status == "active":
            query = query.filter(models.ListaPrecios.activo == True)
        elif status == "inactive":
            query = query.filter(models.ListaPrecios.activo == False)
        return query.all()

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

    # --- Segmentos ---
    @staticmethod
    def get_segmentos(db: Session, status: str = "active") -> List[models.Segmento]:
        query = db.query(models.Segmento)
        if status == "active":
            query = query.filter(models.Segmento.activo == True)
        elif status == "inactive":
            query = query.filter(models.Segmento.activo == False)
        return query.all()

    @staticmethod
    def get_segmento(db: Session, id: UUID) -> Optional[models.Segmento]:
        return db.query(models.Segmento).filter(models.Segmento.id == id).first()

    @staticmethod
    def create_segmento(db: Session, segmento: schemas.SegmentoCreate) -> models.Segmento:
        db_segmento = models.Segmento(**segmento.model_dump())
        db.add(db_segmento)
        db.commit()
        db.refresh(db_segmento)
        return db_segmento

    @staticmethod
    def update_segmento(db: Session, id: UUID, segmento: schemas.SegmentoUpdate) -> Optional[models.Segmento]:
        db_segmento = MaestrosService.get_segmento(db, id)
        if not db_segmento:
            return None
        
        update_data = segmento.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_segmento, key, value)
        
        db.add(db_segmento)
        db.commit()
        db.refresh(db_segmento)
        return db_segmento

    # --- Vendedores ---
    @staticmethod
    def get_vendedores(db: Session, status: str = "active") -> List[models.Vendedor]:
        query = db.query(models.Vendedor)
        if status == "active":
            query = query.filter(models.Vendedor.activo == True)
        elif status == "inactive":
            query = query.filter(models.Vendedor.activo == False)
        return query.all()

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
