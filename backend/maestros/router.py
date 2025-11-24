# backend/maestros/router.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from backend.maestros import schemas, service

router = APIRouter(
    prefix="/maestros",
    tags=["Maestros"],
    responses={404: {"description": "Not found"}},
)

@router.get("/provincias", response_model=List[schemas.ProvinciaResponse])
def read_provincias(db: Session = Depends(get_db)):
    return service.MaestrosService.get_provincias(db)

@router.get("/tipos-contacto", response_model=List[schemas.TipoContactoResponse])
def read_tipos_contacto(db: Session = Depends(get_db)):
    return service.MaestrosService.get_tipos_contacto(db)

@router.get("/condiciones-iva", response_model=List[schemas.CondicionIvaResponse])
def read_condiciones_iva(db: Session = Depends(get_db)):
    return service.MaestrosService.get_condiciones_iva(db)

@router.get("/listas-precios", response_model=List[schemas.ListaPreciosResponse])
def read_listas_precios(db: Session = Depends(get_db)):
    return service.MaestrosService.get_listas_precios(db)
