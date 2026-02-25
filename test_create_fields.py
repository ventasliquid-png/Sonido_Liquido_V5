import os
import requests
import time
import subprocess
import uuid

# Start backend server using venv
env = os.environ.copy()
env['DATABASE_URL'] = 'sqlite:///c:/dev/Sonido_Liquido_V5/pilot.db'
uvicorn_path = r"c:\dev\Sonido_Liquido_V5\backend\venv\Scripts\uvicorn.exe"

print("Starting server for persistence check...")
proc = subprocess.Popen(
    [uvicorn_path, "backend.main:app", "--host", "127.0.0.1", "--port", "8012"],
    cwd=r"c:\dev\Sonido_Liquido_V5",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(5)

try:
    # IDs from typical seed
    SEGMENTO_ID = "8989a55d-cc6e-4e1b-b6b6-03e1d6e7f6ee"
    LISTA_ID = "42ace2cd-aa95-4b7b-9110-1eeb8d2b2279"
    IVA_ID = "966fdb33-d6a6-4e49-9c81-197790567dcb"
    
    payload = {
        "razon_social": "PERSISTENCE TEST CORP",
        "cuit": "20999999991",
        "nombre_fantasia": "FANTASY FIX",
        "segmento_id": SEGMENTO_ID,
        "lista_precios_id": LISTA_ID,
        "condicion_iva_id": IVA_ID,
        "vendedor_id": 1,
        "observaciones": "TESTING ROBUST CREATE",
        "domicilios": [
            {
                "calle": "Test 123",
                "numero": "10",
                "localidad": "Test City",
                "provincia_id": "CABA",
                "es_fiscal": True,
                "activo": True
            }
        ]
    }
    
    print("Testing POST /clientes/...")
    res = requests.post("http://127.0.0.1:8012/clientes/", json=payload, timeout=10)
    data = res.json()
    
    print("POST Response status:", res.status_code)
    
    check_fields = ['segmento_id', 'vendedor_id', 'nombre_fantasia', 'observaciones']
    success = True
    for field in check_fields:
        val = data.get(field)
        expected = payload.get(field)
        print(f"Field '{field}': {val} (Expected: {expected})")
        if str(val) != str(expected) and expected is not None:
             success = False
             
    if success:
        print("✅ SUCCESS: All fields persisted correctly on create.")
    else:
        print("❌ FAILURE: Some fields were lost.")

except Exception as e:
    print("Test failed:", e)

print("Stopping server...")
proc.terminate()
proc.wait()
