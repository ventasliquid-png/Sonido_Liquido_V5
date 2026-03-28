from fastapi.testclient import TestClient
import os
from datetime import datetime

# Force SQLite for the test
from backend.main import app 

client = TestClient(app)

def test_create_pedido_tactico():
    print("\n--- Testing /pedidos/tactico ---")
    
    # Using IDs found in previous steps
    cliente_id = "023d1327-c172-4a59-818a-5536b82863fb"
    producto_id = 1 # Assuming 1 exists or will try to find one
    
    payload = {
        "cliente_id": cliente_id,
        "fecha": datetime.now().isoformat(),
        "items": [
            {
                "producto_id": 16, # Let's use a common one or find one
                "cantidad": 10.5,
                "precio_unitario": 100.0
            }
        ],
        "estado": "PENDIENTE",
        "tipo_facturacion": "B"
    }
    
    try:
        response = client.post("/pedidos/tactico", json=payload)
        print("STATUS:", response.status_code)
        if response.status_code == 201:
            print("SUCCESS: Pedido created successfully!")
            print("DATA:", response.json())
        else:
            print("FAILED:", response.text)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_pedido_tactico()
