import requests
import json

BASE_URL = "http://localhost:8000"
CLIENT_ID = "6224c227-22c3-41d4-9b48-e8a3fb8539db"
DOMICILIO_ID = "c517e3a8-61aa-4b20-877a-292a7f62c7d8"

def test_update_domicilio():
    url = f"{BASE_URL}/clientes/{CLIENT_ID}/domicilios/{DOMICILIO_ID}"
    
    # Payload simulating a toggle or edit
    payload = {
        "id": "c517e3a8-61aa-4b20-877a-292a7f62c7d8",
        "cliente_id": "6224c227-22c3-41d4-9b48-e8a3fb8539db",
        "alias": None,
        "calle": "Cramer",
        "numero": "4601",
        "localidad": "CABA",
        "provincia_id": None,
        "activo": True,
        "es_fiscal": False,
        "es_entrega": True,
        "transporte_id": "5e47275c-1ad8-4f53-afed-5dd4a6e2bc90",
        "intermediario_id": None,
        "metodo_entrega": "TRANSPORTE",
        "modalidad_envio": "A_DOMICILIO",
        "origen_logistico": "DESPACHO_NUESTRO",
        # Potential extra fields causing trouble?
        "transporte_habitual_nodo_id": None, 
    }
    
    print(f"🔄 Testing PUT {url}...")
    headers = {
        "Origin": "http://localhost:5173",
        "Referer": "http://localhost:5173/"
    }
    
    # Test OPTIONS first (Browser Preflight)
    print("Testing OPTIONS...")
    try:
        opt_response = requests.options(url, headers=headers)
        print(f"OPTIONS Status: {opt_response.status_code}")
        print("OPTIONS Headers:", opt_response.headers)
    except Exception as e:
        print(f"OPTIONS Failed: {e}")

    # Test PUT
    try:
        response = requests.put(url, json=payload, headers=headers)
        print(f"PUT Status Code: {response.status_code}")
        print("PUT Headers:", response.headers)
        if "Access-Control-Allow-Origin" not in response.headers:
             print("❌ CRITICAL: Access-Control-Allow-Origin header MISSING!")
        else:
             print(f"✅ CORS Header: {response.headers['Access-Control-Allow-Origin']}")
             
        try:
            print("Response Body Sample:", str(response.json())[:100])
        except:
            print("Raw Text:", response.text)
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    test_update_domicilio()
