import requests
import json

url = "http://localhost:8000/remitos/ingesta-process"
payload = {
    "cliente": {
        "id": "2fbeb6ebffc649ff81d1e324f410eed6",
        "cuit": "20182604071",
        "razon_social": "BIO-LAB S.A."
    },
    "factura": {
        "numero": "00001-00002531-TRAP",
        "cae": "12345678901234",
        "vto_cae": "2026-12-31"
    },
    "items": [
        {
            "descripcion": "Cofias Descartables Plisadas bca x 100",
            "cantidad": 2000.0,
            "precio_unitario": 41.0
        }
    ],
    "transporte_id": None,
    "bultos": 1,
    "valor_declarado": 0.0,
    "modo_ingesta": "NUEVO"
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
