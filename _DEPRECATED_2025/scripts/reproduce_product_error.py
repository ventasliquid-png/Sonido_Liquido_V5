import requests
import json

BASE_URL = "http://localhost:8000"

def create_product():
    # 1. Get a valid Rubro ID
    try:
        response = requests.get(f"{BASE_URL}/productos/rubros")
        if response.status_code != 200:
            print(f"Error getting rubros: {response.status_code} {response.text}")
            return
        
        rubros = response.json()
        if not rubros:
            print("No rubros found. Cannot create product without rubro.")
            # Create a rubro if none exists
            rubro_payload = {"nombre": "Rubro Test", "codigo": "TST", "activo": True}
            resp = requests.post(f"{BASE_URL}/productos/rubros", json=rubro_payload)
            if resp.status_code == 200:
                rubro_id = resp.json()["id"]
                print(f"Created temporary rubro with ID: {rubro_id}")
            else:
                print(f"Failed to create rubro: {resp.text}")
                return
        else:
            rubro_id = rubros[0]["id"]
            print(f"Using Rubro ID: {rubro_id}")

        # 2. Create Product
        payload = {
            "nombre": "Producto Test Auto",
            "rubro_id": rubro_id,
            "unidad_medida": "UN",
            "costos": {
                "costo_reposicion": 100.0,
                "margen_mayorista": 50.0,
                "iva_alicuota": 21.0,
                "moneda_costo": "ARS"
            },
            "tipo_producto": "VENTA",
            "factor_compra": 1.0,
            # Optional fields
            "codigo_visual": "TEST-001",
            "descripcion": "Producto de prueba generado por script"
        }

        print("Sending payload:", json.dumps(payload, indent=2))
        response = requests.post(f"{BASE_URL}/productos/", json=payload)
        
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    create_product()
