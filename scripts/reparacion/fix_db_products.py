import sys
import os
sys.path.append('C:\\dev\\Sonido_Liquido_V5')

from backend.core.database import SessionLocal
from backend.productos.models import Producto, Rubro

def main():
    db = SessionLocal()
    
    # 1. Ensure Rubro exists
    rubro = db.query(Rubro).first()
    if not rubro:
        rubro = Rubro(codigo="GEN", nombre="Genérico")
        db.add(rubro)
        db.flush()
        print("Rubro Genérico Creado")
        
    # 2. Ensure Producto VARIOS exists
    prod = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
    if not prod:
        prod = Producto(nombre="ÍTEM VARIOS (Auto)", sku=999999, codigo_visual="VAR-001", rubro_id=rubro.id)
        db.add(prod)
        db.flush()
        print("Producto VARIOS Creado")
        
    db.commit()
    print("Database Fix: OK")

if __name__ == "__main__":
    main()
