
import sys
import os
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select

# Add project root to path
sys.path.append('c:\\dev\\Sonido_Liquido_V5')

from backend.core.database import SessionLocal, engine
from backend.maestros.models import Unidad, TasaIVA
from backend.productos.models import Rubro, Producto
from backend.proveedores.models import Proveedor # Fix relationship error

def seed_ropa_descartable():
    db = SessionLocal()
    try:
        # 1. Create Parent Rubro
        ropa_rubro = db.query(Rubro).filter(Rubro.nombre == "ROPA DESCARTABLE").first()
        if not ropa_rubro:
            ropa_rubro = Rubro(nombre="ROPA DESCARTABLE", codigo="RD", activo=True)
            db.add(ropa_rubro)
            db.commit()
            db.refresh(ropa_rubro)
            print(f"Created Rubro: {ropa_rubro.nombre}")
        else:
            print(f"Found Rubro: {ropa_rubro.nombre}")

        # 2. Create Subrubros
        subs = [
            {"nombre": "BARBIJOS", "codigo": "BAR"},
            {"nombre": "COFIAS", "codigo": "COF"},
            {"nombre": "CUBREZAPATOS", "codigo": "CUB"},
            {"nombre": "CAMISOLINES", "codigo": "CAM"},
            {"nombre": "GUANTES", "codigo": "GUA"}
        ]
        
        sub_map = {}

        for s in subs:
            # Try to find by code first (more stable) or name
            sub = db.query(Rubro).filter((Rubro.codigo == s["codigo"]) | (Rubro.nombre == s["nombre"])).first()
            
            if not sub:
                sub = Rubro(nombre=s["nombre"], codigo=s["codigo"], padre_id=ropa_rubro.id, activo=True)
                db.add(sub)
                db.commit()
                db.refresh(sub)
                print(f"  Created Subrubro: {sub.nombre}")
            else:
                # Ensure parent linkage if it exists but orphaned or elsewhere? 
                # For now just log
                print(f"  Found Subrubro: {sub.nombre}")
                if sub.padre_id != ropa_rubro.id:
                     sub.padre_id = ropa_rubro.id
                     db.commit()
                     print(f"    (Relinked to {ropa_rubro.nombre})")

            sub_map[s["nombre"]] = sub

        # 3. Create Products
        # Barbijos
        create_products(db, sub_map["BARBIJOS"], ["Barbijo Tricapa", "Barbijo N95", "Barbijo Social"])
        # Cofias
        create_products(db, sub_map["COFIAS"], ["Cofia Plisada", "Cofia Redonda"])
        # Cubrezapatos
        create_products(db, sub_map["CUBREZAPATOS"], ["Cubrezapato Antideslizante"])
        # Camisolines
        create_products(db, sub_map["CAMISOLINES"], ["Camisolín Hemorrepelente", "Camisolín SMS"])

        # Guantes (10 types x 5 sizes)
        guantes_types = [
            "Guante Polietileno Corto", "Guante Polietileno Largo", 
            "Guante Nitrilo Azul", "Guante Nitrilo Negro",
            "Guante Latex Exam", "Guante Latex Cirugía",
            "Guante Vinilo Clear", "Guante Vinilo Blue",
            "Guante Neoprene", "Guante TPE"
        ]
        sizes = ["XS", "S", "M", "L", "XL"]
        
        guantes_prod_names = []
        for t in guantes_types:
            for sz in sizes:
                guantes_prod_names.append(f"{t} Talle {sz}")
        
        create_products(db, sub_map["GUANTES"], guantes_prod_names)

    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

def create_products(db: Session, rubro: Rubro, names: list):
    for name in names:
        # Check by name
        exists = db.query(Producto).filter(Producto.nombre == name).first()
        if not exists:
            # Fake SKU logic automatic by DB, but we handle unique fields
            prod = Producto(
                nombre=name,
                descripcion=f"Producto de prueba {name}",
                rubro_id=rubro.id,
                tipo_producto="VENTA",
                unidad_medida="UN",
                activo=True
            )
            db.add(prod)
            try:
                db.commit()
                print(f"    Created Product: {name} in {rubro.nombre}")
            except Exception as e:
                 db.rollback()
                 print(f"    Error creating {name}: {e}")

if __name__ == "__main__":
    seed_ropa_descartable()
