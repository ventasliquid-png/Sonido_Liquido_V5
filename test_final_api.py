import requests
import json

base_url = "http://127.0.0.1:8080"

endpoints = [
    "/stats/dashboard",
    "/clientes/?include_inactive=true",
    "/productos?activo=true"
]

for ep in endpoints:
    url = base_url + ep
    print(f"Checking {url}...")
    try:
        response = requests.get(url)
        print(f"  Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"  Error Detail: {response.text}")
    except Exception as e:
        print(f"  Request failed: {e}")
