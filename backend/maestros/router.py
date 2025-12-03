# backend/maestros/router.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from core.database import get_db
from backend.maestros import schemas, service

router = APIRouter(
    prefix="/maestros",
    tags=["Maestros"],
    responses={404: {"description": "Not found"}},
)

# --- Read Only Maestros ---
@router.get("/provincias", response_model=List[schemas.ProvinciaResponse])
def read_provincias(db: Session = Depends(get_db)):
    return service.MaestrosService.get_provincias(db)

@router.post("/provincias", response_model=schemas.ProvinciaResponse, status_code=status.HTTP_201_CREATED)
def create_provincia(provincia: schemas.ProvinciaCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_provincia(db, provincia)

@router.put("/provincias/{id}", response_model=schemas.ProvinciaResponse)
def update_provincia(id: str, provincia: schemas.ProvinciaUpdate, db: Session = Depends(get_db)):
    db_provincia = service.MaestrosService.update_provincia(db, id, provincia)
    if db_provincia is None:
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    return db_provincia

@router.delete("/provincias/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provincia(id: str, db: Session = Depends(get_db)):
    if not service.MaestrosService.delete_provincia(db, id):
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    return None

@router.get("/condiciones-iva", response_model=List[schemas.CondicionIvaResponse])
def read_condiciones_iva(db: Session = Depends(get_db)):
    return service.MaestrosService.get_condiciones_iva(db)

@router.post("/condiciones-iva", response_model=schemas.CondicionIvaResponse, status_code=status.HTTP_201_CREATED)
def create_condicion_iva(condicion: schemas.CondicionIvaCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_condicion_iva(db, condicion)

@router.put("/condiciones-iva/{id}", response_model=schemas.CondicionIvaResponse)
def update_condicion_iva(id: UUID, condicion: schemas.CondicionIvaUpdate, db: Session = Depends(get_db)):
    db_condicion = service.MaestrosService.update_condicion_iva(db, id, condicion)
    if db_condicion is None:
        raise HTTPException(status_code=404, detail="Condición de IVA no encontrada")
    return db_condicion

@router.delete("/condiciones-iva/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_condicion_iva(id: UUID, db: Session = Depends(get_db)):
    if not service.MaestrosService.delete_condicion_iva(db, id):
        raise HTTPException(status_code=404, detail="Condición de IVA no encontrada")
    return None

@router.get("/tipos-contacto", response_model=List[schemas.TipoContactoResponse])
def read_tipos_contacto(db: Session = Depends(get_db)):
    return service.MaestrosService.get_tipos_contacto(db)

@router.post("/tipos-contacto", response_model=schemas.TipoContactoResponse, status_code=status.HTTP_201_CREATED)
def create_tipo_contacto(tipo: schemas.TipoContactoCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_tipo_contacto(db, tipo)

@router.put("/tipos-contacto/{id}", response_model=schemas.TipoContactoResponse)
def update_tipo_contacto(id: str, tipo: schemas.TipoContactoUpdate, db: Session = Depends(get_db)):
    db_tipo = service.MaestrosService.update_tipo_contacto(db, id, tipo)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de contacto no encontrado")
    return db_tipo

@router.delete("/tipos-contacto/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo_contacto(id: str, db: Session = Depends(get_db)):
    if not service.MaestrosService.delete_tipo_contacto(db, id):
        raise HTTPException(status_code=404, detail="Tipo de contacto no encontrado")
    return None

# --- Listas de Precios ---
@router.get("/listas-precios", response_model=List[schemas.ListaPreciosResponse])
def read_listas_precios(status: str = Query("active", enum=["active", "inactive", "all"]), db: Session = Depends(get_db)):
    return service.MaestrosService.get_listas_precios(db, status)

@router.post("/listas-precios", response_model=schemas.ListaPreciosResponse, status_code=status.HTTP_201_CREATED)
def create_lista_precios(lista: schemas.ListaPreciosCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_lista_precios(db, lista)

@router.put("/listas-precios/{id}", response_model=schemas.ListaPreciosResponse)
def update_lista_precios(id: UUID, lista: schemas.ListaPreciosUpdate, db: Session = Depends(get_db)):
    db_lista = service.MaestrosService.update_lista_precios(db, id, lista)
    if db_lista is None:
        raise HTTPException(status_code=404, detail="Lista de precios no encontrada")
    return db_lista

# --- Segmentos ---
@router.get("/segmentos", response_model=List[schemas.SegmentoResponse])
def read_segmentos(status: str = Query("active", enum=["active", "inactive", "all"]), db: Session = Depends(get_db)):
    return service.MaestrosService.get_segmentos(db, status)

@router.post("/segmentos", response_model=schemas.SegmentoResponse, status_code=status.HTTP_201_CREATED)
def create_segmento(segmento: schemas.SegmentoCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_segmento(db, segmento)

@router.put("/segmentos/{id}", response_model=schemas.SegmentoResponse)
def update_segmento(id: UUID, segmento: schemas.SegmentoUpdate, db: Session = Depends(get_db)):
    db_segmento = service.MaestrosService.update_segmento(db, id, segmento)
    if db_segmento is None:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    return db_segmento

# --- Vendedores ---
@router.get("/vendedores", response_model=List[schemas.VendedorResponse])
def read_vendedores(status: str = Query("active", enum=["active", "inactive", "all"]), db: Session = Depends(get_db)):
    return service.MaestrosService.get_vendedores(db, status)

@router.post("/vendedores", response_model=schemas.VendedorResponse, status_code=status.HTTP_201_CREATED)
def create_vendedor(vendedor: schemas.VendedorCreate, db: Session = Depends(get_db)):
    return service.MaestrosService.create_vendedor(db, vendedor)

@router.put("/vendedores/{id}", response_model=schemas.VendedorResponse)
def update_vendedor(id: UUID, vendedor: schemas.VendedorUpdate, db: Session = Depends(get_db)):
    db_vendedor = service.MaestrosService.update_vendedor(db, id, vendedor)
    if db_vendedor is None:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    return db_vendedor

# --- Tasas IVA ---
@router.get("/tasas-iva", response_model=List[schemas.TasaIVAResponse])
def read_tasas_iva(db: Session = Depends(get_db)):
    return service.MaestrosService.get_tasas_iva(db)

# --- Unidades ---
@router.get("/unidades", response_model=List[schemas.UnidadResponse])
def read_unidades(db: Session = Depends(get_db)):
    return service.MaestrosService.get_unidades(db)
