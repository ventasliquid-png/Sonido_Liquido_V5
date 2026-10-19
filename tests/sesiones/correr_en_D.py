import re, subprocess, sys, os
SCR = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(SCR, "correr_en_B.py"), encoding="utf-8").read()
pruebas = re.findall(r'\("(test_[a-z0-9_]+\.py)", (\d+)\)', src)
PY = r"C:\dev\Sonido_Liquido_V5\backend\venv\Scripts\python.exe"
mal = 0
for nombre, esperado in pruebas:
    p = subprocess.run([PY, os.path.join(SCR, nombre)], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=r"C:\dev\Sonido_Liquido_V5", env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=900)
    m = re.findall(r"(\d+)/(\d+) checks OK", p.stdout + p.stderr)
    ok, tot = (int(m[-1][0]), int(m[-1][1])) if m else (-1, -1)
    estado = "OK " if ok == tot == int(esperado) else "REVISAR"
    mal += estado != "OK "
    print(f"{estado:8s} {nombre:38s} {ok}/{tot} (esperado {esperado})", flush=True)
    if estado != "OK ":
        for l in [l for l in (p.stdout + p.stderr).splitlines() if "[FAIL]" in l or "Traceback" in l or "Error" in l][:5]: print("          ", l[:170])
print("\nTODO EN VERDE" if not mal else f"\nHAY {mal} PARA REVISAR")
print("FIN")
