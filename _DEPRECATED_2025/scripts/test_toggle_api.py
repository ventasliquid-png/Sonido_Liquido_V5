import requests
import json

BASE_URL = "http://localhost:8000/productos"
PRODUCT_ID = 289

def get_status():
    r = requests.get(f"{BASE_URL}/{PRODUCT_ID}")
    try:
        data = r.json()
        return data.get('activo')
    except:
        return None

def test_api_toggle():
    print(f"Testing API Toggle for Product {PRODUCT_ID}...")
    
    initial = get_status()
    print(f"Initial Status: {initial}")
    
    # Toggle 1
    print("Calling DELETE (Toggle)...")
    r = requests.delete(f"{BASE_URL}/{PRODUCT_ID}")
    print(f"Response: {r.status_code}")
    
    new_status = get_status()
    print(f"Status after toggle: {new_status}")
    
    if new_status != initial:
        print("SUCCESS: API Toggle worked.")
    else:
        print("FAILURE: API Toggle did not change status.")
        
    # Toggle Back
    print("Toggle Back...")
    requests.delete(f"{BASE_URL}/{PRODUCT_ID}")
    print(f"Final Status: {get_status()}")

if __name__ == "__main__":
    test_api_toggle()
