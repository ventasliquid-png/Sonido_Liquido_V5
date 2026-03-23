import os
import sys
import uuid
from datetime import datetime, timezone

# ROOT_DIR as in main.py
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

# Force SQLite
abs_db_path = os.path.abspath(os.path.join(ROOT_DIR, "pilot_v5x.db"))
os.environ["DATABASE_URL"] = f"sqlite:///{abs_db_path}"

from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, text, func
from backend.core.database import SessionLocal, engine
from backend.clientes.models import Cliente, Domicilio, domicilios_clientes
from backend.clientes.service import ClienteService

def seed_hub():
    db = SessionLocal()
    try:
        print("--- [SEED HUB]: Iniciando migración de domicilios... ---")
        
        # 0. Pre-load Registry
        import backend.auth.models
        import backend.maestros.models
        import backend.logistica.models
        import backend.productos.models
        import backend.clientes.models
        import backend.pedidos.models
        import backend.remitos.models
        import backend.agenda.models
        import backend.contactos.models
        import backend.proveedores.models
        import backend.core.models
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
        
        # 1. Fetch all active legacy domicilios
        print("--- [SEED HUB]: Buscando domicilios legacy... ---")
        legacy_doms = db.query(Domicilio).filter(Domicilio.cliente_id != None).all()
        print(f"--- [SEED HUB]: Encontrados {len(legacy_doms)} domicilios con cliente_id directo. ---")

        # 2. Normalization & Dedup Map
        # { "normalized_string": [dom1, dom2, ...] }
        dedup_map = {}
        for dom in legacy_doms:
            norm = ClienteService.normalize_address(dom.calle, dom.numero, dom.piso, dom.depto)
            if norm not in dedup_map:
                dedup_map[norm] = []
            dedup_map[norm].append(dom)

        print(f"--- [SEED HUB]: {len(dedup_map)} domicilios únicos detectados. ---")

        # 3. Process each group
        for norm, group in dedup_map.items():
            # The "Master" Domicilio for this address
            master = group[0]
            
            for dom in group:
                # Every client linked to any dom in this group should be linked to 'master' in N:M
                if not dom.cliente_id: continue
                
                # Link client to master
                # flags = 2097152 (Bit 21 ON)
                flags = 2097152
                alias = dom.alias or "MIGRADO"
                
                # Check if link already exists
                existing_link = db.query(domicilios_clientes).filter(
                    domicilios_clientes.c.cliente_id == dom.cliente_id,
                    domicilios_clientes.c.domicilio_id == master.id
                ).first()

                if not existing_link:
                    db.execute(
                        insert(domicilios_clientes).values(
                            cliente_id=dom.cliente_id,
                            domicilio_id=master.id,
                            flags=flags,
                            alias=alias,
                            es_predeterminado=dom.es_predeterminado or False
                        )
                    )
                else:
                    # Update flags to ensure Bit 21 is ON
                    db.execute(
                        domicilios_clientes.update().where(
                            domicilios_clientes.c.cliente_id == dom.cliente_id,
                            domicilios_clientes.c.domicilio_id == master.id
                        ).values(flags=flags)
                    )

        db.commit()
        print("--- [SEED HUB]: Siembra completada con éxito. ---")
        
    except Exception as e:
        db.rollback()
        print(f"--- [SEED HUB ERROR]: {e} ---")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_hub()
