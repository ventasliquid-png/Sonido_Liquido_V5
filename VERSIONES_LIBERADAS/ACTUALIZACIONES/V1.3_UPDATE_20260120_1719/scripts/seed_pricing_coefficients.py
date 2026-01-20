
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from backend.core.database import SessionLocal
from backend.maestros.models import ListaPrecios

def seed_coefficients():
    db = SessionLocal()
    try:
        # Define Coeficientes Acordados (Standard Default)
        # Mayorista (Roca) = Base 1.0
        # Distribuidor = 1.0 (Same as Roca usually, or slight markup?) - User said "acordados", I'll set 1.0 for base.
        # Minorista Neto = 1.4 (40% markup)
        # Minorista Final = 1.7 (approx 40% + IVA) - But type is PRESUPUESTO usually.
        # Mayorista 1/2 IVA = 1.105 (Base + 10.5%)
        
        updates = {
            "Mayorista (Roca)": 1.0000,
            "Mayorista 1/2 IVA": 1.1050, # 10.5% added
            "Distribuidor": 1.2000,      # 20% markup
            "Minorista Neto": 1.5000,    # 50% markup
            "Minorista Final": 1.8150,   # 50% + 21% IVA approx
            "MELI": 1.9500,              # High markup for fees
            "Tienda Propia": 1.6000
        }
        
        print("--- Actualizando Coeficientes ---")
        for nombre, coef in updates.items():
            lista = db.query(ListaPrecios).filter(ListaPrecios.nombre == nombre).first()
            if lista:
                lista.coeficiente = coef
                print(f"Update {nombre} -> {coef}")
            else:
                # Create if missing?
                print(f"Skipping {nombre} (Not found)")
        
        db.commit()
        print("✅ Coeficientes actualizados.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_coefficients()
