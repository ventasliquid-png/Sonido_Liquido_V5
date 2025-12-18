
import requests
import json

URL = "http://localhost:8000/pedidos/tactico"

def test_post():
    # 1. Get Client
    try:
        res = requests.get("http://localhost:8000/clientes/")
        clients = res.json()
        if isinstance(clients, dict) and 'items' in clients: clients = clients['items']
        client = clients[0] if clients else None
    except:
        client = {'id': 'aef00048-1159-4294-a9ad-d995ac9c115f'} # Fallback

    if not client:
        print("No client found")
        return

    # 2. Get Product
    try:
        res = requests.get("http://localhost:8000/productos/") # With Slash
        products = res.json()
        # Handle list/dict
        if isinstance(products, dict):
             if 'items' in products: products = products['items']
             else: products = list(products.values()) if products else []
        
        product = products[0] if products and len(products) > 0 else None
    except Exception as e:
        print(f"Product fetch failed: {e}")
        product = None

    if not product:
        print("No product found. Cannot test 500 vs 201.")
        return

    print(f"Using Client: {client.get('razon_social', 'Unknown')} ({client.get('id')})")
    print(f"Using Product: {product.get('nombre', 'Unknown')} ({product.get('id')})")

    payload = {
        "cliente_id": client.get('id'),
        "fecha": "2025-12-15",
        "nota": "Real Test with OC",
        "oc": "OC-12345",
        "estado": "PRESUPUESTO",
        "items": [
            {
                "producto_id": product.get('id'),
                "cantidad": 1,
                "precio_unitario": 100
            }
        ]
    }

    try:
        res = requests.post(URL, json=payload)
        print(f"POST Status: {res.status_code}")
        try:
             print("Response JSON:", json.dumps(res.json(), indent=2))
        except:
             print("Response Text:", res.text[:500])
    except Exception as e:
        print(f"POST Failed: {e}")

if __name__ == "__main__":
    test_post()
