# [IDENTIDAD] - scripts\reparacion\repair_canon_identities.py
# Versión: V1.0 | Protocolo Nike | PIN 1974
# ---------------------------------------------------------

import sys
import os
from pathlib import Path

# Configurar Path para importar backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.clientes.service import ClienteService
# Importar modelos relacionados para evitar errores de registro en SQLAlchemy
from backend.logistica import models as logistica_models
from backend.maestros import models as maestros_models
from backend.pedidos import models as pedidos_models
from backend.productos import models as productos_models

def repair_identities():
    db = SessionLocal()
    try:
        print("--- [OPERACIÓN SANEAMIENTO] Iniciando Canonización de Clientes ---")
        clientes = db.query(Cliente).all()
        count = 0
        collisions = []
        canon_map = {} # canon -> [razon_social, ...]

        for c in clientes:
            canon = ClienteService.normalize_name(c.razon_social)
            
            # Detectar colisión en memoria antes de intentar guardar
            if canon and canon not in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
                if canon in canon_map:
                    collisions.append({
                        "canon": canon,
                        "original": canon_map[canon],
                        "duplicate": c.razon_social,
                        "id_orig": str(db.query(Cliente).filter(Cliente.razon_social == canon_map[canon]).first().id if db.query(Cliente).filter(Cliente.razon_social == canon_map[canon]).first() else "???"),
                        "id_dup": str(c.id)
                    })
                else:
                    canon_map[canon] = c.razon_social

            # Actualizar en DB
            c.razon_social_canon = canon
            count += 1
            if count % 10 == 0:
                print(f"Procesados: {count}...")

        try:
            db.commit()
            print(f"\nEXITO: {count} clientes canonizados correctamente.")
        except Exception as e:
            db.rollback()
            print(f"\nERROR AL GUARDAR: {e}")
            print("Es probable que existan duplicados exactos que impiden el indice UNIQUE.")

    finally:
        db.close()

if __name__ == "__main__":
    repair_identities()
