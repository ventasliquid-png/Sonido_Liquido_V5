from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.auth.models import Usuario
from backend.logistica.models import NodoTransporte, EmpresaTransporte
from backend.agenda.models import VinculoComercial
from backend.maestros.models import Provincia, CondicionIva, Segmento, ListaPrecios
from backend.productos.models import Producto
from backend.clientes.models import Cliente
from backend.clientes.service import ClienteService
from backend.pedidos.models import Pedido
import sys

def simulate_gelato_issue():
    db = SessionLocal()
    try:
        print("--- Buscando Clientes 'Gelato' ---")
        # Search case-insensitive
        clientes = db.query(Cliente).filter(Cliente.razon_social.ilike("%gelato%")).all()
        
        print(f"Encontrados: {len(clientes)}")
        for c in clientes:
            pedidos_count = db.query(Pedido).filter(Pedido.cliente_id == c.id).count()
            print(f"ID: {c.id} | Razon: {c.razon_social} | CUIT: {c.cuit} | Activo: {c.activo} | Pedidos: {pedidos_count}")
        
        # Identify the active ones
        activos = [c for c in clientes if c.activo]
        print(f"\nClientes Activos: {len(activos)}")
        
        if not activos:
            print("No hay clientes 'Gelato' activos para probar la baja.")
            return

        # Try to soft delete the first active one? 
        # Or better, just list them and ask user?
        # Creating a specific test case:
        # Create a dummy client with order and try to delete it.
        
        print("\n--- Simulacion de Baja en Cliente Dummy con Pedido ---")
        # 1. Create Dummy
        from backend.clientes.schemas import ClienteCreate
        import uuid
        dummy_cuit = f"20-{uuid.uuid4().int % 100000000:08}-1"
        dummy_data = ClienteCreate(
            razon_social="Gelato Dummy Test",
            cuit=dummy_cuit,
            condicion_iva_id=None, 
            activo=True,
            domicilios=[]
        )
        # Hack to bypass validacion in router, calling service directly might fail if dependencies missing?
        # Service needs ID for condicion iva? 
        # Let's just use raw model for speed
        dummy = Cliente(
            razon_social="Gelato Dummy Test", 
            cuit=dummy_cuit, 
            activo=True,
            estrategia_precio="MAYORISTA_FISCAL"
        )
        db.add(dummy)
        db.commit()
        db.refresh(dummy)
        print(f"Dummy Creado: {dummy.id}")
        
        # 2. Add Dummy Order
        pedido = Pedido(cliente_id=dummy.id, total=100.0, estado="PENDIENTE")
        db.add(pedido)
        db.commit()
        print("Pedido Dummy Creado.")
        
        # 3. Request Soft Delete via Service
        print("Intentando Soft Delete vía Service...")
        updated = ClienteService.delete_cliente(db, dummy.id)
        
        if updated and not updated.activo:
            print(f"✅ ÉXITO: Cliente {updated.razon_social} desactivado correctamente teniendo pedidos.")
        else:
            print("❌ FALLO: Cliente no se desactivó.")

        # Cleanup
        db.delete(pedido)
        db.delete(dummy)
        db.commit()
        
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_gelato_issue()
