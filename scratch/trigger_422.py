import requests

factura_id = "2715c0ab-9d26-4547-ae34-311db7e5394e"
url = f"http://localhost:8080/facturacion/{factura_id}/sellar"

payload = {
    "cae": "7123",
    "vto_cae": "",  # Empty string instead of None
    "punto_venta": 3,
    "numero_comprobante": 2512,
    "estado": "AUTORIZADA_AFIP"
}

r = requests.patch(url, json=payload)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
