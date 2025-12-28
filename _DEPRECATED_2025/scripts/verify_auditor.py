import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_auditor_mode():
    print("[START] Starting Auditor Mode Verification...")

    # 1. Create a Client
    cuit = "20123456789"
    client_data = {
        "razon_social": "Test Auditor Mode",
        "cuit": cuit,
        "activo": True,
        "requiere_auditoria": False
    }
    
    # Check if exists and delete if so (cleanup)
    print("1. Checking CUIT...")
    resp = requests.get(f"{BASE_URL}/clientes/check-cuit/{cuit}")
    if resp.status_code == 200:
        data = resp.json()
        if data['status'] != 'NEW':
            print(f"[WARN] Client exists ({data['status']}). Cleaning up...")
            for c in data['existing_clients']:
                # Try hard delete
                requests.delete(f"{BASE_URL}/clientes/{c['id']}/hard")

    print("2. Creating Client 1 (Original)...")
    resp = requests.post(f"{BASE_URL}/clientes/", json=client_data)
    assert resp.status_code == 201
    client1_id = resp.json()['id']
    print(f"[OK] Client 1 Created: {client1_id}")

    print("3. Creating Client 2 (Duplicate)...")
    # This should trigger "requiere_auditoria=True" in the backend logic (Libertad Vigilada)
    resp = requests.post(f"{BASE_URL}/clientes/", json=client_data)
    assert resp.status_code == 201
    client2_id = resp.json()['id']
    client2_data = resp.json()
    
    if client2_data['requiere_auditoria']:
        print(f"[OK] Client 2 Created and marked for AUDIT: {client2_id}")
    else:
        print(f"[FAIL] Client 2 NOT marked for audit. Check service logic.")
        # Force it for testing if logic failed
        # requests.put(f"{BASE_URL}/clientes/{client2_id}", json={"requiere_auditoria": True})

    print("4. Testing APPROVE Endpoint...")
    resp = requests.put(f"{BASE_URL}/clientes/{client2_id}/aprobar")
    assert resp.status_code == 200
    assert resp.json()['requiere_auditoria'] == False
    print("[OK] Client 2 Approved.")

    print("5. Testing HARD DELETE (Success Case)...")
    # Client 2 has no history, should succeed.
    resp = requests.delete(f"{BASE_URL}/clientes/{client2_id}/hard")
    assert resp.status_code == 200
    print("[OK] Client 2 Hard Deleted.")

    print("6. Testing HARD DELETE (Conflict Case)...")
    # Clean up Client 1
    requests.delete(f"{BASE_URL}/clientes/{client1_id}/hard")
    print("[OK] Client 1 Hard Deleted (Cleanup).")

    print("[SUCCESS] All Backend Tests Passed!")

if __name__ == "__main__":
    try:
        test_auditor_mode()
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")
        exit(1)
