from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from backend.core.database import get_db
from backend.productos import models, schemas

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# --- RUBROS ---

@router.get("/rubros", response_model=List[schemas.RubroRead])
def read_rubros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Para obtener el árbol, idealmente filtraríamos solo los raíces (padre_id=None)
    # y dejaríamos que la recursividad cargue los hijos.
    # Pero para un listado plano o select, a veces se necesitan todos.
    # Aquí devolveremos todos los raíces con sus hijos anidados.
    rubros = db.query(models.Rubro).filter(models.Rubro.padre_id == None).offset(skip).limit(limit).all()
    return rubros

@router.post("/rubros", response_model=schemas.RubroRead)
def create_rubro(rubro: schemas.RubroCreate, db: Session = Depends(get_db)):
    # Validar unicidad de código
    if db.query(models.Rubro).filter(models.Rubro.codigo == rubro.codigo).first():
        raise HTTPException(status_code=400, detail=f"El código '{rubro.codigo}' ya existe.")
    
    # Validar unicidad de nombre
    if db.query(models.Rubro).filter(models.Rubro.nombre == rubro.nombre).first():
        raise HTTPException(status_code=400, detail=f"El rubro '{rubro.nombre}' ya existe.")

    db_rubro = models.Rubro(**rubro.dict())
    db.add(db_rubro)
    db.commit()
    db.refresh(db_rubro)
    return db_rubro

@router.put("/rubros/{rubro_id}", response_model=schemas.RubroRead)
def update_rubro(rubro_id: int, rubro: schemas.RubroUpdate, db: Session = Depends(get_db)):
    db_rubro = db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    
    # Validar unicidad de código si cambia
    if rubro.codigo and rubro.codigo != db_rubro.codigo:
        if db.query(models.Rubro).filter(models.Rubro.codigo == rubro.codigo).first():
            raise HTTPException(status_code=400, detail=f"El código '{rubro.codigo}' ya existe.")

    # Validar unicidad de nombre si cambia
    if rubro.nombre and rubro.nombre != db_rubro.nombre:
        if db.query(models.Rubro).filter(models.Rubro.nombre == rubro.nombre).first():
            raise HTTPException(status_code=400, detail=f"El rubro '{rubro.nombre}' ya existe.")

    # Validar ciclos en jerarquía
    if rubro.padre_id is not None:
        if rubro.padre_id == rubro_id:
            raise HTTPException(status_code=400, detail="Un rubro no puede ser su propio padre.")
        
        # Chequear si el nuevo padre es descendiente del rubro actual (Ciclo)
        # Recorremos hacia arriba desde el nuevo padre
        current = db.query(models.Rubro).get(rubro.padre_id)
        while current:
            if current.id == rubro_id:
                raise HTTPException(status_code=400, detail="No se puede asignar como padre a un descendiente (Ciclo detectado).")
            current = current.padre if current.padre_id else None

    # Validar desactivación (Si se está desactivando)
    if rubro.activo is False and db_rubro.activo is True:
        # Validar si tiene hijos activos
        if db.query(models.Rubro).filter(models.Rubro.padre_id == rubro_id, models.Rubro.activo == True).first():
            raise HTTPException(status_code=400, detail="No se puede desactivar un rubro que tiene sub-rubros activos.")
        
        # Validar si tiene productos asociados activos
        if db.query(models.Producto).filter(models.Producto.rubro_id == rubro_id, models.Producto.activo == True).first():
            raise HTTPException(status_code=400, detail="No se puede desactivar un rubro que tiene productos activos asociados.")

    for key, value in rubro.dict(exclude_unset=True).items():
        setattr(db_rubro, key, value)
    
    db.commit()
    db.refresh(db_rubro)
    return db_rubro

@router.delete("/rubros/{rubro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rubro(rubro_id: int, db: Session = Depends(get_db)):
    db_rubro = db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")
    
    # Soft delete or hard delete? Model has 'activo', let's use soft delete if possible or hard if requested.
    # The model has 'activo = Column(Boolean, default=True)'
    # Let's do soft delete by default or toggle active.
    # But usually delete endpoint implies removal.
    # Given the previous pattern in other modules, let's check.
    # Proveedores router does soft delete.
    # Let's do soft delete here too.
    # Validar si tiene hijos activos
    if db.query(models.Rubro).filter(models.Rubro.padre_id == rubro_id, models.Rubro.activo == True).first():
        raise HTTPException(status_code=400, detail="No se puede eliminar un rubro que tiene sub-rubros activos.")

    # Validar si tiene productos asociados
    if db.query(models.Producto).filter(models.Producto.rubro_id == rubro_id, models.Producto.activo == True).first():
        raise HTTPException(status_code=400, detail="No se puede eliminar un rubro que tiene productos activos asociados.")

    db_rubro.activo = False
    db.commit()
    return None

# --- PRODUCTOS ---

def calculate_prices(producto: models.Producto):
    """Helper para calcular precios basados en costos."""
    if not producto.costos:
        return producto
    
    costo = producto.costos.costo_reposicion
    margen = producto.costos.margen_mayorista
    iva = producto.costos.iva_alicuota
    
    # Cálculos Simples (Ejemplo)
    # Precio Mayorista = Costo + Margen
    precio_neto = costo * (1 + margen / 100)
    precio_final = precio_neto * (1 + iva / 100)
    
    # Asignamos atributos dinámicos al objeto (Pydantic los leerá)
    producto.precio_mayorista = precio_final # Asumiendo que el precio mayorista es el final con IVA? O sin IVA?
    # Usualmente Mayorista es con IVA.
    
    # Distri y Minorista (Placeholders por ahora)
    producto.precio_distribuidor = precio_final * Decimal("1.10") # +10%
    producto.precio_minorista = precio_final * Decimal("1.40") # +40%
    
    return producto

from decimal import Decimal

@router.get("/", response_model=List[schemas.ProductoRead])
def read_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).options(joinedload(models.Producto.costos), joinedload(models.Producto.rubro)).offset(skip).limit(limit).all()
    
    # Calcular precios para cada producto
    for p in productos:
        calculate_prices(p)
        
    return productos

@router.post("/", response_model=schemas.ProductoRead)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    # 1. Crear Producto
    producto_data = producto.dict(exclude={'costos'})
    db_producto = models.Producto(**producto_data)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    # 2. Crear Costos
    costos_data = producto.costos.dict()
    db_costos = models.ProductoCosto(**costos_data, producto_id=db_producto.id)
    db.add(db_costos)
    db.commit()
    
    # Recargar con relaciones
    db.refresh(db_producto)
    # Forzar carga de costos si no se hizo
    # db_producto.costos 
    
    return calculate_prices(db_producto)

@router.get("/{producto_id}", response_model=schemas.ProductoRead)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).options(joinedload(models.Producto.costos), joinedload(models.Producto.rubro)).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return calculate_prices(producto)
