import unicodedata
import re
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, cast, String
from fastapi import HTTPException, status
from typing import List, Optional
from backend.productos import models, schemas
from backend.productos.models import ProductFlags
from backend.pricing_engine import calculate_lists

class ProductoService:
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        [GY-FIX-V16.2] Protocolo de Tokenización Alfabética (Bag of Words - Blindaje Nike).
        Remueve acentos, unifica siglas (quita puntos), tokeniza por palabras,
        elimina ruido (<2 chars), ordena alfabéticamente y sella la cadena única.
        """
        if not name: return ""
        
        # 1. Normalización Unicode (Mata acentos)
        text = unicodedata.normalize('NFKD', str(name))
        text = text.encode('ASCII', 'ignore').decode('ASCII').upper()
        
        # 2. Unificación de Siglas: "S.R.L." -> "SRL" antes de tokenizar
        text = text.replace('.', '')
        
        # 3. Tokenización: Reemplazar todo lo no-alfanumérico por ESPACIO
        text = re.sub(r'[^A-Z0-9]', ' ', text)
        tokens = text.split()
        
        # 4. Limpieza de Ruido (Filtramos palabras de 1 solo caracter)
        tokens = [t for t in tokens if len(t) >= 2]
        
        # 5. Ordenamiento Alfabético [EL TALLER SRL] -> [EL, SRL, TALLER]
        tokens.sort()
        
        # 6. Sellado: Unir sin espacios
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
        producto.precio_mayorista = listas.get('lista_1', 0)    # Referencia Base
        producto.precio_distribuidor = listas.get('lista_3', 0) # Referencia Distribuidor
        producto.precio_minorista = listas.get('lista_5', 0)    # Referencia Público
        
        return producto

    @staticmethod
    def get_producto(db: Session, producto_id: int) -> Optional[models.Producto]:
        return db.query(models.Producto).options(
            joinedload(models.Producto.costos), 
            joinedload(models.Producto.rubro)
        ).filter(models.Producto.id == producto_id).first()

    @staticmethod
    def create_producto(db: Session, producto_in: schemas.ProductoCreate) -> models.Producto:
        # 1. Validar Nombre Canónico (BOW)
        if ProductoService.check_duplicate_name(db, producto_in.nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"BLOQUEO DE DUPLICADO (BOW): El producto '{producto_in.nombre}' ya existe semánticamente."
            )

        # 2. Crear Producto
        producto_data = producto_in.dict(exclude={'costos'})
        db_producto = models.Producto(**producto_data)
        
        # Asignar Canon Name
        db_producto.nombre_canon = ProductoService.normalize_name(producto_in.nombre)
        
        # Auto-assign SKU if missing
        if not db_producto.sku:
            max_sku = db.query(func.max(models.Producto.sku)).scalar()
            try:
                db_producto.sku = int(max_sku or 10000) + 1
            except (ValueError, TypeError):
                db_producto.sku = 10001
        
        # [PROTOCOL FÉNIX] Set Flags: Active & Virgin
        db_producto.flags_estado = ProductFlags.IS_ACTIVE | ProductFlags.IS_VIRGIN

        db.add(db_producto)
        db.commit()
        db.refresh(db_producto)
        
        # 3. Crear Costos
        costos_data = producto_in.costos.dict()
        db_costos = models.ProductoCosto(**costos_data, producto_id=db_producto.id)
        db.add(db_costos)
        db.commit()
        
        db.refresh(db_producto)
        return ProductoService.calculate_prices(db_producto)

    @staticmethod
    def update_producto(db: Session, producto_id: int, producto_in: schemas.ProductoUpdate) -> models.Producto:
        db_producto = ProductoService.get_producto(db, producto_id)
        if not db_producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # 1. Validar Nombre Canónico si cambia
        if producto_in.nombre and producto_in.nombre != db_producto.nombre:
            if ProductoService.check_duplicate_name(db, producto_in.nombre, exclude_id=producto_id):
                 raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"BLOQUEO DE DUPLICADO (BOW): El nuevo nombre '{producto_in.nombre}' ya existe."
                )
            db_producto.nombre_canon = ProductoService.normalize_name(producto_in.nombre)

        # 2. Update Basic Fields
        update_data = producto_in.dict(exclude_unset=True, exclude={'costos'})
        for key, value in update_data.items():
            setattr(db_producto, key, value)
        
        # 3. Update Costs
        if producto_in.costos:
            if db_producto.costos:
                 costos_data = producto_in.costos.dict(exclude_unset=True)
                 for key, value in costos_data.items():
                     setattr(db_producto.costos, key, value)
            else:
                 costos_data = producto_in.costos.dict()
                 db_costos = models.ProductoCosto(**costos_data, producto_id=db_producto.id)
                 db.add(db_costos)

        db.commit()
        db.refresh(db_producto)
        return ProductoService.calculate_prices(db_producto)

    @staticmethod
    def reactivate_producto(db: Session, producto_id: int, confirm: bool = False) -> models.Producto:
        """
        [PROTOCOLO FÉNIX] Lógica de Doble Aceptación para reactivación.
        """
        db_producto = db.query(models.Producto).get(producto_id)
        if not db_producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if db_producto.activo:
            return db_producto

        # Si no se ha confirmado explícitamente (Doble Aceptación)
        if not confirm:
            # Aquí podríamos verificar colisiones de SKU o Nombre antes de pedir confirmación
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doble Aceptación Requerida: ¿Está seguro que desea reactivar este SKU?"
            )
        
        db_producto.activo = True
        db_producto.flags_estado |= ProductFlags.IS_ACTIVE
        db.commit()
        return db_producto

    @staticmethod
    def hard_delete_producto(db: Session, producto_id: int):
        """
        [LEY DE VIRGINIDAD] Borrado físico condicional.
        """
        db_producto = db.query(models.Producto).get(producto_id)
        if not db_producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Validar Bit 1 (IS_VIRGIN) - Valor 2
        is_virgin = (db_producto.flags_estado & ProductFlags.IS_VIRGIN)
        
        if not is_virgin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="VIOLACIÓN DE LEY DE VIRGINIDAD: El producto no es virgen. Borrado físico prohibido."
            )
            
        db.delete(db_producto)
        db.commit()
        return True
