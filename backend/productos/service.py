from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String, func
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from backend.productos import models, schemas
from backend.pricing_engine import calculate_lists
from backend.productos.constants import ProductoFlags

class ProductoService:

    @staticmethod
    def calculate_prices(producto: models.Producto):
        """Helper para calcular precios basados en costos usando el MOTOR V5."""
        if not producto.costos:
            producto.precio_mayorista = 0
            producto.precio_distribuidor = 0
            producto.precio_minorista = 0
            return producto

        # Motor V5: Cascada Clásica
        listas = calculate_lists(producto.costos.costo_reposicion, producto.costos.rentabilidad_target)

        # Mapeo de Referencia para UI
        producto.precio_mayorista = listas.get('lista_1', 0)
        producto.precio_distribuidor = listas.get('lista_3', 0)
        producto.precio_minorista = listas.get('lista_5', 0)

        return producto

    # --- RUBROS ---

    @staticmethod
    def list_rubros(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Rubro).offset(skip).limit(limit).all()

    @staticmethod
    def create_rubro(db: Session, rubro_in: schemas.RubroCreate):
        if db.query(models.Rubro).filter(models.Rubro.codigo == rubro_in.codigo).first():
            raise HTTPException(status_code=400, detail=f"El código '{rubro_in.codigo}' ya existe.")
        if db.query(models.Rubro).filter(models.Rubro.nombre == rubro_in.nombre).first():
            raise HTTPException(status_code=400, detail=f"El rubro '{rubro_in.nombre}' ya existe.")

        db_rubro = models.Rubro(**rubro_in.dict())
        db.add(db_rubro)
        db.commit()
        db.refresh(db_rubro)
        return db_rubro

    @staticmethod
    def update_rubro(db: Session, rubro_id: int, rubro_in: schemas.RubroUpdate):
        db_rubro = db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()
        if not db_rubro: raise HTTPException(status_code=404, detail="Rubro no encontrado")

        if rubro_in.codigo and rubro_in.codigo != db_rubro.codigo:
            if db.query(models.Rubro).filter(models.Rubro.codigo == rubro_in.codigo).first():
                raise HTTPException(status_code=400, detail=f"El código '{rubro_in.codigo}' ya existe.")

        if rubro_in.nombre and rubro_in.nombre != db_rubro.nombre:
            if db.query(models.Rubro).filter(models.Rubro.nombre == rubro_in.nombre).first():
                raise HTTPException(status_code=400, detail=f"El rubro '{rubro_in.nombre}' ya existe.")

        # Ciclo check
        if rubro_in.padre_id is not None:
            if rubro_in.padre_id == rubro_id:
                raise HTTPException(status_code=400, detail="Un rubro no puede ser su propio padre.")
            current = db.query(models.Rubro).get(rubro_in.padre_id)
            while current:
                if current.id == rubro_id:
                    raise HTTPException(status_code=400, detail="Ciclo detectado en la jerarquía.")
                current = current.padre if current.padre_id else None

        for key, value in rubro_in.dict(exclude_unset=True).items():
            setattr(db_rubro, key, value)

        db.commit()
        db.refresh(db_rubro)
        return db_rubro

    # --- PRODUCTOS ---

    @staticmethod
    def list_productos(db: Session, skip: int = 0, limit: int = 1000, activo: Optional[bool] = None,
                       rubro_id: Optional[int] = None, search: Optional[str] = None):
        query = db.query(models.Producto).options(
            joinedload(models.Producto.costos),
            joinedload(models.Producto.rubro)
        )
        if activo is not None:
            query = query.filter(models.Producto.activo == activo)
        if rubro_id is not None:
            query = query.filter(models.Producto.rubro_id == rubro_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                models.Producto.nombre.ilike(search_term),
                models.Producto.codigo_visual.ilike(search_term),
                cast(models.Producto.sku, String).ilike(search_term)
            ))

        productos = query.offset(skip).limit(limit).all()
        for p in productos:
            ProductoService.calculate_prices(p)
        return productos

    @staticmethod
    def create_producto(db: Session, prod_in: schemas.ProductoCreate):
        # 1. Crear Producto
        producto_data = prod_in.dict(exclude={'costos'})
        db_producto = models.Producto(**producto_data)

        # [AUTO-SKU V5.8]
        if not db_producto.sku:
            max_sku = db.query(func.max(models.Producto.sku)).scalar()
            db_producto.sku = int(max_sku or 10000) + 1

        db.add(db_producto)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Conflicto de integridad: {str(e)}")

        db.refresh(db_producto)

        # 2. Crear Costos
        costos_data = prod_in.costos.dict()
        db_costos = models.ProductoCosto(**costos_data, producto_id=db_producto.id)
        db.add(db_costos)
        db.commit()

        db.refresh(db_producto)
        return ProductoService.calculate_prices(db_producto)

    @staticmethod
    def update_producto(db: Session, producto_id: int, prod_in: schemas.ProductoUpdate):
        db_producto = db.query(models.Producto).options(joinedload(models.Producto.costos)).filter(models.Producto.id == producto_id).first()
        if not db_producto: raise HTTPException(status_code=404, detail="Producto no encontrado")

        prod_data = prod_in.dict(exclude_unset=True, exclude={'costos'})
        for key, value in prod_data.items():
            setattr(db_producto, key, value)

        if prod_in.costos:
            if db_producto.costos:
                for key, value in prod_in.costos.dict(exclude_unset=True).items():
                    setattr(db_producto.costos, key, value)
            else:
                db_costos = models.ProductoCosto(**prod_in.costos.dict(), producto_id=db_producto.id)
                db.add(db_costos)

        db.commit()
        db.refresh(db_producto)
        return ProductoService.calculate_prices(db_producto)

    @staticmethod
    def hard_delete_producto(db: Session, producto_id: int):
        """[LEY DE VIRGINIDAD UNIVERSAL - PIN 1974]"""
        db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
        if not db_producto: raise HTTPException(status_code=404, detail="Producto no encontrado")

        # 1. Check Bit 1 (VIRGINITY) — usando ProductoFlags soberano
        is_virgin = (db_producto.flags_estado & ProductoFlags.VIRGINITY)

        # 2. Check Physical dependencies (PedidoItems)
        from backend.pedidos.models import PedidoItem
        has_history = db.query(PedidoItem).filter(PedidoItem.producto_id == producto_id).first()

        if not is_virgin or has_history:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="VIOLACIÓN DE LEY DE VIRGINIDAD: No se puede eliminar físicamente un producto con historial o que no sea virgen [PIN 1974]."
            )

        db.delete(db_producto)
        db.commit()
        return True
