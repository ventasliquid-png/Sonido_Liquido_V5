from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
try:
    response = client.get("/stats/dashboard")
    print("STATUS:", response.status_code)
    print("BODY:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    response = client.get("/clientes/?include_inactive=true")
    print("STATUS:", response.status_code)
    print("BODY:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
