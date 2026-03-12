import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app

def test_bridge():
    print("Probando Puente RAR-V5 (AFIP)...")
    client = TestClient(app)
    
    # CUIT de prueba (debe ser válido o el propio para testear)
    # Usamos el CUIT propio definido en Conexion_Blindada como default si no hay otro
    cuit_prueba = "20132967572" 
    
    try:
        response = client.get(f"/clientes/afip/{cuit_prueba}")
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(response.json())
        
        if response.status_code == 200:
            print("PUENTE OPERATIVO. Conexión con ARCA exitosa.")
        else:
            print("FALLO EN PUENTE.")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_bridge()
