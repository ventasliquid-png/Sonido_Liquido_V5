r"""Card #164 (S894, 28/10): con una bonificación en la factura, el IVA quedaba calculado sobre los renglones SIN bonificar (el parser
los lee como cantidad x precio) y las percepciones, negativas. Caso real: Wullich 2616, 2617 y 2620 en P. Arreglo: desglose_importes
lleva la base de cada alícuota al neto de ARCA; migrate_070 corrige las ya guardadas; auditoria_facturas.py compara el IVA 21 %.
Sobre COPIAS de la base de P del 27/10 15:58 (con las cinco facturas reales cargadas después del arreglo de la S882)."""
import sys, os, re, sqlite3, subprocess, json
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
import fitz
fitz.TOOLS.mupdf_display_errors(False)
import openpyxl
from backend.ingesta.conciliador import desglose_importes
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261027_1558.db"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_070_iva_facturas_bonificadas.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def pie_iva21(pdf):
    """El IVA 21 % del pie del PDF, tal como lo imprime ARCA."""
    m = re.search(r"IVA 21%:\s*\$?\s*([\d\.,]+)", fitz.open(stream=pdf, filetype="pdf")[0].get_text())
    return float(m.group(1).replace(".", "").replace(",", ".")) if m else None
def iva_auditoria(db, nombre):
    """Las filas con diferencia de IVA 21 % que da auditoria_facturas.py."""
    salida = os.path.join(RAIZ, "scratch", nombre)
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "auditoria_facturas.py"), "--db", db, "--salida", salida],
                       capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    filas = []
    wb = openpyxl.load_workbook(salida, read_only=True)
    for ws in wb.worksheets:
        filas += [tuple(c for c in fila if c not in (None, "")) for fila in ws.iter_rows(values_only=True) if any("IVA 21 %" in str(c) for c in fila if c)]
    wb.close(); os.remove(salida)
    return r.returncode, sorted({next((c for c in f if re.fullmatch(r"\d{5}-\d{8}", str(c))), "?") for f in filas})

MAL = {2616: (876960.0, -43848.0), 2617: (48720.0, -2436.0), 2620: (350784.0, -17539.2)}
partida = {n: (iva, per) for n, iva, per in q(ORIG, "select numero_comprobante, round(iva_21,2), round(percepciones,2) from facturas where tipo_comprobante='FACTURA_A' and numero_comprobante in (2616,2617,2620)")}
check(f"partida (P del 27/10): las tres de Wullich con bonificación guardan el IVA sin bonificar y percepciones negativas {partida}", partida == MAL)

# ---------- desglose_importes con los PDF reales ----------
raws = q(ORIG, "select filename, pdf_bytes, parsed_data_raw from ingesta_facturas_raw where filename like '%_00002616 %' or filename like '%_00002617 %' "
               "or filename like '%_00002618 %' or filename like '%_00002619 %' or filename like '%_00002620 %' order by filename")
check(f"están los cinco PDF guardados (2616 a 2620) [{len(raws)}]", len(raws) == 5)
for fn, pdf, raw in raws:
    d = json.loads(raw); f = d["factura"]; nro = int(f["numero"][-8:])
    items = [{"subtotal": it["subtotal"], "alicuota_iva": it.get("alicuota_iva", 21.0)} for it in d["items"]]
    neto, iva21, iva105, exento, percep, total = desglose_importes({"total_neto": f["total_neto"], "total_final": f["total_final"]}, items)
    pie = pie_iva21(pdf)
    check(f"{nro}: el IVA 21 % calculado ({round(iva21, 2)}) es el del pie del PDF ({pie}), sin percepciones [{percep}] y neto + IVA = total",
          pie is not None and abs(round(iva21, 2) - pie) < 0.011 and percep == 0.0 and abs(neto + iva21 + iva105 + exento - total) < 0.011)
# casos armados
r = desglose_importes({"total_neto": 1900.0, "total_final": 1900.0 + 199.5 + 99.75}, [{"subtotal": 1000.0, "alicuota_iva": 21.0}, {"subtotal": 1000.0, "alicuota_iva": 10.5}])
check(f"dos alícuotas con 5 % de bonificación: cada base se lleva al neto (IVA 21 % 199,50 y 10,5 % 99,75) {tuple(round(x, 2) for x in r)}",
      abs(r[1] - 199.5) < 0.001 and abs(r[2] - 99.75) < 0.001 and r[4] == 0.0)
