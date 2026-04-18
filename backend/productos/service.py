import unicodedata
import re
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
    def normalize_name(name: str) -> str:
        """
        [GY-V16.2 → UTI-64bit] Protocolo de Tokenización Alfabética (Bag of Words).
        Remueve acentos, unifica siglas, tokeniza, elimina ruido y ordena alfabéticamente.
        """
        if not name: return ""
        text = unicodedata.normalize('NFKD', str(name))
        text = text.encode('ASCII', 'ignore').decode('ASCII').upper()
        text = text.replace('.', '')
        text = re.sub(r'[^A-Z0-9]', ' ', text)
        tokens = text.split()
        tokens = [t for t in tokens if len(t) >= 2]
        tokens.sort()
        return "".join(tokens)

    @staticmethod
    def check_duplicate_name(db: Session, name: str, exclude_id: int = None) -> bool:
        """Verifica si existe un producto con el mismo nombre canónico (BOW)."""
        canon_name = ProductoService.normalize_name(name)
        if not canon_name:
            return False
        query = db.query(models.Producto).filter(models.Producto.nombre_canon == canon_name)
        if exclude_id:
            query = query.filter(models.Producto.id != exclude_id)
        return query.first() is not None

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
    def list_rubros(db: Session, skip: int = 0, limit: int = 100, include_banned: bool = False):
        query = db.query(models.Rubro)
        if not include_banned:
            # [V5.9 GOLD] Ocultar borrados lógicos por defecto (Bit 2 = 4)
            query = query.filter((models.Rubro.flags_estado.op('&')(4) == 0))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def _auto_codigo(db: Session, nombre: str) -> str:
        """[AUTO-CODIGO V5.9] Genera un código de 3 chars único a partir del nombre."""
        import re as _re
        base = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII').upper()
        base = _re.sub(r'[^A-Z0-9]', '', base)[:3].ljust(3, 'X')
        candidate = base
        suffix = 1
        while db.query(models.Rubro).filter(models.Rubro.codigo == candidate).first():
            candidate = base[:2] + str(suffix)
            suffix += 1
        return candidate

    @staticmethod
    def create_rubro(db: Session, rubro_in: schemas.RubroCreate):
        # [AUTO-CODIGO V5.9] Si no viene código, generarlo automáticamente
        if not rubro_in.codigo:
            rubro_in.codigo = ProductoService._auto_codigo(db, rubro_in.nombre)

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

        # [V5.9 ADOPCIÓN] Si el operador re-asigna rubro explícitamente, limpiar flag EXPATRIADO (Bit 3)
        if 'rubro_id' in prod_data and (db_producto.flags_estado & 8):
            db_producto.flags_estado = db_producto.flags_estado & ~8

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
    def reactivate_producto(db: Session, producto_id: int, confirm: bool = False) -> models.Producto:
        """[PROTOCOLO FÉNIX] Doble Aceptación para reactivación."""
        db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
        if not db_producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if db_producto.activo:
            return db_producto

        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doble Aceptación Requerida: ¿Está seguro que desea reactivar este SKU?"
            )

        db_producto.activo = True
        db_producto.flags_estado |= ProductoFlags.IS_ACTIVE  # [64-bit] ProductoFlags soberano
        db.commit()
        return db_producto

    @staticmethod
    def hard_delete_producto(db: Session, producto_id: int):
        """[LEY DE VIRGINIDAD UNIVERSAL - PIN 1974]
        Doble guarda:
        1. Bit VIRGINITY (flags_estado & 2) — marca soberana seteada en creación,
           limpiada en primera operación. Ausencia de PedidoItem no equivale a virginidad
           (un pedido hard-deleted borra sus items en cascade).
        2. PedidoItem — dependencias físicas actuales.
        3. [V5.8 GOLD] Respaldo en PapeleraRegistro antes de eliminación.
        """
        from backend.core.models import PapeleraRegistro
        from backend.pedidos.models import PedidoItem
        from backend.clientes.models import Cliente
        from backend.logistica.models import EmpresaTransporte
        from datetime import datetime
        import json
        import uuid

        db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
        if not db_producto: raise HTTPException(status_code=404, detail="Producto no encontrado")

        # 1. Check Bit 1 (VIRGINITY) — marca soberana
        is_virgin = (db_producto.flags_estado or 0) & ProductoFlags.VIRGINITY

        # 2. Check dependencias físicas actuales
        has_history = db.query(PedidoItem).filter(PedidoItem.producto_id == producto_id).first()

        if not is_virgin or has_history:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="VIOLACIÓN DE LEY DE VIRGINIDAD: No se puede eliminar físicamente un producto con historial o que no sea virgen [PIN 1974]."
            )

        try:
            # 3. Serializar para Papelera (Sincronizado con ClienteService)
            def json_safe(obj):
                if isinstance(obj, dict):
                    return {k: json_safe(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [json_safe(v) for v in obj]
                elif isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, (datetime, uuid.UUID)):
                    return str(obj)
                return obj

            prod_dict = {}
            for column in db_producto.__table__.columns:
                prod_dict[column.name] = getattr(db_producto, column.name)
            
            prod_dict = json_safe(prod_dict)

            # 4. Guardar en Papelera (Entidad ID como String para soportar Integer)
            trash_entry = PapeleraRegistro(
                entidad_tipo='PRODUCTO',
                entidad_id=str(db_producto.id), # Cast to string for GUID compatibility
                data=prod_dict,
                borrado_por="MASTER_TOOLS_PIN_1974"
            )
            db.add(trash_entry)
            
            print(f"[TRASH] Preparando borrado de Producto {db_producto.nombre} (SKU: {db_producto.sku})")

            # 5. Borrado físico real
            db.delete(db_producto)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[X] CRITICAL PRODUCT TRASH ERROR: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"ERROR INTERNO (Papelera/DB): {str(e)}"
            )

    @staticmethod
    def hard_delete_rubro(db: Session, rubro_id: int):
        """[LEY DE VIRGINIDAD - RUBROS]
        Permite el borrado físico de un rubro si no tiene dependencias.
        """
        from backend.core.models import PapeleraRegistro
        import json

        db_rubro = db.query(models.Rubro).filter(models.Rubro.id == rubro_id).first()
        if not db_rubro: raise HTTPException(status_code=404, detail="Rubro no encontrado")

        # Check dependencias
        has_hijos = db.query(models.Rubro).filter(models.Rubro.padre_id == rubro_id).first()
        has_prods = db.query(models.Producto).filter(models.Producto.rubro_id == rubro_id).first()

        if has_hijos or has_prods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar físicamente un rubro con hijos o productos asociados. Mígrelos primero."
            )

        try:
            # Serializar para Papelera (convertir tipos no JSON-serializables)
            rubro_dict = {}
            for column in db_rubro.__table__.columns:
                val = getattr(db_rubro, column.name)
                if isinstance(val, Decimal):
                    val = float(val)
                elif hasattr(val, 'isoformat'):
                    val = val.isoformat()
                rubro_dict[column.name] = val

            trash_entry = PapeleraRegistro(
                entidad_tipo='RUBRO',
                entidad_id=str(db_rubro.id),
                data=rubro_dict,
                borrado_por="MASTER_TOOLS_PIN_1974"
            )
            db.add(trash_entry)
            db.delete(db_rubro)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
