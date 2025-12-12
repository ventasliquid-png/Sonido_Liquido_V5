import sys
import os
import pandas as pd
from sqlalchemy import text
from decimal import Decimal

# Add root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine, Base
# Import ALL models to ensure metadata is complete
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro, ProductoCosto
from backend.pedidos.models import Pedido, PedidoItem
from backend.maestros.models import CondicionIva, Provincia, Segmento, ListaPrecios
from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.auth.models import Usuario, Rol
from backend.agenda.models import VinculoComercial, Persona
from backend.proveedores.models import Proveedor


DATA_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"

def seed_data():
    print("--- Seeding Pilot Data & Fixing Schema ---")

    # 1. Schema Fix (Drop Pedidos to enforce UUID)
    try:
        with engine.connect() as conn:
            print("Dropping 'pedidos_items' and 'pedidos'...")
            conn.execute(text("DROP TABLE IF EXISTS pedidos_items CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS pedidos CASCADE"))
            conn.commit()
    except Exception as e:
        print(f"Warning dropping tables: {e}")

    # 2. Re-create all tables
    print("Creating/Updating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 3. Rubro Default
        rubro = db.query(Rubro).filter(Rubro.codigo == "GEN").first()
        if not rubro:
            rubro = Rubro(nombre="GENERAL", codigo="GEN")
            db.add(rubro)
            db.commit()
            db.refresh(rubro)
            print("Created default Rubro: GENERAL")
        
        # 4. Productos
        prod_path = os.path.join(DATA_DIR, "productos_raw.csv")
        if os.path.exists(prod_path):
            df_prod = pd.read_csv(prod_path).fillna("")
            count_p = 0
            for _, row in df_prod.iterrows():
                nombre = row.get("nombre", "").strip()
                if not nombre: continue
                
                # Check exist
                if db.query(Producto).filter(Producto.nombre == nombre).first():
                    continue

                precio = row.get("precio", 0)
                try:
                    precio = float(precio) if precio else 0
                except:
                    precio = 0

                prod = Producto(
                    nombre=nombre,
                    rubro_id=rubro.id,
                    activo=True
                )
                db.add(prod)
                db.flush() # get ID

                # Create Costo
                costo = ProductoCosto(
                    producto_id=prod.id,
                    costo_reposicion=Decimal(precio),
                    margen_mayorista=Decimal(30), # Default
                    iva_alicuota=Decimal(21)
                )
                db.add(costo)
                count_p += 1
            
            db.commit()
            print(f"Imported {count_p} Productos.")
        else:
            print(f"Not found: {prod_path}")

        # 5. Clientes
        clie_path = os.path.join(DATA_DIR, "clientes_raw.csv")
        if os.path.exists(clie_path):
            df_clie = pd.read_csv(clie_path).fillna("")
            count_c = 0
            for _, row in df_clie.iterrows():
                nombre = row.get("nombre", "").strip()
                if not nombre: continue
                
                cuit = str(row.get("cuit", "")).strip().replace("-", "").replace("/", "")
                if not cuit: cuit = "00000000000" # Dummy for pilot

                # Check exist
                if db.query(Cliente).filter(Cliente.razon_social == nombre).first():
                    continue

                cli = Cliente(
                    razon_social=nombre,
                    cuit=cuit,
                    activo=True,
                    condicion_iva_id=None # Nullable
                )
                db.add(cli)
                count_c += 1
            
            db.commit()
            print(f"Imported {count_c} Clientes.")
        else:
            print(f"Not found: {clie_path}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
