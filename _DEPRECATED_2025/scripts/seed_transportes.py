
import sys
import os

# Ajustar PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.core.database import SessionLocal, engine
# Importar modelos relacionados para registro en SQLAlchemy
from backend.maestros.models import Provincia 
from backend.logistica.models import EmpresaTransporte

# Transportes Comunes
TRANSPORTES = [
    {"nombre": "Retira por el Local", "direccion": "Fábrica"},
    {"nombre": "Flete Propio (CABA/GBA)", "direccion": "Logística Interna"},
    {"nombre": "Via Cargo", "web_tracking": "https://www.viacargo.com.ar/tracking"},
    {"nombre": "Andreani", "web_tracking": "https://www.andreani.com"},
    {"nombre": "Cruz del Sur", "web_tracking": "https://www.cruzdelsur.com.ar"},
    {"nombre": "Transporte Snaider", "direccion": "Pompeya"},
    {"nombre": "Expreso Lujan", "direccion": "CABA"}
]

def seed_transportes():
    print("🚚 Sembrando Empresas de Transporte...")
    db = SessionLocal()
    try:
        for t in TRANSPORTES:
            existe = db.query(EmpresaTransporte).filter_by(nombre=t["nombre"]).first()
            if not existe:
                new_t = EmpresaTransporte(
                    nombre=t["nombre"],
                    direccion=t.get("direccion"),
                    web_tracking=t.get("web_tracking"),
                    activo=True
                )
                db.add(new_t)
                print(f"   + Transporte: {t['nombre']}")
        
        db.commit()
        print("✅ Transportes sembrados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error sembrando transportes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_transportes()
