import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.main import app 
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from fastapi.testclient import TestClient

client = TestClient(app)

def verify_poka_yoke():
    db = SessionLocal()
    try:
        # 1. Prepare a client with Bit 6
        target_client = db.query(Cliente).first()
        if not target_client:
            print("ERROR: No client found to test.")
            return
            
        original_flags = target_client.flags_estado
        target_client.flags_estado = original_flags | 64
        db.commit()
        
        cid = str(target_client.id)
        print(f"Testing with Client: {target_client.razon_social} ({cid}) - Flags: {target_client.flags_estado}")
        
        # Verify from current session
        db.refresh(target_client)
        print(f"RE-Check Flags: {target_client.flags_estado}")

        # 2. Try to create order WITHOUT OC and WITHOUT override
        payload = {
            "cliente_id": cid,
            "items": [{"producto_id": 1, "cantidad": 1, "precio_unitario": 100}],
            "oc": "",
            "oc_override": False
        }
        
        print("\n--- TEST 1: No OC, No Override (Should Fail) ---")
        res = client.post("/pedidos/tactico", json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code != 400:
            print(f"FULL RESPONSE: {res.text}")
        
        assert res.status_code == 400
        
        # 3. Try WITH OC
        print("\n--- TEST 2: With OC (Should Succeed) ---")
        payload["oc"] = "OC-123"
        res = client.post("/pedidos/tactico", json=payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 201
        
        # 4. Try WITHOUT OC but WITH Override
        print("\n--- TEST 3: No OC, With Override (Should Succeed) ---")
        payload["oc"] = ""
        payload["oc_override"] = True
        res = client.post("/pedidos/tactico", json=payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 201
        
        # 5. Try WITH 'S/N' (Should Succeed)
        print("\n--- TEST 4: With 'S/N' (Should Succeed) ---")
        payload["oc"] = "S/N"
        payload["oc_override"] = False
        res = client.post("/pedidos/tactico", json=payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 201
        
        print("\n✅ POKA-YOKE BACKEND VERIFIED!")
        
        # Restore flags
        target_client.flags_estado = original_flags
        db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    verify_poka_yoke()
