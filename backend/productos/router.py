from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
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
    rubros = db.query(models.Rubro).offset(skip).limit(limit).all()
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

from fastapi.responses import JSONResponse
import traceback

@router.get("/rubros/test/probe")
def probe_router():
    return {"message": "Router works"}



    # return schemas.RubroDependency(
    #    rubros_hijos=hijos,
    #    productos=productos,
    #    cantidad_hijos=len(hijos),
    #    cantidad_productos=len(productos)
    # )

@router.get("/rubros/{rubro_id}/productos", response_model=List[schemas.ProductoRead])
def read_rubro_products(rubro_id: int, db: Session = Depends(get_db)):
    """Obtiene los productos directos de un rubro."""
    productos = db.query(models.Producto).options(joinedload(models.Producto.costos), joinedload(models.Producto.rubro)).filter(models.Producto.rubro_id == rubro_id, models.Producto.activo == True).all()
    for p in productos:
        calculate_prices(p)
    return productos

@router.post("/rubros/{rubro_id}/migrate_and_delete", status_code=status.HTTP_200_OK)
def migrate_and_delete_rubro(rubro_id: int, migration: schemas.RubroMigration, db: Session = Depends(get_db)):
    # 1. Validate Source
    source = db.query(models.Rubro).get(rubro_id)
    if not source:
        raise HTTPException(status_code=404, detail="Rubro origen no encontrado")
        
    # 2. Validate Target
    target = db.query(models.Rubro).get(migration.target_rubro_id)
    if not target:
        raise HTTPException(status_code=404, detail="Rubro destino no encontrado")
        
    if target.id == source.id:
        raise HTTPException(status_code=400, detail="No se puede migrar al mismo rubro")
        
    # Check for cycles if source is an ancestor of target (unlikely if active but possible)
    # If source is parent of target, and we move source's children to target... wait.
    # If source is parent of target, we cannot delete source and move target to target?
    # Logic:
    # Source (Delete) -> Children moved to Target.
    # If Target is a child of Source, then Target becomes a child of Target? (Cycle)
    # We must check if Target is a descendant of Source.
    
    # Simple Cycle Check: Is Source an ancestor of Target?
    curr = target
    while curr:
        if curr.id == source.id:
             raise HTTPException(status_code=400, detail="El rubro destino es descendiente del rubro a eliminar. Esto crearía un ciclo.")
        curr = curr.padre if curr.padre_id else None

    # 3. Migrate Children (Sub-rubros)
    # Update all rubros where padre_id = source.id
    hijos = db.query(models.Rubro).filter(models.Rubro.padre_id == source.id).all()
    for hijo in hijos:
        # If hijo is the target (rare case if not caught by cycle check), skip? 
        # No, cycle check handles it.
        hijo.padre_id = target.id
        
    # 4. Migrate Products
    productos = db.query(models.Producto).filter(models.Producto.rubro_id == source.id).all()
    for prod in productos:
        prod.rubro_id = target.id
        
    # 5. Deactivate/Delete Source
    source.activo = migration.new_status # Usually False
    
    db.commit()
    
    return {"message": f"Se migraron {len(hijos)} sub-rubros, {len(productos)} productos y se actualizó el estado del rubro origen."}

@router.post("/rubros/bulk_move", status_code=status.HTTP_200_OK)
def bulk_move_rubro_items(move_data: schemas.RubroBulkMove, db: Session = Depends(get_db)):
    # 1. Validate Target
    target = db.query(models.Rubro).get(move_data.target_rubro_id)
    if not target:
        raise HTTPException(status_code=404, detail="Rubro destino no encontrado")

    count_sub = 0
    count_prod = 0

    # 2. Move Sub-rubros
    if move_data.subrubros_ids:
        subrubros = db.query(models.Rubro).filter(models.Rubro.id.in_(move_data.subrubros_ids)).all()
        for sub in subrubros:
            # Cycle check for each subrubro
            # Check if target is a descendant of sub (cycle)
            curr = target
            while curr:
                if curr.id == sub.id:
                    raise HTTPException(status_code=400, detail=f"El rubro destino es descendiente de '{sub.nombre}'. Ciclo detectado.")
                curr = curr.padre if curr.padre_id else None
            
            # Additional check: sub cannot be target
            if sub.id == target.id:
                 raise HTTPException(status_code=400, detail=f"No se puede mover '{sub.nombre}' a sí mismo.")

            sub.padre_id = target.id
            count_sub += 1

    # 3. Move Products
    if move_data.productos_ids:
        # Bulk update is efficient here
        updated = db.query(models.Producto).filter(models.Producto.id.in_(move_data.productos_ids)).update({models.Producto.rubro_id: target.id}, synchronize_session=False)
        count_prod = updated

    db.commit()
    return {"message": f"Se movieron {count_sub} sub-rubros y {count_prod} productos a '{target.nombre}'."}

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

@router.get("/")
def read_productos(
    skip: int = 0, 
    limit: int = 1000, 
    activo: Optional[bool] = None, 
    rubro_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Producto).options(joinedload(models.Producto.costos), joinedload(models.Producto.rubro))
        
        # Apply Filters
        if activo is not None:
            query = query.filter(models.Producto.activo == activo)
        
        if rubro_id is not None:
            query = query.filter(models.Producto.rubro_id == rubro_id)

        productos = query.offset(skip).limit(limit).all()
        
        # Calcular precios para cada producto
        for p in productos:
            calculate_prices(p)
            
        # Minimal debug return
        return [
            {
                "id": p.id, 
                "nombre": p.nombre,
                "sku": p.sku,
                "precio_costo": p.costos.costo_reposicion if p.costos else 0
            } 
            for p in productos
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reading productos: {str(e)}")

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

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
def update_producto(producto_id: int, producto: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).options(joinedload(models.Producto.costos)).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Update Producto fields
    producto_data = producto.dict(exclude_unset=True, exclude={'costos'})
    for key, value in producto_data.items():
        setattr(db_producto, key, value)
    
    # Update Costos if present
    if producto.costos:
        # Check if costs exist
        if db_producto.costos:
             costos_data = producto.costos.dict(exclude_unset=True)
             for key, value in costos_data.items():
                 setattr(db_producto.costos, key, value)
        else:
             # Create costs if missing
             costos_data = producto.costos.dict()
             db_costos = models.ProductoCosto(**costos_data, producto_id=db_producto.id)
             db.add(db_costos)

    db.commit()
    db.refresh(db_producto)
    return calculate_prices(db_producto)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db_producto.activo = not db_producto.activo
    db.commit()
    return None

@router.delete("/{producto_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_producto(producto_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    try:
        db.delete(db_producto)
        db.commit()
    except IntegrityError:
        # Rollback automatically handled by session context usually, but explicit here
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el producto porque tiene registros asociados (ventas)."
        )
    return None
