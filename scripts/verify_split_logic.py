# scripts/verify_split_logic.py
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.getcwd())

# Set ENV to force SQLite
os.environ["DATABASE_URL"] = "sqlite:///c:/dev/Sonido_Liquido_V5/backend/pilot.db"
os.environ["ENABLE_AI"] = "False" # Disable AI to speed up boot

from backend.main import app
from backend.core.database import get_db, Base
from backend.productos.models import Producto

client = TestClient(app)

def verify_flow():
    print("--- 🧪 INICIANDO VERIFICACIÓN DE PROTOCOLO V7 (SPLIT) ---")
    
    # 1. Identificar un producto y cliente para el test
    # Usaremos el primer producto y cliente disponibles
    try:
        response = client.get("/productos/?limit=1")
        if response.status_code != 200:
            print("❌ Error obteniendo productos")
            return
        productos = response.json()
        if not productos:
            print("❌ No hay productos para testear")
            return
        producto_id = productos[0]["id"]
        
        response = client.get("/clientes/?limit=1")
        cliente_id = response.json()[0]["id"]
        
        # Get Current Stock
        response = client.get(f"/productos/{producto_id}")
        prod_data = response.json()
        initial_fisico = prod_data.get("stock_fisico") or 0.0
        initial_reservado = prod_data.get("stock_reservado") or 0.0
        
        print(f"📦 Producto ID: {producto_id}")
        print(f"📊 Stock Inicial: Físico={initial_fisico}, Reservado={initial_reservado}")
        
        # 2. Crear Pedido (Reserve Logic)
        print("\n👉 Creando Pedido (10 Unidades)...")
        pedido_payload = {
            "cliente_id": cliente_id,
            "fecha": "2026-02-04T12:00:00",
            "items": [
                {
                    "producto_id": producto_id,
                    "cantidad": 10.0,
                    "precio_unitario": 100.0
                }
            ],
            "domicilio_entrega_id": "00000000-0000-0000-0000-000000000000", # Fake GUID or fetch real one
            "transporte_id": "00000000-0000-0000-0000-000000000000"
        }
        
        # We need a valid domicilio/transporte ID ideally, but if schema is loose we can try fake.
        # But FK constraints might fail in SQLite.
        # Let's fetch valid Logistica IDs.
        try:
             # Just cheat and use None if nullable? No, schema says nullable=True in models but payload might require it
             # Pedido model: nullable=True.
             pedido_payload["domicilio_entrega_id"] = None
             pedido_payload["transporte_id"] = None
        except:
            pass

        r = client.post("/pedidos/tactico", json=pedido_payload)
        if r.status_code != 201:
            print(f"❌ Error creando pedido: {r.text}")
            return
        
        pedido_id = r.json()["id"]
        pedido_item_id = r.json()["items"][0]["id"]
        print(f"✅ Pedido #{pedido_id} creado.")
        
        # 3. Check Reservation
        response = client.get(f"/productos/{producto_id}")
        prod_data = response.json()
        new_reservado = prod_data.get("stock_reservado") or 0.0
        
        print(f"📊 Stock Post-Pedido: Reservado={new_reservado} (Esperado: {initial_reservado + 10})")
        if new_reservado == initial_reservado + 10:
            print("✅ RESERVA OK")
        else:
            print("❌ FALLO RESERVA")
            
        # 4. Crear Remito (Split 4 Unidades)
        print("\n👉 Creando Remito (4 Unidades) [Aprobado=True]...")
        # Need transport/address for Remito. 
        # We need to fetch real ones or insert them.
        # Let's try to fetch from cliente/logistica endpoints.
        
        # Assuming we can insert a fake transport/address via direct DB or just find one
        # For simplicity, let's create a remito with "dummy" IDs if constraints allow, 
        # but they are FKs.
        # Check if we have transportes
        r = client.get("/logistica/transportes")
        transportes = r.json()
        if not transportes:
             print("⚠️ No hay transportes. Saltando test Remito (Falta data maestra).")
             # Clean up
             client.delete(f"/pedidos/{pedido_id}")
             return
             
        transporte_id = transportes[0]["id"]
        domicilio_entrega_id = "00000000-0000-0000-0000-000000000000" # We need a domicile.
        
        # Try fetch domiciles of client
        r = client.get(f"/clientes/{cliente_id}")
        cliente_data = r.json()
        if cliente_data.get("domicilios"):
             domicilio_entrega_id = cliente_data["domicilios"][0]["id"]
        else:
             print("⚠️ Cliente sin domicilios. Saltando test Remito.")
             client.delete(f"/pedidos/{pedido_id}")
             return

        remito_payload = {
            "pedido_id": pedido_id,
            "domicilio_entrega_id": domicilio_entrega_id,
            "transporte_id": transporte_id,
            "aprobado_para_despacho": True,
            "items": [
                {
                    "pedido_item_id": pedido_item_id,
                    "cantidad": 4.0
                }
            ]
        }
        
        r = client.post("/remitos/", json=remito_payload)
        if r.status_code != 201:
            print(f"❌ Error creando remito: {r.text}")
            client.delete(f"/pedidos/{pedido_id}")
            return
            
        remito_id = r.json()["id"]
        print(f"✅ Remito creodo: {remito_id}")
        
        # 5. Despachar Remito
        print("\n👉 Despachando Remito...")
        r = client.post(f"/remitos/{remito_id}/despachar")
        if r.status_code != 200:
             print(f"❌ Error despachando: {r.text}")
             return
             
        print("✅ Despacho confirmado.")
        
        # 6. Check Final Stock
        response = client.get(f"/productos/{producto_id}")
        prod_data = response.json()
        final_fisico = prod_data.get("stock_fisico") or 0.0
        final_reservado = prod_data.get("stock_reservado") or 0.0
        
        print(f"📊 Stock Final: Físico={final_fisico}, Reservado={final_reservado}")
        print(f"   Esperado: Físico={initial_fisico - 4}, Reservado={initial_reservado + 10 - 4}")
        
        if final_fisico == initial_fisico - 4 and final_reservado == initial_reservado + 6:
            print("✅ MOVIMIENTO DE STOCK EXITOSO")
        else:
             print("❌ FALLO MOVIMIENTO STOCK")
             
        # Cleanup
        print("\n🧹 Limpiando...")
        client.delete(f"/pedidos/{pedido_id}") # Should fallback reservation
        # We need to manually fix stock from the remito? 
        # Delete pedido releases remaining 6 reservation.
        # But the 4 dispatched are gone physically.
             
    except Exception as e:
        print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    verify_flow()
