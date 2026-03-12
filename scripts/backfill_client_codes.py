import sys
import os
import logging
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Force SQLite for Script
os.environ["DATABASE_URL"] = "sqlite:///./pilot_v5x.db"

from backend.core.database import SessionLocal

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backfill_client_codes():
    logger.info("🦅 INICIANDO PROTOCOLO DE REPARACIÓN DE CÓDIGOS (BACKFILL - RAW SQL)")
    
    # Connect
    try:
        db = SessionLocal()
    except Exception as e:
        logger.error(f"❌ Error conectando a DB: {e}")
        return
    
    try:
        # 1. Get Max Code (Raw SQL)
        # Check if table exists/columns by running a simple query first if needed, but we assume schema is okay.
        logger.info("📊 Consultando MAX(codigo_interno)...")
        result = db.execute(text("SELECT MAX(codigo_interno) FROM clientes"))
        max_code = result.scalar() or 0
        logger.info(f"📊 Último Código Usado: {max_code}")
        
        current_code = int(max_code) + 1
        
        # 2. Get Clients with NULL Code (Raw SQL)
        logger.info("🔍 Buscando clientes sin código...")
        clients_result = db.execute(text("SELECT id, razon_social FROM clientes WHERE codigo_interno IS NULL ORDER BY razon_social"))
        clients = clients_result.fetchall()
        
        if not clients:
            logger.info("✅ No se encontraron clientes sin código. El sistema está sano.")
            return

        logger.info(f"⚠️ Se detectaron {len(clients)} clientes sin código. Procediendo a asignar...")
        
        for row in clients:
            client_id = row[0]
            razon_social = row[1]
            
            logger.info(f"✨ Asignando #{current_code} a: {razon_social}")
            
            # Update
            db.execute(
                text("UPDATE clientes SET codigo_interno = :code WHERE id = :id"),
                {"code": current_code, "id": client_id}
            )
            current_code += 1
            
        # 3. Commit
        db.commit()
        logger.info("💾 CAMBIOS GUARDADOS EXITOSAMENTE.")
        
    except Exception as e:
        logger.error(f"❌ Error durante el backfill: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_client_codes()
