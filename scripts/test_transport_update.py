import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_transport_update():
    # 1. Create a transport
    name = f"Test Transport {uuid.uuid4()}"
    payload = {
        "nombre": name,
        "activo": False
    }
    print(f"Creating transport: {name} (Inactive)")
    response = requests.post(f"{BASE_URL}/logistica/empresas", json=payload)
    if response.status_code != 201:
        print(f"Failed to create: {response.text}")
        return
    
    data = response.json()
    t_id = data['id']
    print(f"Created ID: {t_id}, Activo: {data['activo']}")

    # 2. Update to Active
    print("Updating to Active...")
    update_payload = {
        "activo": True,
        "nombre": name # Send name too as frontend sends full object
    }
    response = requests.put(f"{BASE_URL}/logistica/empresas/{t_id}", json=update_payload)
    
    if response.status_code != 200:
        print(f"Failed to update: {response.text}")
        return

    updated_data = response.json()
    print(f"Updated Activo: {updated_data['activo']}")

    if updated_data['activo'] == True:
        print("SUCCESS: Transport activated.")
    else:
        print("FAILURE: Transport did NOT activate.")

if __name__ == "__main__":
    test_transport_update()