r = desglose_importes({"total_neto": 1000.0, "total_final": 1250.0}, [{"subtotal": 1000.0, "alicuota_iva": 21.0}])
check(f"sin bonificación todo sigue igual y una percepción real queda (IVA 210, percepciones 40) {tuple(round(x, 2) for x in r)}", r[1] == 210.0 and r[4] == 40.0)
r = desglose_importes({"total_neto": None, "total_final": None}, [{"subtotal": 1000.0, "alicuota_iva": 21.0}])
check(f"sin el neto de ARCA no se prorratea nada (neto = renglones, IVA 210) {tuple(round(x, 2) for x in r)}", r[0] == 1000.0 and r[1] == 210.0 and r[5] == 1210.0)
src = open(os.path.join(RAIZ, "backend", "remitos", "service.py"), encoding="utf-8").read()
check("el modo espejo de la ingesta usa el mismo desglose", "from backend.ingesta.conciliador import desglose_importes" in src)

# ---------- la auditoría ve el IVA ----------
rc, malas = iva_auditoria(ORIG, "test_iva_aud_antes.xlsx")
check(f"auditoria_facturas.py ahora compara el IVA 21 %: marca justo las tres [{rc}] {malas}", rc == 0 and malas == ["00001-00002616", "00001-00002617", "00001-00002620"])

# ---------- migrate_070 ----------
A = copia("test_070_a.db")
def resto(db):
    return (q(db, "select id, estado, neto_gravado, total, iva_21, percepciones, notas_auditoria from facturas where numero_comprobante not in (2616,2617,2620) or tipo_comprobante != 'FACTURA_A' order by id"),
            q(db, "select id, cantidad, precio_unitario_neto, subtotal_neto from facturas_items order by id"),
            q(db, "select id, numero_comprobante, neto_gravado, total, estado from facturas order by id"))
antes = resto(A)
rc, out = migrar(A)
check(f"corre sin error y corrige tres [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "corregidas 3, saltadas 0, con error 0" in out)
pies = {int(re.search(r"_(\d{8}) ", fn).group(1)): pie_iva21(pdf) for fn, pdf, raw in raws}
despues = {n: (iva, per) for n, iva, per in q(A, "select numero_comprobante, round(iva_21,2), round(percepciones,2) from facturas where tipo_comprobante='FACTURA_A' and numero_comprobante in (2616,2617,2620)")}
check(f"2616, 2617 y 2620: el IVA 21 % es el de ARCA y las percepciones quedan en cero {despues}", all(abs(despues[n][0] - pies[n]) < 0.011 and despues[n][1] == 0.0 for n in MAL))
notas = dict(q(A, "select numero_comprobante, notas_auditoria from facturas where tipo_comprobante='FACTURA_A' and numero_comprobante in (2616,2617,2620)"))
check("la nota de auditoría conserva la original y suma la marca [SISTEMA] con el antes y el después (2616: 876960.0 -> 833112.0)",
      all("GENERADA POR MODO ESPEJO" in n and "[SISTEMA] IVA recalculado sobre el neto bonificado de ARCA" in n for n in notas.values())
      and "IVA 21 % 876960.0 -> 833112.0" in notas[2616])
check("nada más cambia: neto, total, estado, renglones y las demás facturas", resto(A) == antes)
rc, malas = iva_auditoria(A, "test_iva_aud_despues.xlsx")
check(f"la auditoría después de la migración: ninguna diferencia de IVA [{rc}] {malas}", rc == 0 and malas == [])
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '070%'"); con.commit(); con.close()
snap = resto(A); rc3, out3 = migrar(A)
check(f"sin el registro: no queda nada con percepciones negativas y no toca nada [{rc3}]", rc3 == 0 and "0 comprobante(s)" in out3 and resto(A) == snap)
os.remove(A)

# ---------- guarda: lo que no cierra no se toca ----------
G = copia("test_070_g.db"); con = sqlite3.connect(G); con.execute("update facturas set total = total - 50000 where tipo_comprobante='FACTURA_A' and numero_comprobante=2616"); con.commit(); con.close()
rcg, outg = migrar(G)
g = q(G, "select numero_comprobante, round(iva_21,2) from facturas where tipo_comprobante='FACTURA_A' and numero_comprobante in (2616,2617,2620) order by 1")
check(f"guarda: si con el IVA prorrateado no cierra el total (2616 con 50.000 menos), esa queda como estaba y avisa; las otras dos se corrigen [{rcg}] {g}",
      rcg == 0 and "corregidas 2, saltadas 1" in outg and "AVISO -- 00001-00002616" in outg and g[0] == (2616, 876960.0) and g[1][1] != 48720.0)
os.remove(G)

ok = sum(1 for _, c in checks if c)
print(f"\n{ok}/{len(checks)} checks OK")
sys.exit(0 if ok == len(checks) else 1)
