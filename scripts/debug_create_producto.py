import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.productos import models
from backend.proveedores import models as proveedores_models
from backend.maestros import models as maestros_models

def debug_create_producto():
    db = SessionLocal()
    try:
        print("Attempting to create Producto directly...")
        
        # Get a rubro
        rubro = db.query(models.Rubro).first()
        if not rubro:
            print("No rubro found, creating one...")
            rubro = models.Rubro(nombre="Rubro Debug Prod", codigo="DBP", activo=True)
            db.add(rubro)
            db.commit()
            db.refresh(rubro)
            print(f"Created Rubro: {rubro.id}")
        else:
            print(f"Using Rubro: {rubro.id}")

        import random
        rand_suffix = random.randint(1000, 9999)
        new_producto = models.Producto(
            nombre=f"Producto Debug Direct {rand_suffix}",
            rubro_id=rubro.id,
            unidad_medida="UN",
            tipo_producto="VENTA",
            factor_compra=1.0,
            codigo_visual=f"DBG-PROD-{rand_suffix}",
            descripcion="Debug Product"
        )
        db.add(new_producto)
        db.commit()
        db.refresh(new_producto)
        print(f"✅ Created Producto: {new_producto.id} - {new_producto.nombre}")
        
        # Create Costos
        costos = models.ProductoCosto(
            producto_id=new_producto.id,
            costo_reposicion=100.0,
            margen_mayorista=50.0,
            iva_alicuota=21.0,
            moneda_costo="ARS"
        )
        db.add(costos)
        db.commit()
        print("✅ Created Costos")

        # Simulate router logic
        db.refresh(new_producto)
        print("Refreshed product")
        
        if not new_producto.costos:
            print("⚠️ Costos not loaded automatically")
        else:
            print(f"✅ Costos loaded: {new_producto.costos.costo_reposicion}")

        # Calculate prices
        costo = new_producto.costos.costo_reposicion
        margen = new_producto.costos.margen_mayorista
        iva = new_producto.costos.iva_alicuota
        
        precio_neto = costo * (1 + margen / 100)
        precio_final = precio_neto * (1 + iva / 100)
        
        print(f"Calculated Price: {precio_final}")

    except Exception as e:
        print(f"❌ Error creating producto: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_create_producto()
