import requests
import json

API_URL = "http://127.0.0.1:8000/pedidos/"
# Ensure we have a token if needed, but normally GET /pedidos/ might be protected.
# Check auth logic. The router uses Depends(get_db) but maybe global middleware?
# Router definition: router = APIRouter(...)
# In main.py: app.include_router(pedidos_router)
# No implicit auth dependency on the router level shown in router.py snippet.

def check_api():
    try:
        print(f"GET {API_URL}")
        resp = requests.get(API_URL)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Count: {len(data)}")
            print(json.dumps(data[:3], indent=2))
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
