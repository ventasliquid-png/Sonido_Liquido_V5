
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
from backend.maestros import models

def seed_masters():
    db = SessionLocal()
    print("--- [SEED] Dynamic Masters (Units & IVA) ---")
    
    # 1. Units
    # Format: (codigo, nombre)
    units_data = [
        ("07", "Unidad"),
        ("01", "Kilogramo"),
        ("02", "Metro"),
        ("05", "Litro"),
        ("08", "Par"),
        ("62", "Pack")
    ]
    
    for code, name in units_data:
        try:
            exists = db.query(models.Unidad).filter(models.Unidad.codigo == code).first()
            if not exists:
                print(f"[NEW] Unidad: {name} ({code})")
                db.add(models.Unidad(codigo=code, nombre=name))
            else:
                print(f"[SKIP] Unidad: {name} exists.")
        except Exception as e:
            print(f"[ERROR] Unidad {name}: {e}")

    # 2. IVA
    # Format: (nombre, valor)
    iva_data = [
        ("IVA 21%", 21.0),
        ("IVA 10.5%", 10.5),
        ("IVA 27%", 27.0),
        ("IVA 0%", 0.0)
    ]

    for name, value in iva_data:
        try:
            # Check by value to avoid duplicates if name differs slighly
            exists = db.query(models.TasaIVA).filter(models.TasaIVA.valor == value).first()
            if not exists:
                print(f"[NEW] IVA: {name} ({value}%)")
                db.add(models.TasaIVA(nombre=name, valor=value))
            else:
                print(f"[SKIP] IVA {value}% exists.")
        except Exception as e:
            print(f"[ERROR] IVA {name}: {e}")

    db.commit()
    db.close()
    print("--- [SEED] Completed ---")

if __name__ == "__main__":
    seed_masters()
