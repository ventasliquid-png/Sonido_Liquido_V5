from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.logistica import models
import uuid

client = TestClient(app)

def test_create_nodo():
    # 1. Get an existing empresa
    db = SessionLocal()
    empresa = db.query(models.EmpresaTransporte).first()
    db.close()
    
    if not empresa:
        print("No hay empresas para probar.")
        return

    print(f"Testing with Empresa ID: {empresa.id}")

    # 2. Payload similar to frontend
    payload = {
        "nombre_nodo": "Sede Test Script",
        "direccion_completa": "Av Test 123",
        "localidad": "CABA",
        "provincia_id": "C",
        "telefono": "123456",
        "email": "test@test.com",
        "es_punto_despacho": False,
        "es_punto_retiro": False,
        "empresa_id": str(empresa.id)
    }

    # 3. Simulate POST (Without Auth for now? No, endpoint needs auth)
    # The endpoint relies on get_current_user. If I use TestClient with override_dependency or just try and see 401.
    # To properly test, I should probably override the auth dependency or login.
    # Let's try to override get_current_user to return a mock user.
    
    from backend.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"username": "testuser", "id": 1}

    try:
        response = client.post("/logistica/nodos", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_create_nodo()
