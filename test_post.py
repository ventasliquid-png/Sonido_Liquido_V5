import os
import requests
import time
import subprocess
import uuid

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

print("Attempting to create physical client...")
try:
    payload = {
        "cuit": "27311111111",
        "razon_social": "LEZANO AVILEZ CELESTE",
        "flags_estado": 5,
        "estado_arca": "VALIDADO",
        "condicion_iva_id": "966fdb33-d6a6-4e49-9c81-197790567dcb", # RI
        "lista_precios_id": "42ace2cd-aa95-4b7b-9110-1eeb8d2b2279", # Mayorista
        "segmento_id": "8989a55d-cc6e-4e1b-b6b6-03e1d6e7f6ee", # B
        "activo": True,
        "domicilios": [
            {
                "calle": "SIN DOMICILIO FISCAL",
                "numero": "S/N",
                "localidad": "CABA",
                "provincia_id": "CABA",
                "es_fiscal": True,
                "es_entrega": True,
                "activo": True
            }
        ]
    }
    res = requests.post(f"http://127.0.0.1:8011/clientes/", json=payload, timeout=10)
    print("POST response:", res.status_code, res.text)
except requests.exceptions.ConnectionError as e:
    print("Connection refused! server crashed.", e)
except Exception as e:
    print("Request failed:", e)

print("Killing server...")
proc.terminate()
proc.wait(timeout=5)

print("\n--- SERVER OUTPUT ---")
print(proc.stdout.read())
