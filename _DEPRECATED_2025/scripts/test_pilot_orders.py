import requests
import json
import uuid

BASE_URL = "http://localhost:8001"

def create_client_if_not_exists(razon_social, cuit):
    print(f"\n--- Checking/Creating Client: {razon_social} ({cuit}) ---")
    # 1. Check if exists using the check-cuit logic (optional, but good test)
    # But check-cuit returns NEW for these special cuits, so we can't find them by check-cuit easily if we rely on that.
    # Instead, we search by CUIT in the list or just try to create (we turned off uniqueness check so create might duplicate if we aren't careful, 
    # but for this test we mainly want to see if it allows creation).
    
    # Actually, we should check if they exist to avoid spamming duplicates or just accept we create a new one.
    # Let's search by name
    # The API doesn't have a search by name endpoint easily exposed other than list with filter?
    # Let's just create a new one for the test, ensuring the API accepts it.
    
    payload = {
        "razon_social": razon_social,
        "cuit": cuit,
        "condicion_iva_id": None, # Optional/Default
        "lista_precios_id": None,
        "activo": True,
        "domicilios": [
            {
                "calle": "Calle Falsa",
                "numero": "123",
                "localidad": "Testville",
                "activo": True,
                "es_entrega": True
            }
        ]
    }
    
    # We need to fetch Condicion IVA ID first probably? 
    # The schema says Optional but create_cliente might need it valid if provided.
    # Let's fetch one from backend/maestros/condicion-iva if possible or send None.
    # We'll send None.
    
    response = requests.post(f"{BASE_URL}/clientes/", json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success! Created Client ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Failed to create client. Status: {response.status_code}")
        print(response.text)
        return None

def create_pedido(cliente_id, items):
    print(f"\n--- Creating Pedido for Client {cliente_id} ---")
    payload = {
        "cliente_id": cliente_id,
        "items": items,
        "nota": "Pedido de Prueba [TEST SCRIPT]"
    }
    
    response = requests.post(f"{BASE_URL}/pedidos/tactico", json=payload)
    if response.status_code == 201:
        # It successfully created and returned an Excel file
        print("✅ Success! Pedido Created. Backend returned Excel content.")
        # We don't need to save the excel for this test, just knowing it 201'd is enough.
        return True
    else:
        print(f"❌ Failed to create pedido. Status: {response.status_code}")
        print(response.text)
        return False

def run_tests():
    # Scenario 1: "Paola" - The Shadow Circuit
    # CUIT: 00000000000
    paola_id = create_client_if_not_exists("Paola [TEST] Sombra", "00000000000")
    
    # Scenario 2: "Juan" - The Tracked Anonymous
    # CUIT: 99999999999
    juan_id = create_client_if_not_exists("Juan [TEST] Kiosco", "99999999999")
    
    if not paola_id or not juan_id:
        print("⚠️ Skipping Order creation due to client failure.")
        return

    # Create Orders
    # Use a dummy product ID. We need to fetch one product.
    print("\n--- Fetching a Product ---")
    prod_resp = requests.get(f"{BASE_URL}/productos/?limit=1")
    if prod_resp.status_code == 200 and len(prod_resp.json()) > 0:
        prod_id = prod_resp.json()[0]['id']
        print(f"Using Product ID: {prod_id}")
        
        items = [
            {
                "producto_id": prod_id,
                "cantidad": 10,
                "precio_unitario": 100.0,
                "nota": "Item Test"
            }
        ]
        
        create_pedido(paola_id, items)
        create_pedido(juan_id, items)
        
    else:
        print("❌ Could not fetch any product to test orders.")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"An error occurred: {e}")
