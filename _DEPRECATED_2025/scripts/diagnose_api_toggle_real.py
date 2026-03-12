import requests
import sys

BASE_URL = "http://localhost:8000"
PRODUCT_NAME = "30-52744428-0"

def get_product_id():
    # 1. Search for the product to get ID
    print(f"Searching for {PRODUCT_NAME}...")
    try:
        resp = requests.get(f"{BASE_URL}/productos/?search={PRODUCT_NAME}")
        resp.raise_for_status()
        data = resp.json()
        if not data:
            print("Product not found via API search.")
            return None
        
        # Filter exact match if possible, or take first
        target = None
        for p in data:
            if p.get('nombre') == PRODUCT_NAME:
                target = p
                break
        
        if not target:
            target = data[0]
            
        print(f"Found Product ID: {target['id']}, Status: {target['activo']}")
        return target
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return None

def test_toggle(product_id, current_status):
    print(f"\n--- Testing Toggle on ID {product_id} (Currently: {current_status}) ---")
    
    url = f"{BASE_URL}/productos/{product_id}/toggle"
    try:
        # POST request
        print(f"POST {url}")
        resp = requests.post(url)
        
        print(f"Response Code: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error Response: {resp.text}")
            return
            
        new_data = resp.json()
        print(f"New Status from API: {new_data['activo']}")
        
        if new_data['activo'] == current_status:
            print("❌ FAIL: Status did NOT change!")
        else:
            print("✅ SUCCESS: Status changed.")
            
    except Exception as e:
        print(f"Exception during toggle: {e}")

if __name__ == "__main__":
    product = get_product_id()
    if product:
        test_toggle(product['id'], product['activo'])
