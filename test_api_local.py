import requests
try:
    r = requests.get("http://localhost:8080/clientes/?include_inactive=true", timeout=10)
    print("Status Code:", r.status_code)
    print("Response:", r.text[:1000])
except Exception as e:
    print("Error:", e)
