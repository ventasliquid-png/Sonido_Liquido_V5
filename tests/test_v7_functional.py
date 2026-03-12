# import pytest (removed)
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio

client = TestClient(app)

def test_create_domicilio_v7_fields():
    # 1. Create a dummy client
    db = SessionLocal()
    # Create client manually
    c = Cliente(razon_social="Test V7 Logistics", cuit="20123456789")
    db.add(c)
    db.commit()
    db.refresh(c)
    client_id = str(c.id)
    db.close()

    # 2. Payload with V7 fields
    payload = {
        "calle": "Av. Test",
        "numero": "123",
        "piso": "4",
        "depto": "B",
        "localidad": "CABA",
        "es_fiscal": True,
        "es_entrega": True,
        "notas_logistica": "Tocar timbre fuerte",
        "maps_link": "https://maps.google.com/?q=..."
    }

    # 3. Post to API
    response = client.post(f"/clientes/{client_id}/domicilios", json=payload)
    
    assert response.status_code == 201, response.text
    data = response.json()
    
    # 4. Verify fields in response
    assert data["piso"] == "4"
    assert data["depto"] == "B"
    assert data["notas_logistica"] == "Tocar timbre fuerte"
    
    # 5. Verify persistence in DB
    db = SessionLocal()
    dom = db.query(Domicilio).filter(Domicilio.id == data["id"]).first()
    assert dom.piso == "4"
    assert dom.depto == "B"
    assert dom.notas_logistica == "Tocar timbre fuerte"
    
    # Cleanup
    db.delete(dom)
    db.delete(db.query(Cliente).filter(Cliente.id == client_id).first())
    db.commit()
    db.close()
    
    print("✅ V7 Fields Persistence Verified")

if __name__ == "__main__":
    # Allow running directly
    try:
        test_create_domicilio_v7_fields()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        exit(1)
