"""Corre las pruebas de D contra el código del CLON de B (current/), cambiando solo sys.path y chdir. Compara con lo que dieron en D."""
import os, re, subprocess, sys, shutil
SCR = os.path.dirname(os.path.abspath(__file__))   # [S888] las pruebas viven acá, en tests/sesiones/
DEST = os.path.join(r"C:\dev\Sonido_Liquido_V5\scratch", "en_B"); os.makedirs(DEST, exist_ok=True)   # [S888] carpeta ignorada por git
D_ROOT = "C:\\dev\\Sonido_Liquido_V5"; B_APP = "C:\\dev\\_porte_B_ensayo\\current"
PY = r"C:\dev\Sonido_Liquido_V5\backend\venv\Scripts\python.exe"
# prueba -> checks que dio en D
PRUEBAS = [("test_remito_renglon_s876.py", 60), ("test_liberar_despacho.py", 20), ("test_estado_desde_informe.py", 9),
           ("test_informe_g_no_facturables.py", 21), ("test_hub_bit_identidad_null.py", 10), ("test_etapa6_devolucion.py", 20),
           ("test_etapa7b_conciliador.py", 49), ("test_etapa7c_contra_natura.py", 38), ("test_etapa7d_nc_nd.py", 110),
           ("test_backup_semanal.py", 15), ("test_domicilio_fiscal_s878.py", 8),
           ("test_productos_duplicados_s879.py", 45), ("test_p24_cache_index_s879.py", 11), ("test_cantidades_renglon_s879.py", 36), ("test_descuento_renglon_s879.py", 21), ("test_espejo_cae_s881.py", 6), ("test_migrate_049_s881.py", 15), ("test_migrate_050_s882.py", 20), ("test_migrate_051_s882.py", 21), ("test_migrate_052_s882.py", 16), ("test_remito_oc_casillero_s882.py", 14), ("test_migrate_053_s882.py", 32), ("test_migrate_054_s882.py", 15), ("test_migrate_055_s882.py", 30), ("test_migrate_056_s882.py", 9), ("test_cumplimiento_oc_s882.py", 23), ("test_migrate_057_s882.py", 16), ("test_migrate_058_s882.py", 21), ("test_ingesta_espejo_s882.py", 13), ("test_nc_ingesta_s883.py", 8), ("test_migrate_060_s883.py", 20), ("test_transporte_domicilios_s883.py", 22), ("test_alta_pedido_estado_s883.py", 10), ("test_domicilio_bifurcacion_s883.py", 9), ("test_migrate_061_s883.py", 15), ("test_direcciones_similares_s883.py", 42), ("test_hub_similares_s883.py", 14), ("test_guardia_roles_s885.py", 34), ("test_migrate_062_s885.py", 20), ("test_migrate_059_s882.py", 13), ("test_espejo_mensual_s887.py", 18), ("test_remitos_ui_s887.py", 27), ("test_remito_existente_s887.py", 15), ("test_remito_existente_ui_s887.py", 17)]
sel = sys.argv[1:]
resumen = []
for nombre, esperado in PRUEBAS:
    if sel and nombre not in sel: continue
    src = open(os.path.join(SCR, nombre), encoding="utf-8").read()
    # solo los puntos de entrada de código: sys.path.insert(...) y os.chdir(...) de la raíz de D (el resto, bases temporales, queda igual)
    nuevo = re.sub(r'(sys\.path\.insert\(0, r?")' + re.escape(D_ROOT) + r'(\\scripts)?(")', lambda m: m.group(1) + B_APP + (m.group(2) or "") + m.group(3), src)
    nuevo = re.sub(r'(os\.chdir\(r?")' + re.escape(D_ROOT) + r'(")', lambda m: m.group(1) + B_APP + m.group(2), nuevo)
    # tests que fijan la ruta con una variable RAIZ (S879): el codigo sale de B_APP; RAIZ queda en D (scratch, bases temporales)
    if re.search(r'^RAIZ = r"' + re.escape(D_ROOT) + '"', nuevo, re.M):
        nuevo = nuevo.replace("sys.path.insert(0, RAIZ); os.chdir(RAIZ)", f'sys.path.insert(0, r"{B_APP}"); os.chdir(r"{B_APP}")')
        nuevo = nuevo.replace('os.path.join(RAIZ, "scripts"', f'os.path.join(r"{B_APP}", "scripts"')
        assert B_APP in nuevo, "el reemplazo no se aplico"
    if nombre == "test_espejo_mensual_s887.py":   # el espejo vive en la RAIZ de B (scripts/), no en current/
        nuevo = nuevo.replace(B_APP + "\scripts", r"C:\dev\_porte_B_ensayo\scripts"); assert r"_porte_B_ensayo\scripts" in nuevo
    ruta = os.path.join(DEST, nombre); open(ruta, "w", encoding="utf-8").write(nuevo)
    env = dict(os.environ); env["PYTHONIOENCODING"] = "utf-8"; env.pop("DATABASE_URL", None); env["PYTHONPATH"] = SCR
    p = subprocess.run([PY, ruta], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=B_APP, env=env, timeout=900)
    sal = p.stdout + p.stderr
    m = re.findall(r"(\d+)/(\d+) checks OK", sal)
    ok, tot = (int(m[-1][0]), int(m[-1][1])) if m else (-1, -1)
    estado = "OK " if (ok == tot == esperado) else "REVISAR"
    resumen.append((estado, nombre, ok, tot, esperado))
    print(f"{estado:8s} {nombre:38s} {ok}/{tot} (en D: {esperado})", flush=True)
    if estado != "OK ":
        fall = [l for l in sal.splitlines() if "[FAIL]" in l or "FALLO" in l or "Traceback" in l or "Error" in l][:6]
        for l in fall: print("          ", l[:160])
print("\nTODO IGUAL QUE EN D" if all(r[0] == "OK " for r in resumen) else "\nHAY DIFERENCIAS: revisar las líneas REVISAR")
