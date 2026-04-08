# [IDENTIDAD] - scripts\reparacion\re-canonizar_base.py
# Versión: V2.0 | Protocolo de Tokenización Alfabética | PIN 1974
# -----------------------------------------------------------------

import sys
import os
from pathlib import Path

# Configurar Path para importar backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.clientes.models import Cliente
from backend.clientes.service import ClienteService
# Importar modelos para evitar errores de registro en SQLAlchemy
from backend.logistica import models as logistica_models
from backend.maestros import models as maestros_models
from backend.pedidos import models as pedidos_models
from backend.productos import models as productos_models

def migrate_canons(db_path=None):
    if not db_path:
        db_path = os.getenv('DATABASE_PATH', r'C:\dev\Sonido_Liquido_V5\pilot_v5x.db')
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
    
    print(f"--- [MIGRACIÓN NUCLEAR V2.0] Database: {db_path} ---")
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        print("--- [MIGRACIÓN NUCLEAR V2.0] Iniciando Re-Canonización Alfabética ---")
        clientes = db.query(Cliente).all()
        count_updated = 0
        count_collisions = 0
        
        canon_map = {} # nuevo_canon -> [id, razon_social]
        
        print(f"Buscando colisiones en {len(clientes)} registros...")
        
        for c in clientes:
            old_canon = c.razon_social_canon
            new_canon = ClienteService.normalize_name(c.razon_social)
            
            # Detectar colisiones semánticas bajo el nuevo protocolo
            if new_canon and new_canon not in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
                if new_canon in canon_map:
                    orig = canon_map[new_canon]
                    print(f"!!! COLISIÓN DETECTADA:")
                    print(f"    - Nuevo Canon: {new_canon}")
                    print(f"    - Registro 1: {orig['razon_social']} (ID: {orig['id']})")
                    print(f"    - Registro 2: {c.razon_social} (ID: {c.id})")
                    count_collisions += 1
                else:
                    canon_map[new_canon] = {"id": str(c.id), "razon_social": c.razon_social}
            
            if old_canon != new_canon:
                c.razon_social_canon = new_canon
                count_updated += 1
        
        print(f"\nResumen de Auditoría:")
        print(f"- Total Clientes: {len(clientes)}")
        print(f"- Cánones a actualizar: {count_updated}")
        print(f"- Nuevas Colisiones Detectadas: {count_collisions}")
        
        if count_collisions > 0:
            print("\nADVERTENCIA: Se han detectado colisiones que antes estaban ocultas.")
            print("El commit se realizará, pero los registros colisionados podrían requerir fusión manual.")

        try:
            db.commit()
            print("\nEXITO: La base de datos ha sido re-canonizada correctamente.")
        except Exception as e:
            db.rollback()
            print(f"\nERROR AL GUARDAR: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    migrate_canons()
