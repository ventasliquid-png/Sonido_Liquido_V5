import sys
import os
import shutil
import pandas as pd
from sqlalchemy import delete

# Add the project root to the python path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine
from backend.productos.models import Producto

# Import pack script
from scripts.pack_for_git import backup_to_iowa as pack_valija

def execute_purge():
    local_db = "pilot.db"
    backup_db = "pilot_pre_purge.db"
    excel_file = "productos_V5_purificado.xlsx"
    
    print("--- INICIANDO PROTOCOLO DE PURGA MASIVA ---")
    
    # 1. Backup de Seguridad
    if os.path.exists(local_db):
        try:
            shutil.copy2(local_db, backup_db)
            print(f"✅ Backup de seguridad creado: {backup_db}")
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return
    else:
        print(f"❌ No se encuentra la base de datos: {local_db}")
        return

    # 2. Leer CSV/Excel
    try:
        print(f"Leyendo archivo de decisiones: {excel_file}")
        df = pd.read_excel(excel_file)
        
        # Identify decision column (Index 6 -> Unnamed: 6)
        if len(df.columns) <= 6:
            print("❌ El archivo no tiene suficientes columnas (se requiere índice 6)")
            return
            
        decision_col = df.columns[6]
        print(f"Columna de decisión detectada: '{decision_col}'")
        
        # Filter for 'n' or 'N'
        to_delete = df[
            df[decision_col].astype(str).str.lower().str.strip() == 'n'
        ]
        
        ids_to_purge = to_delete['ID_PRODUCTO'].tolist()
        count_purge = len(ids_to_purge)
        
        print(f"🎯 Blancos identificados para eliminación: {count_purge}")
        
        if count_purge == 0:
            print("No hay productos marcados con 'n'. Abortando.")
            return

    except Exception as e:
        print(f"❌ Error leyendo archivo Excel: {e}")
        return

    # 3. Ejecutar Delete
    db = SessionLocal()
    try:
        initial_count = db.query(Producto).count()
        print(f"Población inicial: {initial_count} productos")
        
        print(f"⚡ Ejecutando DELETE masivo de {count_purge} registros...")
        
        # Bulk delete using SQLAlchemy Core for efficiency given IDs
        # Sync session false is usually faster but need to be careful with cascading if not using ORM delete
        # However, for pure bulk delete by ID, query.delete() is standard.
        
        # Using ORM query delete
        # synchronize_session=False is required if we are not fetching objects
        deleted_count = db.query(Producto).filter(Producto.id.in_(ids_to_purge)).delete(synchronize_session=False)
        
        db.commit()
        
        final_count = db.query(Producto).count()
        print(f"✅ Eliminación completada. Registros borrados: {deleted_count}")
        print(f"Población final: {final_count} productos")
        
        if deleted_count != count_purge:
            print(f"⚠️ Alerta: Se solicitaron eliminar {count_purge} pero se eliminaron {deleted_count}. (Posibles IDs inexistentes)")

    except Exception as e:
        print(f"❌ Error Crítico durante la purga: {e}")
        db.rollback()
    finally:
        db.close()
        
    # 4. Empaquetar Valija
    print("\n--- EJECUTANDO PACK_FOR_GIT ---")
    pack_valija()

if __name__ == "__main__":
    execute_purge()
