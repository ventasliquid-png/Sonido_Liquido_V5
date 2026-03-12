import requests
import json

BASE_URL = "http://localhost:8000/productos"
PRODUCT_ID = 289
# Note: Previous script left it toggled, so we don't know state.

def get_status():
    r = requests.get(f"{BASE_URL}/{PRODUCT_ID}")
    try:
        data = r.json()
        return data.get('activo')
    except:
        return None

def test_api_toggle_post():
    print(f"Testing POST Toggle for Product {PRODUCT_ID}...")
    
    initial = get_status()
    print(f"Initial Status: {initial}")
    
    # Toggle 1 (POST)
    print("Calling POST toggle...")
    r = requests.post(f"{BASE_URL}/{PRODUCT_ID}/toggle")
    print(f"Response: {r.status_code}")
    data = r.json()
    print(f"Returned Status: {data.get('activo')}")
    
    new_status = get_status()
    print(f"Confirmed Status via GET: {new_status}")
    
    if new_status != initial and new_status == data.get('activo'):
        print("SUCCESS: POST Toggle worked.")
    else:
        print("FAILURE: POST Toggle did not change status.")

if __name__ == "__main__":
    test_api_toggle_post()
