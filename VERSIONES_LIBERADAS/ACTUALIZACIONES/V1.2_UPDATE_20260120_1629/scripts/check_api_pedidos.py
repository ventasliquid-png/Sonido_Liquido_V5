import requests
import sys
import os

# Ajustar BASE_URL según puerto local (8000 por defecto)
BASE_URL = "http://localhost:8000"

def check_pedidos():
    print(f"--- Diagnóstico de API Pedidos ({BASE_URL}) ---")
    
    # 1. Probar Endpoint de Listado
    try:
        url = f"{BASE_URL}/pedidos/?limit=100"
        print(f"GET {url}...")
        resp = requests.get(url)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Status 200 OK")
            print(f"📦 Cantidad de Pedidos recibidos: {len(data)}")
            if len(data) > 0:
                print("📝 Muestra del primer pedido:")
                print(data[0])
            else:
                print("⚠️  La lista está VACÍA, aunque la DB dice tener registros.")
        else:
            print(f"❌ Error HTTP {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"❌ Excepción conectando a API: {e}")

if __name__ == "__main__":
    check_pedidos()
