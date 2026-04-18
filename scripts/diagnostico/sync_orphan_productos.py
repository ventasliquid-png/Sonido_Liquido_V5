import sqlite3
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, engine
from backend.productos import models, schemas
from backend.productos.service import ProductoService
from backend.productos.models import ProductFlags, Rubro
import os

SOURCE_DB = r'C:\dev\v5-ls-Tom\V5_RELEASE_09\V5_LS_MASTER.db'
# We will now sync ALL products from this source instead of using the text list,
# since this is the confirmed 'Cantera/Master' with 45 items.
MIGRATION_RUBRO_NAME = '[Z-MIGRACION-FENIX]'

def sync_orphans():
    print(f"--- [PROTOCOLO FENIX] Iniciando Sincronizacion desde V5_LS_MASTER ---")
    
    if not os.path.exists(SOURCE_DB):
        print(f"ERROR: No se encontro la base de origen en {SOURCE_DB}")
        return

    db: Session = SessionLocal()
    
    # 2. Asegurar Rubro de Migración
    rubro_migracion = db.query(Rubro).filter(Rubro.nombre == MIGRATION_RUBRO_NAME).first()
    if not rubro_migracion:
        print(f"[MOD] Creando rubro temporal {MIGRATION_RUBRO_NAME}")
        rubro_migracion = Rubro(codigo='ZMF', nombre=MIGRATION_RUBRO_NAME, activo=True)
        db.add(rubro_migracion)
        db.commit()
        db.refresh(rubro_migracion)

    # 3. Conectar a Base de Origen
    conn = sqlite3.connect(SOURCE_DB)
    cursor = conn.cursor()
    
    # 3.1 Obtener todos los productos de origen
    cursor.execute("SELECT sku, nombre, descripcion, codigo_visual, rubro_id, activo FROM productos")
    source_products = cursor.fetchall()
    
    print(f"[SOURCE] Detectados {len(source_products)} productos en origen.")

    stats = {"created": 0, "skipped": 0, "collision": 0}

    for row in source_products:
        sku, nombre, descripcion, codigo_visual, old_rubro_id, activo = row
        
        # 3.5 Verificar si ya existe en destino (por SKU si existe, o por BOW)
        existing_in_target = None
        if sku:
            existing_in_target = db.query(models.Producto).filter(models.Producto.sku == sku).first()
        
        if not existing_in_target:
            if ProductoService.check_duplicate_name(db, nombre):
                 print(f"[BOW] COLISION DETECTADA: '{nombre}' ya existe en destino.")
                 stats["collision"] += 1
                 continue
        else:
            print(f"[SKIP] SKU {sku} ya existe en el destino.")
            stats["skipped"] += 1
            continue
            
        # 4. Inserción Quirúrgica
        # Intentaremos buscar en productos_costos de origen
        cursor.execute("SELECT costo_reposicion, rentabilidad_target FROM productos_costos WHERE producto_id = (SELECT id FROM productos WHERE nombre = ?)", (nombre,))
        # (Nota: usamos nombre como fallback de búsqueda si el ID cambió, pero es frágil. 
        #  Mejor buscar por el mismo ID original si el esquema es idéntico)
        
        costo_row = cursor.fetchone()
        costo_reposicion = costo_row[0] if costo_row else 0
        rentabilidad = costo_row[1] if costo_row else 30

        # Si el SKU es None, generamos uno masivo
        if not sku:
             max_sku = db.query(func.max(models.Producto.sku)).scalar()
             sku = int(max_sku or 50000) + 1

        new_prod = models.Producto(
            sku=sku,
            nombre=nombre,
            nombre_canon=ProductoService.normalize_name(nombre),
            descripcion=descripcion,
            codigo_visual=codigo_visual if codigo_visual and str(codigo_visual).strip() != '' else None,
            rubro_id=rubro_migracion.id,
            tipo_producto='VENTA',
            presentacion_compra=None,
            unidades_bulto=1,
            tasa_iva_id=1, # Default 21%
            stock_fisico=0,
            stock_reservado=0,
            unidad_medida='UN',
            activo=bool(activo),
            flags_estado=ProductFlags.IS_ACTIVE | ProductFlags.IS_VIRGIN 
        )
        
        db.add(new_prod)
        db.flush() 
        
        new_costo = models.ProductoCosto(
            producto_id=new_prod.id,
            costo_reposicion=costo_reposicion,
            rentabilidad_target=rentabilidad,
            precio_roca=0 
        )
        db.add(new_costo)
        
        stats["created"] += 1
        print(f"[OK] Inyectado SKU {sku}: {nombre}")

    db.commit()
    conn.close()
    
    print(f"\n--- REPORTE FINAL ---")
    print(f"Nuevos Productos: {stats['created']}")
    print(f"Colisiones BOW: {stats['collision']}")
    print(f"No encontrados en origen: {stats['skipped']}")
    print(f"Total procesados: {len(orphan_skus)}")

if __name__ == "__main__":
    sync_orphans()
