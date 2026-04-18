from sqlalchemy import text
from backend.core.database import engine, SessionLocal
from backend.productos.service import ProductoService
from backend.productos import models
import traceback

def run_migration():
    print(f"--- [MIGRACION FENIX] Actualizando Base de Datos Remota ---")
    
    with engine.connect() as connection:
        # 1. Agregar nombre_canon
        try:
            connection.execute(text("ALTER TABLE productos ADD COLUMN nombre_canon VARCHAR(150)"))
            connection.commit()
            print("[MOD] Columna 'nombre_canon' añadida a 'productos'.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicada" in str(e).lower():
                print("[SKIP] Columna 'nombre_canon' ya existe.")
            else:
                print(f"[ERROR] Al añadir nombre_canon: {e}")

        # 2. Crear Índice
        try:
            connection.execute(text("CREATE INDEX idx_productos_nombre_canon ON productos(nombre_canon)"))
            connection.commit()
            print("[MOD] Indice 'idx_productos_nombre_canon' creado.")
        except Exception as e:
             if "already exists" in str(e).lower() or "ya existe" in str(e).lower():
                print("[SKIP] Indice 'idx_productos_nombre_canon' ya existe.")
             else:
                print(f"[ERROR] Al crear indice: {e}")

    # 3. Normalizar productos existentes
    print("[RUN] Iniciando normalizacion de productos existentes...")
    db = SessionLocal()
    try:
        prods = db.query(models.Producto).all()
        count = 0
        for p in prods:
            if not p.nombre_canon:
                p.nombre_canon = ProductoService.normalize_name(p.nombre)
                count += 1
        db.commit()
        print(f"[MOD] {count} productos normalizados.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] En normalizacion: {e}")
        traceback.print_exc()
    finally:
        db.close()
        
    print("--- [FIN MIGRACION] ---")

if __name__ == "__main__":
    run_migration()
