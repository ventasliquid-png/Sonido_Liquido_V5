import requests

payload = {
    "cliente": {
        "cuit": "20295915863",
        "razon_social": "FERNANDEZ AGUSTIN TEST"
    },
    "factura": {
        "numero": "0001-00000003",
        "cae": "1234567890",
        "vto_cae": "01/01/2026"
    },
    "items": [
        {
            "descripcion": "ITEM DEBUG 3",
            "cantidad": 1.0,
            "precio_unitario": 0.0,
            "codigo": "DEBUG-03"
        }
    ]
}

try:
    print("Sending request to http://localhost:8000/remitos/ingesta-process")
    res = requests.post("http://localhost:8000/remitos/ingesta-process", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
