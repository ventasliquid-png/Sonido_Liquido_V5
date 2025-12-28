
import requests
import os
from dotenv import dotenv_values

# Config
config = dotenv_values(".env")
BASE_URL = "http://localhost:8000" # Asumimos puerto default

def check_endpoint(endpoint, name):
    try:
        url = f"{BASE_URL}/{endpoint}"
        print(f"📡 Consultando {name}: {url}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print(f"✅ {name}: OK ({count} registros)")
            if count == 0:
                print(f"⚠️  {name} está vacío en la API, aunque la DB tenga datos. Chequear filtros default (ej: ?activo=true).")
            else:
                print(f"   Ejemplo: {data[0].get('razon_social') or data[0].get('nombre')}")
        else:
            print(f"❌ {name}: Error {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ {name}: Fallo de conexión. ¿Está corriendo uvicorn? ({e})")

if __name__ == "__main__":
    print("--- DIAGNÓSTICO DE API ---")
    check_endpoint("clientes", "Clientes")
    check_endpoint("productos", "Productos")
    print("--------------------------")
