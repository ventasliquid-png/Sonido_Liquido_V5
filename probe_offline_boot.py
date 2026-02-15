
import requests
import sys

try:
    print("--- [PROBE] Apuntando a http://127.0.0.1:8001/ ...")
    r = requests.get("http://127.0.0.1:8001/")
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
    
    if r.status_code == 200:
        print("--- [SUCCESS] Backend is responding!")
        sys.exit(0)
    else:
        print("--- [FAIL] Backend responded with error.")
        sys.exit(1)
except Exception as e:
    print(f"--- [CRITICAL] Connection failed: {e}")
    sys.exit(1)
