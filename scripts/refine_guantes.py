
import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append('c:\\dev\\Sonido_Liquido_V5')

from backend.core.database import SessionLocal
from backend.maestros.models import Unidad, TasaIVA
from backend.productos.models import Rubro
from backend.proveedores.models import Proveedor

def refine_guantes():
    db = SessionLocal()
    try:
        # 1. Find GUANTES (currently a subrubro of ROPA DESCARTABLE usually, but code is GUA)
        guantes = db.query(Rubro).filter(Rubro.codigo == "GUA").first()
        
        if not guantes:
            print("Rubro GUANTES (GUA) not found.")
            return

        print(f"Found GUANTES: {guantes.nombre} (Padre ID: {guantes.padre_id})")

        # 2. Promote to Root
        if guantes.padre_id is not None:
            guantes.padre_id = None
            db.commit()
            print("  Promoted GUANTES to Root (Padre ID set to None).")
        else:
            print("  GUANTES is already a Root.")

        # 3. Create Subrubros for GUANTES
        subs = [
            {"nombre": "Examinación", "codigo": "GEX"},
            {"nombre": "Cirugía", "codigo": "GCI"},
            {"nombre": "Protección de Corte", "codigo": "GCO"}
        ]

        for s in subs:
            # Check exist
            exists = db.query(Rubro).filter(Rubro.codigo == s["codigo"]).first()
            if not exists:
                new_sub = Rubro(
                    nombre=s["nombre"],
                    codigo=s["codigo"],
                    padre_id=guantes.id,
                    activo=True
                )
                db.add(new_sub)
                db.commit()
                print(f"  Created Subrubro: {s['nombre']}")
            else:
                 print(f"  Subrubro exists: {s['nombre']}")
                 if exists.padre_id != guantes.id:
                     exists.padre_id = guantes.id
                     db.commit()
                     print(f"    Relinked {s['nombre']} to GUANTES")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    refine_guantes()
