
import requests
import json

# URL
URL = "http://localhost:8000/pedidos/tactico"

def reproduce_error():
    # 1. First, create a dummy client like "Juan Kiosco" (if API allows, or find existing)
    # We'll try to find the one the user created.
    # Actually, let's just list clients to find the ID of "Juan Kiosco"
    try:
        print("Testing /maestros/segmentos connectivity...")
        res = requests.get("http://localhost:8000/maestros/segmentos")
        print(f"Status: {res.status_code}, URL: {res.url}")

        print("Testing /clientes/ (with slash)...")
        res = requests.get("http://localhost:8000/clientes/")
        print(f"Status: {res.status_code}, URL: {res.url}, History: {res.history}")
        
        try:
             clients = res.json()
        except:
             print("Clients failed to parse JSON")
             clients = []


        # Handle if it's paginated (e.g. {'items': [...]})
        if isinstance(clients, dict) and 'items' in clients:
            clients = clients['items']
            
        print(f"Clients type: {type(clients)}")
        if isinstance(clients, dict):
            print(f"Keys: {clients.keys()}")
            if 'error' in clients:
                print(f"ERROR MSG: {clients['error']}")
                return
            
        if isinstance(clients, list) and len(clients) > 0:
             print(f"Sample client: {clients[0]}")
             
        target_client = next((c for c in clients if isinstance(c, dict) and "juan" in c.get('razon_social', '').lower()), None)

        
        if not target_client:
            print("Client 'Juan' not found. Cannot reproduce exactly.")
            # Use any client
            if clients:
                target_client = clients[0]
            else:
                print("No clients found.")
                return

        print(f"Target Client: {target_client['id']} - {target_client['razon_social']}")
        
        # 2. Find a product
        res = requests.get("http://localhost:8000/productos")
        products = res.json()
        if not products:
            print("No products found (empty).")
            return

        if isinstance(products, dict):
            print(f"DEBUG: Products response keys: {products.keys()}")
            if 'detail' in products:
                 print(f"DEBUG: Error Detail: {products['detail']}")
                 # Fallback to dummy
                 prod = {'id': 1, 'nombre': 'Dummy Product'}
            elif 'items' in products:
                products = products['items']
                prod = products[0]
            else:
                prod = {'id': 1, 'nombre': 'Dummy Product'}
        elif isinstance(products, list) and len(products) > 0:
            prod = products[0]
        else:
            print("No products found, using dummy.")
            prod = {'id': 1, 'nombre': 'Dummy Product'}

        print(f"Target Product: {prod['id']} - {prod['nombre']}")

        # 3. Construct Payload exactly as GridLoader.vue
        payload = {
            "cliente_id": target_client['id'],
            "fecha": "2025-12-15",
            "nota": "Test from debug script",
            "oc": "",
            "items": [
                {
                    "producto_id": prod['id'],
                    "cantidad": 1,
                    "precio_unitario": 0 
                }
            ]
        }
        
        print("Sending Payload:", json.dumps(payload, indent=2))
        
        print("Testing POST /pedidos/tactico (NO Slash)...")
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(URL, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print("Response:", response.text[:500])
        except Exception as e:
            print(f"POST Failed: {e}")

        print("Testing POST /pedidos/tactico/ (WITH Slash)...")
        try:
            response = requests.post(URL + "/", json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print("Response:", response.text[:500])
        except Exception as e:
            print(f"POST Slash Failed: {e}")
            
        print("Testing OPTIONS /pedidos/tactico...")
        try:
            response = requests.options(URL)
            print(f"Status Code: {response.status_code}")
            print("Headers:", response.headers)
        except Exception as e:
             print(f"OPTIONS Failed: {e}")

        return # End here
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Request failed: {repr(e)}")

if __name__ == "__main__":
    reproduce_error()
