from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.core.database import get_db
from backend.productos import models, schemas
from backend.productos.service import ProductoService

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# --- RUBROS ---

@router.get("/rubros", response_model=List[schemas.RubroRead])
def read_rubros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ProductoService.list_rubros(db, skip, limit)

@router.post("/rubros", response_model=schemas.RubroRead)
def create_rubro(rubro: schemas.RubroCreate, db: Session = Depends(get_db)):
    return ProductoService.create_rubro(db, rubro)

@router.put("/rubros/{rubro_id}", response_model=schemas.RubroRead)
def update_rubro(rubro_id: int, rubro: schemas.RubroUpdate, db: Session = Depends(get_db)):
    return ProductoService.update_rubro(db, rubro_id, rubro)

@router.delete("/rubros/{rubro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rubro(rubro_id: int, db: Session = Depends(get_db)):
    db_rubro = db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado")

    if db.query(models.Rubro).filter(models.Rubro.padre_id == rubro_id, models.Rubro.activo == True).first():
        raise HTTPException(status_code=400, detail="No se puede eliminar un rubro que tiene sub-rubros activos.")

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

@router.get("/rubros/{rubro_id}/productos", response_model=List[schemas.ProductoRead])
def read_rubro_products(rubro_id: int, db: Session = Depends(get_db)):
    """Obtiene los productos directos de un rubro."""
    productos = db.query(models.Producto).options(
        joinedload(models.Producto.costos),
        joinedload(models.Producto.rubro)
    ).filter(
        models.Producto.rubro_id == rubro_id,
        models.Producto.activo == True
    ).all()
    for p in productos:
        ProductoService.calculate_prices(p)
    return productos

@router.post("/rubros/{rubro_id}/migrate_and_delete", status_code=status.HTTP_200_OK)
def migrate_and_delete_rubro(rubro_id: int, migration: schemas.RubroMigration, db: Session = Depends(get_db)):
    source = db.query(models.Rubro).get(rubro_id)
    if not source:
        raise HTTPException(status_code=404, detail="Rubro origen no encontrado")

    target = db.query(models.Rubro).get(migration.target_rubro_id)
    if not target:
        raise HTTPException(status_code=404, detail="Rubro destino no encontrado")

    if target.id == source.id:
        raise HTTPException(status_code=400, detail="No se puede migrar al mismo rubro")

    curr = target
    while curr:
        if curr.id == source.id:
             raise HTTPException(status_code=400, detail="El rubro destino es descendiente del rubro a eliminar. Esto crearía un ciclo.")
        curr = curr.padre if curr.padre_id else None

    hijos = db.query(models.Rubro).filter(models.Rubro.padre_id == source.id).all()
    for hijo in hijos:
        hijo.padre_id = target.id

    productos = db.query(models.Producto).filter(models.Producto.rubro_id == source.id).all()
    for prod in productos:
        prod.rubro_id = target.id

    source.activo = migration.new_status
    db.commit()

    return {"message": f"Se migraron {len(hijos)} sub-rubros, {len(productos)} productos y se actualizó el estado del rubro origen."}

@router.post("/rubros/bulk_move", status_code=status.HTTP_200_OK)
def bulk_move_rubro_items(move_data: schemas.RubroBulkMove, db: Session = Depends(get_db)):
    target = db.query(models.Rubro).get(move_data.target_rubro_id)
    if not target:
        raise HTTPException(status_code=404, detail="Rubro destino no encontrado")

    count_sub = 0
    count_prod = 0

    if move_data.subrubros_ids:
        subrubros = db.query(models.Rubro).filter(models.Rubro.id.in_(move_data.subrubros_ids)).all()
        for sub in subrubros:
            curr = target
            while curr:
                if curr.id == sub.id:
                    raise HTTPException(status_code=400, detail=f"El rubro destino es descendiente de '{sub.nombre}'. Ciclo detectado.")
                curr = curr.padre if curr.padre_id else None

            if sub.id == target.id:
                 raise HTTPException(status_code=400, detail=f"No se puede mover '{sub.nombre}' a sí mismo.")

            sub.padre_id = target.id
            count_sub += 1

    if move_data.productos_ids:
        updated = db.query(models.Producto).filter(models.Producto.id.in_(move_data.productos_ids)).update(
            {models.Producto.rubro_id: target.id}, synchronize_session=False
        )
        count_prod = updated

    db.commit()
    return {"message": f"Se movieron {count_sub} sub-rubros y {count_prod} productos a '{target.nombre}'."}

# --- PRODUCTOS ---

@router.get("", response_model=List[schemas.ProductoRead])
def read_productos(
    skip: int = 0,
    limit: int = 1000,
    activo: Optional[bool] = None,
    rubro_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return ProductoService.list_productos(db, skip, limit, activo, rubro_id, search)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reading productos: {str(e)}")

@router.post("", response_model=schemas.ProductoRead)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return ProductoService.create_producto(db, producto)

@router.get("/{producto_id}", response_model=schemas.ProductoRead)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).options(
        joinedload(models.Producto.costos),
        joinedload(models.Producto.rubro)
    ).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoService.calculate_prices(producto)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
def update_producto(producto_id: int, producto: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    return ProductoService.update_producto(db, producto_id, producto)

@router.post("/{producto_id}/toggle", response_model=schemas.ProductoRead)
def toggle_producto_status(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db_producto.activo = not db_producto.activo
    db.commit()
    return ProductoService.calculate_prices(db_producto)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    print(f"--- DELETE REQUEST FOR ID {producto_id} ---")
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        print("Product not found")
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    current_status = db_producto.activo
    db_producto.activo = not current_status
    db.commit()
    print(f"Toggled Product {producto_id} from {current_status} to {db_producto.activo}")
    return None

@router.get("/{producto_id}/integrity_check")
def check_producto_integrity(producto_id: int, db: Session = Depends(get_db)):
    """
    Verifica si es seguro eliminar físicamente un producto.
    Retorna conteo de dependencias (Items de Pedido).
    """
    from backend.pedidos.models import PedidoItem

    dependency_count = db.query(PedidoItem).filter(PedidoItem.producto_id == producto_id).count()

    is_safe = dependency_count == 0
    message = "Sin dependencias. Seguro para eliminar." if is_safe else f"Participa en {dependency_count} líneas de pedido."

    return {
        "safe": is_safe,
        "dependencies": dependency_count,
        "message": message
    }

@router.delete("/{producto_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_producto(producto_id: int, db: Session = Depends(get_db)):
    return ProductoService.hard_delete_producto(db, producto_id)

# --- PROVEEDORES ALTERNATIVOS (V5.4) ---

@router.post("/{producto_id}/proveedores", response_model=schemas.ProductoProveedorRead)
def create_producto_proveedor(producto_id: int, proveedor_data: schemas.ProductoProveedorCreate, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).get(producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    from backend.proveedores.models import Proveedor
    db_proveedor = db.query(Proveedor).get(proveedor_data.proveedor_id)
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db_rel = models.ProductoProveedor(
        producto_id=producto_id,
        proveedor_id=proveedor_data.proveedor_id,
        costo=proveedor_data.costo,
        moneda=proveedor_data.moneda,
        observaciones=proveedor_data.observaciones
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

@router.delete("/proveedores/{costo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_proveedor(costo_id: int, db: Session = Depends(get_db)):
    db_rel = db.query(models.ProductoProveedor).get(costo_id)
    if not db_rel:
        raise HTTPException(status_code=404, detail="Registro de costo no encontrado")

    db.delete(db_rel)
    db.commit()
    return None
