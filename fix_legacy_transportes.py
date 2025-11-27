import sys
import os
from sqlalchemy import text

# Add project root and backend to path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal

def backfill_transportes():
    print("--- Backfilling Transportes (Raw SQL) ---")
    db = SessionLocal()
    try:
        # 1. Find "Retiro en Local" ID
        sql_find = text("SELECT id FROM empresas_transporte WHERE nombre ILIKE :nombre LIMIT 1")
        result = db.execute(sql_find, {"nombre": "%retiro%"}).fetchone()
        
        retiro_id = None
        if result:
            retiro_id = result[0]
            print(f"ℹ️ Found 'Retiro en Local' with ID: {retiro_id}")
        else:
            print("⚠️ 'Retiro en Local' not found. Creating it...")
            # Create it
            import uuid
            new_id = uuid.uuid4()
            sql_create = text("""
                INSERT INTO empresas_transporte (id, nombre, activo, requiere_carga_web, formato_etiqueta)
                VALUES (:id, 'RETIRO EN LOCAL', true, false, 'PROPIA')
            """)
            db.execute(sql_create, {"id": new_id})
            db.commit()
            retiro_id = new_id
            print(f"✅ Created 'RETIRO EN LOCAL' with ID: {retiro_id}")

        # 2. Update Domicilios
        sql_count = text("SELECT COUNT(*) FROM domicilios WHERE transporte_id IS NULL")
        count = db.execute(sql_count).scalar()
        print(f"Found {count} domicilios with missing transport.")

        if count > 0:
            sql_update = text("UPDATE domicilios SET transporte_id = :tid WHERE transporte_id IS NULL")
            db.execute(sql_update, {"tid": retiro_id})
            db.commit()
            print(f"✅ Updated {count} domiciles.")
        else:
            print("No updates needed.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_transportes()
