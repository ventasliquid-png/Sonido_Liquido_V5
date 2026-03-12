import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_provincias():
    print("\n--- Testing Provincias ---")
    # Create
    prov_id = "Z"
    data = {"id": prov_id, "nombre": "Provincia Test"}
    try:
        requests.delete(f"{BASE_URL}/maestros/provincias/{prov_id}") # Cleanup first
    except:
        pass

    res = requests.post(f"{BASE_URL}/maestros/provincias", json=data)
    print(f"Create: {res.status_code}")
    assert res.status_code == 201

    # Read
    res = requests.get(f"{BASE_URL}/maestros/provincias")
    print(f"Read All: {res.status_code}")
    assert any(p['id'] == prov_id for p in res.json())

    # Update
    update_data = {"nombre": "Provincia Test Updated"}
    res = requests.put(f"{BASE_URL}/maestros/provincias/{prov_id}", json=update_data)
    print(f"Update: {res.status_code}")
    assert res.json()['nombre'] == "Provincia Test Updated"

    # Delete
    res = requests.delete(f"{BASE_URL}/maestros/provincias/{prov_id}")
    print(f"Delete: {res.status_code}")
    assert res.status_code == 204

def test_condiciones_iva():
    print("\n--- Testing Condiciones IVA ---")
    # Create
    data = {"nombre": "IVA Test"}
    res = requests.post(f"{BASE_URL}/maestros/condiciones-iva", json=data)
    print(f"Create: {res.status_code}")
    assert res.status_code == 201
    created_id = res.json()['id']

    # Read
    res = requests.get(f"{BASE_URL}/maestros/condiciones-iva")
    print(f"Read All: {res.status_code}")
    assert any(c['id'] == created_id for c in res.json())

    # Update
    update_data = {"nombre": "IVA Test Updated"}
    res = requests.put(f"{BASE_URL}/maestros/condiciones-iva/{created_id}", json=update_data)
    print(f"Update: {res.status_code}")
    assert res.json()['nombre'] == "IVA Test Updated"

    # Delete
    res = requests.delete(f"{BASE_URL}/maestros/condiciones-iva/{created_id}")
    print(f"Delete: {res.status_code}")
    assert res.status_code == 204

def test_tipos_contacto():
    print("\n--- Testing Tipos Contacto ---")
    # Create
    tipo_id = "TEST_TIPO"
    data = {"id": tipo_id, "nombre": "Tipo Test"}
    try:
        requests.delete(f"{BASE_URL}/maestros/tipos-contacto/{tipo_id}") # Cleanup first
    except:
        pass

    res = requests.post(f"{BASE_URL}/maestros/tipos-contacto", json=data)
    print(f"Create: {res.status_code}")
    assert res.status_code == 201

    # Read
    res = requests.get(f"{BASE_URL}/maestros/tipos-contacto")
    print(f"Read All: {res.status_code}")
    assert any(t['id'] == tipo_id for t in res.json())

    # Update
    update_data = {"nombre": "Tipo Test Updated"}
    res = requests.put(f"{BASE_URL}/maestros/tipos-contacto/{tipo_id}", json=update_data)
    print(f"Update: {res.status_code}")
    assert res.json()['nombre'] == "Tipo Test Updated"

    # Delete
    res = requests.delete(f"{BASE_URL}/maestros/tipos-contacto/{tipo_id}")
    print(f"Delete: {res.status_code}")
    assert res.status_code == 204

if __name__ == "__main__":
    try:
        test_provincias()
        test_condiciones_iva()
        test_tipos_contacto()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
