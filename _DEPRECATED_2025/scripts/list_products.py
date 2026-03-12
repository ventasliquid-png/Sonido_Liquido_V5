import requests

try:
    response = requests.get('http://localhost:8000/productos/?limit=5')
    data = response.json()
    print("Available Products:")
    for p in data:
        print(f"- {p['nombre']} (ID: {p['id']})")
except Exception as e:
    print(e)
