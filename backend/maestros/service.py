# backend/maestros/service.py
from typing import List
from sqlalchemy.orm import Session
from backend.maestros import models

class MaestrosService:
    @staticmethod
    def get_provincias(db: Session) -> List[models.Provincia]:
        return db.query(models.Provincia).all()

    @staticmethod
    def get_tipos_contacto(db: Session) -> List[models.TipoContacto]:
        return db.query(models.TipoContacto).all()

    @staticmethod
    def get_condiciones_iva(db: Session) -> List[models.CondicionIva]:
        return db.query(models.CondicionIva).all()

    @staticmethod
    def get_listas_precios(db: Session) -> List[models.ListaPrecios]:
        return db.query(models.ListaPrecios).filter(models.ListaPrecios.activo == True).all()
