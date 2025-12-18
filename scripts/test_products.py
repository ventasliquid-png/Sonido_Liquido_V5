import requests
import os

try:
    # Try localhost first (since we fixed api.js to point to it)
    response = requests.get('http://localhost:8000/productos/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        products = response.json()
        print(f"Count: {len(products)}")
        if len(products) > 0:
            pid = products[0]['id']
            print(f"Fetching details for ID: {pid}")
            detail = requests.get(f'http://localhost:8000/productos/{pid}')
            print(f"Detail Status: {detail.status_code}")
            print(detail.json().get('nombre'))
    else:
        print(response.text)
except Exception as e:
    print(e)
