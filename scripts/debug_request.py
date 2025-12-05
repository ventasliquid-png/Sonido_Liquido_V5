import requests
import sys

def test_endpoint(url):
    print(f"--- Testing {url} ---")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Response Body:")
            print(response.text)
        else:
            print("Success! (First 200 chars):")
            print(response.text[:200])
    except Exception as e:
        print(f"Request failed: {e}")
    print("\n")

if __name__ == "__main__":
    base_url = "http://localhost:8000"
    test_endpoint(f"{base_url}/clientes/")
    test_endpoint(f"{base_url}/productos/")
    test_endpoint(f"{base_url}/productos/rubros")
