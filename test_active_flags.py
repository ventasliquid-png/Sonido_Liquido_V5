import os
import requests
import time
import subprocess
import uuid

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

time.sleep(5)

print("Verifying Active Flag Persistence...")
try:
    cuit_fix = "27999888771"
    payload = {
        "cuit": cuit_fix,
        "razon_social": "TEST FIX FLAG",
        "flags_estado": 4, # GOLD_ARCA (Bit 2) but bit 0 missing
        "estado_arca": "VALIDADO",
        "activo": True, # Should force Bit 0 (1) on flags_estado
        "condicion_iva_id": "966fdb33-d6a6-4e49-9c81-197790567dcb",
        "lista_precios_id": "42ace2cd-aa95-4b7b-9110-1eeb8d2b2279",
        "segmento_id": "8989a55d-cc6e-4e1b-b6b6-03e1d6e7f6ee",
        "domicilios": []
    }
    res = requests.post("http://127.0.0.1:8011/clientes/", json=payload, timeout=10)
    data = res.json()
    print("POST response:", res.status_code)
    print(f"Flags Result: {data.get('flags_estado')} (Expected at least 5)")
    print(f"Activo Result: {data.get('activo')} (Expected True)")
    
    if data.get('activo') == True and (data.get('flags_estado', 0) & 1):
        print("✅ SUCCESS: Client created active with correct flags.")
    else:
        print("❌ FAILURE: Item might still disappear.")
        
except Exception as e:
    print("Request failed:", e)

print("Killing server...")
proc.terminate()
proc.wait(timeout=5)

print("\n--- SERVER OUTPUT ---")
print(proc.stdout.read())
