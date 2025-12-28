import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.core.database import engine, Base, SessionLocal
from backend.proveedores import models as proveedores_models
from backend.logistica import models as logistica_models
from backend.maestros import models as maestros_models
from backend.productos import models as productos_models

def init_db():
    print("--- Inicializando Infraestructura Satelital ---")
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas sincronizadas.")
        
        db = SessionLocal()
        
        # Seed Unidades
        unidades = [
            {"codigo": "UN", "nombre": "Unidad"},
            {"codigo": "L", "nombre": "Litro"},
            {"codigo": "KG", "nombre": "Kilogramo"},
            {"codigo": "CAJA", "nombre": "Caja"},
            {"codigo": "BULTO", "nombre": "Bulto Cerrado"},
            {"codigo": "MT", "nombre": "Metro"},
            {"codigo": "M2", "nombre": "Metro Cuadrado"},
            {"codigo": "M3", "nombre": "Metro Cúbico"},
        ]
        
        print("🌱 Sembrando Unidades...")
        for u in unidades:
            exists = db.query(maestros_models.Unidad).filter_by(codigo=u["codigo"]).first()
            if not exists:
                db.add(maestros_models.Unidad(**u))
        
        # Seed Tasas IVA
        tasas = [
            {"nombre": "General 21%", "valor": 21.00},
            {"nombre": "Reducido 10.5%", "valor": 10.50},
            {"nombre": "Exento 0%", "valor": 0.00},
            {"nombre": "Super Reducido 2.5%", "valor": 2.50},
            {"nombre": "General 27%", "valor": 27.00},
        ]
        
        print("🌱 Sembrando Tasas IVA...")
        for t in tasas:
            exists = db.query(maestros_models.TasaIVA).filter_by(nombre=t["nombre"]).first()
            if not exists:
                db.add(maestros_models.TasaIVA(**t))
                
        # Seed Deposito Central
        print("🌱 Sembrando Depósito Central...")
        deposito_central = db.query(logistica_models.Deposito).filter_by(nombre="CENTRAL").first()
        if not deposito_central:
            db.add(logistica_models.Deposito(nombre="CENTRAL", tipo="FISICO"))

        db.commit()
        print("✅ Semillas plantadas exitosamente.")
        db.close()

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error al inicializar satélites: {e}")

if __name__ == "__main__":
    init_db()
