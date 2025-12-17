import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

# Try to initialize the full app context to avoid circular import issues
try:
    from backend.main import app
except Exception as e:
    print(f"Warning: Could not import main app: {e}")

from backend.core.database import SessionLocal
# We still import models to be able to use them, but hopefully main has registered them
from backend.clientes.models import Cliente
from backend.pedidos.models import Pedido, PedidoItem
from backend.productos.models import Producto, ProductoCosto, Rubro

def run_war_game():
    print("\n--- [WAR GAME V2] SIMULACIÓN DE PRECIOS ---\n")
    db = SessionLocal()
    
    try:
        # 1. SETUP: Cliente y Producto
        print("1. [SETUP] Buscando Cliente y Producto...")
        
        # Cliente Existing or Create
        cliente = db.query(Cliente).filter(Cliente.razon_social == "CLIENTE TEST SIMULACRO").first()
        if not cliente:
             print("   -> Cliente simulacro no existe. Creando...")
             # Create simple client
             cliente = Cliente(
                 razon_social="CLIENTE TEST SIMULACRO",
                 cuit="20999999992",
                 activo=True
             )
             db.add(cliente)
             db.commit()
             db.refresh(cliente)
        
        # Producto
        producto = db.query(Producto).first()
        if not producto:
            print("❌ No hay productos en la DB para probar. Saliendo.")
            return

        print(f"   -> Usando Cliente: {cliente.razon_social}")
        print(f"   -> Usando Producto: {producto.nombre}")

        # 2. CREAR PEDIDO BORRADOR
        print(f"\n2. [BORRADOR] Creando pedido...")
        pedido = Pedido(
            cliente_id=cliente.id,
            fecha=datetime.now(),
            estado="BORRADOR",
            tipo_comprobante="FISCAL",
            total=0.0
        )
        db.add(pedido)
        db.flush()
        
        # Item
        item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=1,
            precio_unitario=100.0, # PRECIO FIJO PARA TEST
            subtotal=100.0
        )
        db.add(item)
        pedido.total = 100.0
        db.commit()
        db.refresh(pedido)
        
        print(f"   -> Pedido #{pedido.id} creado | Estado={pedido.estado} | Tipo={pedido.tipo_comprobante} | Total=${pedido.total}")

        # 3. CAMBIO A PENDIENTE (FISCAL)
        print(f"\n3. [PENDIENTE] Cambiando a estado PENDIENTE...")
        pedido.estado = "PENDIENTE"
        # Simulate router update behavior (blind update)
        db.commit()
        db.refresh(pedido)
        print(f"   -> Resultado: Total=${pedido.total} (¿Cambió? {'SI' if pedido.total != 100 else 'NO'})")

        # 4. CAMBIO A TIPO X
        print(f"\n4. [TIPO X] Cambiando a TIPO X...")
        pedido.tipo_comprobante = "X"
        # Simulate router update behavior
        db.commit()
        db.refresh(pedido)
        print(f"   -> Resultado: Total=${pedido.total} (¿Cambió? {'SI' if pedido.total != 100 else 'NO'})")

        # 5. RETORNO A FISCAL
        print(f"\n5. [TIPO FISCAL] Volviendo a FISCAL...")
        pedido.tipo_comprobante = "FISCAL"
        # Simulate router update behavior
        db.commit()
        db.refresh(pedido)
        print(f"   -> Resultado: Total=${pedido.total} (¿Cambió? {'SI' if pedido.total != 100 else 'NO'})")
        
        print(f"\n--- CONCLUSION ---")
        if pedido.total == 100.0:
            print("✅ CONFIRMADO: El sistema NO recalcula precios automáticamente al cambiar el tipo de comprobante.")
        else:
            print("⚠️ SORPRESA: El sistema recalculó precios.")

    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_war_game()
