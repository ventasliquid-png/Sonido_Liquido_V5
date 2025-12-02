import requests
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    print("--- Autenticando Usuario Admin ---")
    url = f"{BASE_URL}/auth/token"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Authentication failed: {response.text}")
            return None
    except Exception as e:
        print(f"Authentication exception: {e}")
        return None

def test_agenda_lifecycle():
    token = get_auth_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Persona
    print("Creating persona...")
    persona_data = {
        "nombre_completo": "Test User Lifecycle",
        "email_personal": "lifecycle@example.com",
        "celular_personal": "111222333",
        "observaciones": "Test note",
        "activo": True
    }
    response = requests.post(f"{BASE_URL}/agenda/personas", json=persona_data, headers=headers)
    if response.status_code != 201:
        print(f"Failed to create persona: {response.text}")
        return
    
    persona = response.json()
    persona_id = persona["id"]
    print(f"Created persona: {persona_id} - Activo: {persona['activo']}")

    # 2. Update Activo to False
    print("Deactivating persona...")
    update_data = {"activo": False}
    response = requests.put(f"{BASE_URL}/agenda/personas/{persona_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to update persona: {response.text}")
        return
    
    updated_persona = response.json()
    print(f"Updated persona: {updated_persona['id']} - Activo: {updated_persona['activo']}")
    
    if updated_persona['activo'] is not False:
        print("ERROR: Persona was not deactivated in PUT response!")
    else:
        print("SUCCESS: Persona deactivated in PUT response.")

    # 3. Verify with Get
    print("Verifying with GET...")
    response = requests.get(f"{BASE_URL}/agenda/personas/{persona_id}", headers=headers)
    fetched_persona = response.json()
    print(f"Fetched persona: {fetched_persona['id']} - Activo: {fetched_persona['activo']}")

    if fetched_persona['activo'] is not False:
        print("ERROR: Fetched persona is still active!")
    else:
        print("SUCCESS: Fetched persona is inactive.")

if __name__ == "__main__":
    test_agenda_lifecycle()
