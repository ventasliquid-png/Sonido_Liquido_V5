import requests
import json

def check_vendedores():
    try:
        response = requests.get("http://127.0.0.1:8000/maestros/vendedores?status=all")
        if response.status_code == 200:
            vendedores = response.json()
            print(f"Total Vendedores: {len(vendedores)}")
            for v in vendedores:
                print(f"ID: {v['id']}, Nombre: {v['nombre']}, Activo: {v['activo']} (Type: {type(v['activo'])})")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def check_personas():
    try:
        response = requests.get("http://127.0.0.1:8000/agenda/personas?status=active")
        if response.status_code == 200:
            personas = response.json()
            print(f"\nTotal Personas (Active): {len(personas)}")
            for p in personas:
                print(f"ID: {p['id']}, Nombre: {p['nombre_completo']}, Activo: {p['activo']} (Type: {type(p['activo'])})")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("--- Checking Vendedores ---")
    check_vendedores()
    print("\n--- Checking Personas ---")
    check_personas()
