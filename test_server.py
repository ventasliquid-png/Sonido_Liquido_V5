import os
import requests
import time
import subprocess

# Start backend server using venv
env = os.environ.copy()
env['DATABASE_URL'] = 'sqlite:///c:/dev/Sonido_Liquido_V5/pilot.db'
print("Starting uvicorn server via venv...")
uvicorn_path = r"c:\dev\Sonido_Liquido_V5\backend\venv\Scripts\uvicorn.exe"

proc = subprocess.Popen(
    [uvicorn_path, "backend.main:app", "--host", "127.0.0.1", "--port", "8011"],
    cwd=r"c:\dev\Sonido_Liquido_V5",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(5) # Wait for startup

print("Attempting to fetch client...")
try:
    res = requests.get("http://127.0.0.1:8011/clientes/?q=Galan", timeout=5)
    clients = res.json()
    if not clients:
        print("Galan not found")
        # Let's get any client to test
        res2 = requests.get("http://127.0.0.1:8011/clientes/?limit=1", timeout=5)
        clients = res2.json()
        
    if clients:
        c = clients[0]
        c_id = c['id']
        print(f"Found client: {c['razon_social']}, ID: {c_id}, CUIT: {c.get('cuit')}")
        
        # Send problematic PUT request
        payload = {
            "cuit": "27123456789", # Forces physical person logic
            "razon_social": c['razon_social'],
            "activo": True,
            "flags_estado": c.get('flags_estado', 0),
            "estado_arca": "VALIDADO",
            "condicion_iva_id": c.get("condicion_iva_id"),
            "segmento_id": c.get("segmento_id"),
            "lista_precios_id": c.get("lista_precios_id")
        }
        print("Sending PUT request with payload...")
        try:
            put_res = requests.put(f"http://127.0.0.1:8011/clientes/{c_id}", json=payload, timeout=5)
            print("PUT response:", put_res.status_code, put_res.text)
        except requests.exceptions.ConnectionError as e:
            print("Connection refused! server crashed.", e)
            
except Exception as e:
    print("Request failed:", e)

print("Killing server...")
proc.terminate()
proc.wait(timeout=5)

print("\n--- SERVER OUTPUT ---")
print(proc.stdout.read())
