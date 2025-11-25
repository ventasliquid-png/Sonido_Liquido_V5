# backend/maestros/router.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from backend.maestros import schemas, service

router = APIRouter(
    prefix="/maestros",
    tags=["Maestros"],
    responses={404: {"description": "Not found"}},
)

# --- Read Only ---
@router.get("/provincias", response_model=List[schemas.ProvinciaResponse])
def read_provincias(db: Session = Depends(get_db)):
    return service.MaestrosService.get_provincias(db)

@router.get("/tipos-contacto", response_model=List[schemas.TipoContactoResponse])
def read_tipos_contacto(db: Session = Depends(get_db)):
    return service.MaestrosService.get_tipos_contacto(db)

@router.get("/condiciones-iva", response_model=List[schemas.CondicionIvaResponse])
def read_condiciones_iva(db: Session = Depends(get_db)):
    return service.MaestrosService.get_condiciones_iva(db)

# --- Listas de Precios ---
@router.get("/listas-precios", response_model=List[schemas.ListaPreciosResponse])
def read_listas_precios(db: Session = Depends(get_db)):
    return service.MaestrosService.get_listas_precios(db)

@router.post("/listas-precios", response_model=schemas.ListaPreciosResponse, status_code=status.HTTP_201_CREATED)
def create_lista_precios(lista: schemas.ListaPreciosCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_lista_precios(db, lista)

@router.put("/listas-precios/{id}", response_model=schemas.ListaPreciosResponse)
def update_lista_precios(id: UUID, lista: schemas.ListaPreciosUpdate, db: Session = Depends(get_db)):
    db_lista = service.MaestrosService.update_lista_precios(db, id, lista)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista de precios no encontrada")
    return db_lista

# --- Ramos ---
@router.get("/ramos", response_model=List[schemas.RamoResponse])
def read_ramos(db: Session = Depends(get_db)):
    return service.MaestrosService.get_ramos(db)

@router.post("/ramos", response_model=schemas.RamoResponse, status_code=status.HTTP_201_CREATED)
def create_ramo(ramo: schemas.RamoCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_ramo(db, ramo)

@router.put("/ramos/{id}", response_model=schemas.RamoResponse)
def update_ramo(id: UUID, ramo: schemas.RamoUpdate, db: Session = Depends(get_db)):
    db_ramo = service.MaestrosService.update_ramo(db, id, ramo)
    if db_ramo is None:
        raise HTTPException(status_code=404, detail="Ramo no encontrado")
    return db_ramo

# --- Vendedores ---
@router.get("/vendedores", response_model=List[schemas.VendedorResponse])
def read_vendedores(db: Session = Depends(get_db)):
    return service.MaestrosService.get_vendedores(db)

@router.post("/vendedores", response_model=schemas.VendedorResponse, status_code=status.HTTP_201_CREATED)
def create_vendedor(vendedor: schemas.VendedorCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_vendedor(db, vendedor)

@router.put("/vendedores/{id}", response_model=schemas.VendedorResponse)
def update_vendedor(id: UUID, vendedor: schemas.VendedorUpdate, db: Session = Depends(get_db)):
    db_vendedor = service.MaestrosService.update_vendedor(db, id, vendedor)
    if db_vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    return db_vendedor
