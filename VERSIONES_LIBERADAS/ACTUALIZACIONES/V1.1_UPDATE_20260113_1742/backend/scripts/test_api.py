import requests
import sys

def test_api():
    print("--- Testing API Endpoints ---")
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test Logistica Empresas
    print("\n1. Testing /logistica/empresas?status=all")
    try:
        resp = requests.get(f"{base_url}/logistica/empresas", params={"status": "all"}, timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Count: {len(data)}")
            print(f"Sample: {data[0] if data else 'Empty'}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

    # 2. Test Clientes
    print("\n2. Testing /clientes/")
    try:
        resp = requests.get(f"{base_url}/clientes/", timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Count: {len(data)}")
            # Print first client summary
            if data:
                c = data[0]
                print(f"First Client: {c.get('razon_social')} (Activo: {c.get('activo')})")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_api()
