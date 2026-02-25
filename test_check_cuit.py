import os
import requests
import time
import subprocess

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

print("Attempting to check CUIT...")
try:
    cuit_target = "27123456789"
    res = requests.get(f"http://127.0.0.1:8011/clientes/check-cuit/{cuit_target}", timeout=10)
    print("GET check-cuit response:", res.status_code, res.text)
except requests.exceptions.ConnectionError as e:
    print("Connection refused! server crashed.", e)
except Exception as e:
    print("Request failed:", e)

print("Killing server...")
proc.terminate()
proc.wait(timeout=5)

print("\n--- SERVER OUTPUT ---")
print(proc.stdout.read())
