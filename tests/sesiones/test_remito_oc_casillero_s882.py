r"""Sugerencia de Tomy (S882): la OC del pedido se imprime en el casillero "ORDEN DE COMPRA N°:" del talonario preimpreso (antes la escribia a mano).
Motor del PDF + endpoint GET /remitos/{id}/pdf, sobre una COPIA de la base de P."""
import sys, os, shutil, sqlite3, glob
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.remitos.remito_engine import generar_remito_pdf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
MM = 72 / 25.4
TMPDIR = os.path.join(RAIZ, "scratch", "test_oc_casillero"); os.makedirs(TMPDIR, exist_ok=True)

def palabras_en_casillero(pdf_path, pagina=None):
    """palabras del PDF dentro del casillero de la OC: x desde 165 mm, y entre 80 y 95 mm (nada mas se imprime ahi)."""
    doc = fitz.open(pdf_path); out = []
    for i, pag in enumerate(doc):
        if pagina is not None and i != pagina: continue
        for x0, y0, x1, y1, w, *_ in pag.get_text("words"):
            if x0 >= 165 * MM and 80 * MM <= y0 <= 95 * MM: out.append((i, w, x0 / MM, y0 / MM, x1 / MM))
    return out

def generar(oc, nombre):
    p = os.path.join(TMPDIR, nombre + ".pdf")
    cli = {"razon_social": "LABORATORIO DE MEDICINA SA", "cuit": "30-58105030-1", "domicilio_fiscal": "TRELLES 1566 CABA", "condicion_iva": "RESPONSABLE INSCRIPTO",
           "referencia": "Pedido #29", "oc": oc}
    generar_remito_pdf(cli, [{"codigo": "1", "descripcion": "TOALLA", "cantidad": 6, "unidad": "UN"}], is_preview=False, output_path=p, numero_remito="0015-00003025")
    return p

# ---- motor ----
p = generar("4500123456", "corta")
w = palabras_en_casillero(p)
check(f"OC corta: sale en el casillero, en las 3 copias (original, duplicado, triplicado) {[(a, b) for a, b, *_ in w]}", sorted({a for a, *_ in w}) == [0, 1, 2] and all(b == "4500123456" for _, b, *_ in w))
x0 = min(t[2] for t in w); x1 = max(t[4] for t in w)
check(f"queda a la derecha de la etiqueta (>= 166.8 mm) y dentro del formulario (<= 201 mm): {x0:.1f}..{x1:.1f} mm", x0 >= 166.8 and x1 <= 201)
y = [t[3] for t in w][0]
check(f"altura alineada con la etiqueta (81..86 mm): {y:.1f} mm", 81 <= y <= 86)

p = generar("", "vacia")
check("sin OC: el casillero queda libre (nada impreso)", not palabras_en_casillero(p))
p = generar(None, "none")
check("OC None: el casillero queda libre y no dice 'S/D'", not palabras_en_casillero(p) and "S/D" not in "".join(pg.get_text() for pg in fitz.open(p)))

p = generar("OC 4500123456/2026", "con_espacio")
w = palabras_en_casillero(p, 0)
check(f"OC de 18 caracteres entra en una linea a tamaño normal {[t[1] for t in w]}", [t[1] for t in w] == ["OC", "4500123456/2026"] and max(t[4] for t in w) <= 201)

largo = "PO-2026-LABMED-000123456-REV2"
p = generar(largo, "larga")
w = palabras_en_casillero(p, 0)
filas = sorted({round(t[3], 0) for t in w})
check(f"OC de 28 caracteres: se parte en {len(filas)} renglones, todos dentro del formulario (<= 201 mm)", 2 <= len(filas) <= 3 and max(t[4] for t in w) <= 201)
check(f"no se pierde ningun caracter al partirla ({''.join(t[1] for t in w)})", "".join(t[1] for t in w) == largo)
p = generar("ORDEN DE COMPRA INTERNA 2026 LABORATORIO DE MEDICINA 000123456789 EXT " * 3, "absurda")
check("una OC absurdamente larga no rompe el PDF y no pasa de 3 renglones", len({round(t[3], 0) for t in palabras_en_casillero(p, 0)}) <= 3)
p = generar("OC N° 123 — ñandú", "acentos")
check(f"caracteres fuera de latin-1 (raya larga) no rompen el PDF y se imprimen {[t[1] for t in palabras_en_casillero(p, 0)]}", "123" in [t[1] for t in palabras_en_casillero(p, 0)])

# ---- endpoint: GET /remitos/{id}/pdf sobre una copia de P ----
# [S895] Fijada a la copia de P del 28/10 12:52, ANTERIOR al despliegue del paquete (Tomy relanzó a las 13:03): esta prueba corre migraciones sobre la copia de P
# y con una copia más nueva ya vienen aplicadas (SKIP). Mismo criterio que las de la S890 (auditoría de CA, 28/10).
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1252.db"
T = os.path.join(RAIZ, "scratch", "test_oc_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
con = sqlite3.connect(T)
rid, pid, nl = con.execute("select r.id, r.pedido_id, r.numero_legal from remitos r where r.numero_legal like '0016%2551'").fetchone()
con.execute("update pedidos set oc='OC-7788/2026' where id=?", (pid,)); con.commit(); con.close()
r = cli.get(f"/remitos/{rid}/pdf")
out = os.path.join(TMPDIR, "endpoint_con_oc.pdf"); open(out, "wb").write(r.content)
txt = "".join(pg.get_text() for pg in fitz.open(out)) if r.status_code == 200 else ""
check(f"endpoint con OC en el pedido [{r.status_code}]: sale 'OC-7788/2026' en el casillero {[t[1] for t in palabras_en_casillero(out, 0)]}", r.status_code == 200 and "OC-7788/2026" in [t[1] for t in palabras_en_casillero(out, 0)])
check("la linea REF dice solo el pedido (sin 'OC:' ni 'S/D')", f"REF: Pedido #{pid}" in txt and "OC:" not in txt and "S/D" not in txt)
con = sqlite3.connect(T); con.execute("update pedidos set oc=NULL where id=?", (pid,))
# [S891] la reimpresión de un remito IMPRESO es la imagen del primer papel: para ver el casillero sin OC se dibuja un papel nuevo
con.execute("update remitos set flags_estado = coalesce(flags_estado, 0) & ~? where id=?", (1 << 44, rid)); con.commit(); con.close()
r2 = cli.get(f"/remitos/{rid}/pdf"); out2 = os.path.join(TMPDIR, "endpoint_sin_oc.pdf"); open(out2, "wb").write(r2.content)
check(f"endpoint sin OC [{r2.status_code}]: el casillero queda libre", r2.status_code == 200 and not palabras_en_casillero(out2))
check("el remito mantiene su numero 0016-00002551 en el PDF (no se renumera)", "0016-00002551" in "".join(pg.get_text() for pg in fitz.open(out2)))
del cli; eng.dispose()

# limpieza: el endpoint escribe en DOCUMENTOS_GENERADOS_RAR/Remitos de salida dentro del repo
gen = os.path.join(RAIZ, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida", "remito_0016_00002551.pdf")
if os.path.exists(gen): os.remove(gen)
shutil.rmtree(TMPDIR, ignore_errors=True)
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
