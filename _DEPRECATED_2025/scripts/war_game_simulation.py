import sys
import os
from datetime import datetime
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
# Import ALL models to ensure SQLAlchemy registry is complete
from backend.auth.models import Usuario, Rol
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Provincia, TasaIVA, Unidad, TipoContacto
from backend.agenda.models import VinculoComercial, Persona
from backend.proveedores.models import Proveedor
from backend.clientes.models import Cliente, Domicilio
from backend.pedidos.models import Pedido, PedidoItem
from backend.productos.models import Producto, ProductoCosto, Rubro

def run_war_game():
    print("\n--- [WAR GAME] INICIO DE SIMULACIÓN DE PRECIOS ---\n")
    db = SessionLocal()
    
    try:
        # 1. SETUP: Cliente y Producto
        print("1. [SETUP] Asegurando Cliente y Producto de Prueba...")
        
        # Cliente
        cliente = db.query(Cliente).filter(Cliente.razon_social == "CLIENTE TEST SIMULACRO").first()
        if not cliente:
            print("   -> Creando Cliente Ficticio...")
            cliente = Cliente(
                razon_social="CLIENTE TEST SIMULACRO",
                cuit="20111111112",
                email="test@simulacro.com",
                telefono="1111-2222",
                condicion_iva_id=1, # Asumiendo 1 existe
                lista_precios_id=1, # Asumiendo 1 existe
                activo=True
            )
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
        else:
            print(f"   -> Cliente encontrado: {cliente.razon_social}")

        # Rubro (dummy safety)
        rubro = db.query(Rubro).first()
        if not rubro:
             rubro = Rubro(codigo="TST", nombre="TEST", activo=True)
             db.add(rubro)
             db.commit()

        # Producto
        producto = db.query(Producto).filter(Producto.nombre == "PRODUCTO TEST A").first()
        if not producto:
            print("   -> Creando Producto Ficticio...")
            producto = Producto(
                nombre="PRODUCTO TEST A",
                rubro_id=rubro.id,
                tipo_producto="VENTA",
                activo=True,
                sku=999999
            )
            db.add(producto)
            db.commit()
            db.refresh(producto)
            
            # Costo
            costo = ProductoCosto(
                producto_id=producto.id,
                costo_reposicion=50.0,
                margen_mayorista=50.0, # Precio Venta aprox 75 + IVA
                iva_alicuota=21.0
            )
            db.add(costo)
            db.commit()
        else:
            print(f"   -> Producto encontrado: {producto.nombre}")

        # 2. CREACION DE PEDIDO
        print("\n2. [ACCIÓN] Creando Pedido en estado 'BORRADOR'...")
        pedido = Pedido(
            cliente_id=cliente.id,
            estado="BORRADOR",
            tipo_comprobante="FISCAL", # Default
            fecha=datetime.now(),
            total=0.0
        )
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        print(f"   -> Pedido #{pedido.id} creado. Estado: {pedido.estado}. Tipo: {pedido.tipo_comprobante}")

        # 3. AGREGAR ITEM
        print("\n3. [ACCIÓN] Agregando Item (Precio: $100.00, Cant: 1)...")
        # Forzamos un precio manual para el test claro
        item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=1.0,
            precio_unitario=100.0,
            subtotal=100.0,
            nota="Item de Prueba War Game"
        )
        db.add(item)
        
        # Actualizar total pedido
        pedido.total = 100.0
        db.commit()
        db.refresh(pedido)
        print(f"   -> Item agregado. Total Pedido DB: ${pedido.total:.2f}")

        # 4. IMPACTO 1: PENDIENTE + FISCAL
        print("\n4. [IMPACTO 1] Cambio a PENDIENTE (FISCAL)...")
        pedido.estado = "PENDIENTE"
        pedido.tipo_comprobante = "FISCAL"
        db.commit()
        db.refresh(pedido)
        print(f"   -> DB State: Estado={pedido.estado}, Tipo={pedido.tipo_comprobante}, Total=${pedido.total:.2f}")
        
        # 5. IMPACTO 2: CAMBIO A TIPO 'X'
        print("\n5. [IMPACTO 2] Cambio a TIPO 'X' (Manteniendo PENDIENTE)...")
        # Aquí es donde simulamos lo que hace el usuario en el frontend
        pedido.tipo_comprobante = "X"
        # ¿El backend hace algo mágico aquí? Si uso el ORM directo, NO. 
        # Si la lógica está en el frontend, aquí no pasará nada con el precio.
        # ESTA ES LA PRUEBA: Si el precio es 100, y pasamos a X, ¿Debería bajar el IVA?
        # Si el usuario solo cambia el flag, veamos que queda en DB.
        db.commit()
        db.refresh(pedido)
        print(f"   -> DB State: Estado={pedido.estado}, Tipo={pedido.tipo_comprobante}, Total=${pedido.total:.2f}")

        # 6. IMPACTO 3: VOLVER A FISCAL
        print("\n6. [IMPACTO 3] Volver a TIPO 'FISCAL'...")
        pedido.tipo_comprobante = "FISCAL"
        db.commit()
        db.refresh(pedido)
        print(f"   -> DB State: Estado={pedido.estado}, Tipo={pedido.tipo_comprobante}, Total=${pedido.total:.2f}")

        print("\n--- [SPOILER] ---")
        print("Si el total se mantuvo en $100.00 todo el tiempo, significa que el cambio de tipo es PURAMENTE DECLARATIVO en el backend actual.")
        print("No hay triggers ni lógica en el modelo que recalcule precios automágicamente.")
        
    except Exception as e:
        print(f"\n❌ CRASH: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_war_game()
