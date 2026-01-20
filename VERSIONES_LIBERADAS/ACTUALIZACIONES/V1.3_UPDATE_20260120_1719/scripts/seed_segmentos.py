
import sys
import os
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal
from backend.maestros.models import Segmento

def seed_segmentos():
    db = SessionLocal()
    print("\n--- SEEDING SEGMENTOS ---")
    
    # Official Segments with their Levels
    data = [
        {"nombre": "General", "nivel": 1, "desc": "Lista Base (Mayorista)"},
        {"nombre": "Revendedor", "nivel": 2, "desc": "Lista 1/2 IVA"},
        {"nombre": "Distribuidor", "nivel": 3, "desc": "Lista Distribuidor"},
        {"nombre": "Retail", "nivel": 4, "desc": "Minorista Neto"},
        {"nombre": "Consumidor Final", "nivel": 5, "desc": "Minorista Final"},
        {"nombre": "E-Commerce", "nivel": 6, "desc": "MELI"},
        {"nombre": "Tienda Propia", "nivel": 7, "desc": "Tienda Propia"},
        {"nombre": "Alimentación", "nivel": 1, "desc": "Legacy - Mapped to 1"},
        {"nombre": "Salud", "nivel": 1, "desc": "Legacy - Mapped to 1"},
    ]
    
    for item in data:
        print(f"Checking: {item['nombre']}...")
        seg = db.query(Segmento).filter(Segmento.nombre == item["nombre"]).first()
        if not seg:
            print(f"➕ Creating: {item['nombre']}")
            new_seg = Segmento(
                nombre=item["nombre"],
                descripcion=item["desc"],
                nivel=item["nivel"],
                activo=True
            )
            db.add(new_seg)
        else:
            print(f"🔄 Updating: {item['nombre']} -> Level {item['nivel']}")
            seg.nivel = item["nivel"]
        
    db.commit()
    print("✅ Segmentos seeded.")
    db.close()

if __name__ == "__main__":
    seed_segmentos()
