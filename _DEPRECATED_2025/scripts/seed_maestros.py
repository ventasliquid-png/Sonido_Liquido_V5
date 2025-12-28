
import sys
import os

# Ajustar PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.core.database import SessionLocal, engine
from backend.maestros.models import CondicionIva, Segmento, Provincia, TipoContacto

# Datos Maestros Esenciales (Hardcoded por seguridad operativa)
CONDICIONES_IVA = [
    "Responsable Inscripto",
    "Monotributista",
    "Exento",
    "Consumidor Final",
    "Sujeto No Categorizado"
]

SEGMENTOS = [
    "General",
    "Salud",
    "Industria",
    "Gastronomía",
    "Gobierno"
]

PROVINCIAS = [
    ("B", "Buenos Aires"),
    ("C", "CABA"),
    ("X", "Córdoba"),
    ("S", "Santa Fe"),
    ("M", "Mendoza")
]

TIPOS_CONTACTO = [
    ("COMPRAS", "Jefe de Compras"),
    ("PAGOS", "Cuentas a Pagar"),
    ("DUEÑO", "Dueño / Socio"),
    ("CALIDAD", "Resp. Calidad")
]

def seed_maestros():
    print("🌱 Iniciando Siembra de Maestros Esenciales...")
    db = SessionLocal()
    try:
        # 1. Condiciones IVA
        for nombre in CONDICIONES_IVA:
            existe = db.query(CondicionIva).filter_by(nombre=nombre).first()
            if not existe:
                db.add(CondicionIva(nombre=nombre))
                print(f"   + Iva: {nombre}")
        
        # 2. Segmentos
        for nombre in SEGMENTOS:
            existe = db.query(Segmento).filter_by(nombre=nombre).first()
            if not existe:
                db.add(Segmento(nombre=nombre, descripcion="Segmento Base"))
                print(f"   + Segmento: {nombre}")

        # 3. Provincias
        for codigo, nombre in PROVINCIAS:
            existe = db.query(Provincia).filter_by(id=codigo).first()
            if not existe:
                db.add(Provincia(id=codigo, nombre=nombre))
                print(f"   + Provincia: {nombre}")

        # 4. Tipos de Contacto
        for cod, nombre in TIPOS_CONTACTO:
            existe = db.query(TipoContacto).filter_by(id=cod).first()
            if not existe:
                db.add(TipoContacto(id=cod, nombre=nombre))
                print(f"   + Tipo Contacto: {nombre}")

        db.commit()
        print("✅ Maestros sembrados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error sembrando maestros: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_maestros()
