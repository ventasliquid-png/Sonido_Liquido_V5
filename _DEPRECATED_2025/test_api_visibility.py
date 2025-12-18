
import requests

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("1. Testing /productos (Simple)")
    try:
        r = requests.get(f"{base_url}/productos/?limit=5")
        if r.status_code == 200:
            count = len(r.json())
            print(f"[OK] PRODUCTOS: Found {count} items.")
        else:
            print(f"[FAIL] PRODUCTOS: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] PRODUCTOS: {e}")

    print("\n2. Testing /clientes (Complex)")
    try:
        r = requests.get(f"{base_url}/clientes/?limit=5")
        if r.status_code == 200:
            data = r.json()
            count = len(data)
            print(f"[OK] CLIENTES: Found {count} items.")
            if count > 0:
                print(f"Sample: {data[0].get('razon_social')}")
        else:
            print(f"[FAIL] CLIENTES: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERROR] CLIENTES: {e}")

if __name__ == "__main__":
    test_api()
