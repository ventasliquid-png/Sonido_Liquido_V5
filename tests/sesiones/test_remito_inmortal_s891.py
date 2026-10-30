r"""S891, paquete 2 de remitos, tramo 2 (reglas de Carlos y Nike del 20 al 22/10): el remito con número es inmortal.
(1) Vista previa de un remito SIN número: marca VISTA PREVIA, no toma número, no se marca impreso, no se guarda.
(2) Imprimir: toma número y el PDF de ese momento queda como la IMAGEN DE LO IMPRESO; reimprimir entrega esa misma imagen aunque
    cambien los datos, con una nota [SISTEMA] por reimpresión. Un remito viejo (sin imagen) se regenera, también con nota.
(3) Anular con motivo (no sin número, no facturado), las cantidades vuelven a quedar pendientes; deshacer con motivo, bloqueado por
    cantidades si otro remito ya las cubrió; la cicatriz FUE_ANULADO queda.
(4) Un remito con número no se borra (tacho) ni se edita (PATCH, ni siquiera mandando `estado`).
(5) Pantallas (estática). Sobre una COPIA de P con migrate_066 aplicada."""
import sys, os, shutil, sqlite3, glob, subprocess, hashlib, io
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.remitos.genoma import describir
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_inmortal_s891"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
r = subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", "migrate_066_remitos_genoma_fecha_emision.py")], capture_output=True, text=True,
                   encoding="utf-8", env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
asegurar_esquema(T)
check(f"setup: copia de P con migrate_066 [rc {r.returncode}]", r.returncode == 0)

from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
import backend.remitos.router as _router
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__))))
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida"); IMAGENES = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
_aparte = imagenes_aparte(BASE); _aparte.__enter__()   # la carpeta de imágenes vacía mientras corre: otras copias de P dejan los mismos números
previos = {d: set(os.listdir(d)) if os.path.isdir(d) else set() for d in (SALIDA, IMAGENES)}
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
def h(x): return x.replace("-", "")
def guid(x): x = h(x); return f"{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}"
def notas(rid): return [n for (n,) in q("select texto from remitos_notas where remito_id=? order by id", h(rid))]
def gen(rid): return describir(q("select flags_estado from remitos where id=?", h(rid))[0][0])
def texto(contenido): return " ".join(fitz.open(stream=contenido, filetype="pdf")[0].get_text().split())

pend = q("""select pi.pedido_id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
            where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) from pedidos_items pi join pedidos p on p.id=pi.pedido_id where p.estado='PENDIENTE' order by pi.pedido_id desc""")
pend = [(p, i, x) for p, i, x in pend if x and x > 0]
(p1, i1, x1) = pend[0]
r = cli.post("/remitos/armar", json={"pedido_id": p1, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": i1, "cantidad": x1}]})
rid = r.json()["id"] if r.status_code == 200 else ""

# ---- (1) vista previa
rp = cli.get(f"/remitos/{rid}/pdf?vista_previa=1")
check(f"vista previa de un remito sin número [{rp.status_code}]: dice VISTA PREVIA - SIN VALIDEZ, entera dentro de la hoja", rp.status_code == 200 and "VISTA PREVIA - SIN VALIDEZ" in texto(rp.content))
check("la vista previa no le da número, no lo marca impreso y no guarda imagen",
      q("select numero_legal from remitos where id=?", h(rid))[0][0] is None and "IMPRESO" not in gen(rid)["marcas"]
      and not any(f.endswith(".pdf") and f not in previos[IMAGENES] for f in (os.listdir(IMAGENES) if os.path.isdir(IMAGENES) else [])))

# ---- (2) imprimir, imagen guardada, reimprimir
rp = cli.get(f"/remitos/{rid}/pdf")
num = q("select numero_legal from remitos where id=?", h(rid))[0][0]
imagen = os.path.join(IMAGENES, f"remito_{(num or '').replace('-', '_')}.pdf")
check(f"imprimir: toma número ({num}), queda IMPRESO y se guarda la imagen de lo impreso [{rp.status_code}]",
      rp.status_code == 200 and num and "IMPRESO" in gen(rid)["marcas"] and os.path.exists(imagen))
original = rp.content
check("la imagen guardada es exactamente el PDF que se imprimió", hashlib.sha256(open(imagen, "rb").read()).hexdigest() == hashlib.sha256(original).hexdigest())
check("la primera impresión no deja nota de reimpresión", not [n for n in notas(rid) if "Reimpresión" in n])
q("update remitos set bultos=99, valor_declarado=12345 where id=?", h(rid))   # cambian los datos después de imprimir
q("update pedidos set nota='CAMBIO POSTERIOR' where id=?", p1)
rp2 = cli.get(f"/remitos/{rid}/pdf")
check(f"reimprimir entrega LA MISMA imagen aunque cambiaron los datos (bultos, valor, nota del pedido) [{rp2.status_code}]",
      rp2.status_code == 200 and hashlib.sha256(rp2.content).hexdigest() == hashlib.sha256(original).hexdigest() and "CAMBIO POSTERIOR" not in texto(rp2.content))
check("cada reimpresión deja una nota [SISTEMA]", len([n for n in notas(rid) if n.startswith("[SISTEMA] Reimpresión del remito")]) == 1)
check("reimprimir no cambia el número", q("select numero_legal from remitos where id=?", h(rid))[0][0] == num)
viejo = q("select id from remitos where numero_legal='0015-00003027'")[0][0]
q("update remitos set flags_estado = flags_estado | ? where id=?", 1 << 44, viejo)
rp = cli.get(f"/remitos/{guid(viejo)}/pdf")
check(f"remito impreso antes de guardar imágenes (3027): se regenera, deja nota y desde ahí esa es su imagen [{rp.status_code}]",
      rp.status_code == 200 and any("no había imagen guardada" in n for n in notas(viejo)) and os.path.exists(os.path.join(IMAGENES, "remito_0015_00003027.pdf")))
q("update remitos set bultos=77 where id=?", viejo)
rp2 = cli.get(f"/remitos/{guid(viejo)}/pdf")
check(f"y la reimpresión siguiente del 3027 ya es esa imagen, aunque cambien los datos [{rp2.status_code}]",
      rp2.status_code == 200 and rp2.content == rp.content and "BULTOS: 77" not in texto(rp2.content)
      and len([n for n in notas(viejo) if "no había imagen guardada" in n]) == 1)
# un 0015 que salió SIN PAPEL (con número, sin IMPRESO): su primer papel, aunque sea días después, es el que queda como imagen
sin_papel = q("select id, numero_legal from remitos where numero_legal='0015-00003028'")[0]
q("update remitos set flags_estado = flags_estado & ~? where id=?", 1 << 44, sin_papel[0])
img_sp = os.path.join(IMAGENES, f"remito_{sin_papel[1].replace('-', '_')}.pdf")
rp = cli.get(f"/remitos/{guid(sin_papel[0])}/pdf")
rp2 = cli.get(f"/remitos/{guid(sin_papel[0])}/pdf")
check(f"un 0015 que salió sin papel (3028 sin IMPRESO): el primer papel queda como imagen, con el mismo número, y reimprimirlo da ese mismo [{rp.status_code}/{rp2.status_code}]",
      rp.status_code == 200 and os.path.exists(img_sp) and "IMPRESO" in gen(sin_papel[0])["marcas"] and rp2.content == rp.content
      and q("select numero_legal from remitos where id=?", sin_papel[0])[0][0] == sin_papel[1]
      and not any("no había imagen guardada" in n for n in notas(sin_papel[0])))
# una imagen ajena con el mismo número (en D la deja otra copia de la base) no se entrega en el primer papel
num_ajeno = q("select numero_legal from remitos where numero_legal like '0015-%' order by numero_legal desc limit 1")[0][0]
siguiente = f"0015-{int(num_ajeno.split('-')[1]) + 1:08d}"
open(os.path.join(IMAGENES, f"remito_{siguiente.replace('-', '_')}.pdf"), "wb").write(b"%PDF-1.4 imagen ajena")
r = cli.post("/remitos/armar", json={"pedido_id": pend[2][0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": pend[2][1], "cantidad": pend[2][2]}]})
ajeno = r.json()["id"] if r.status_code == 200 else ""
rp = cli.get(f"/remitos/{ajeno}/pdf")
check(f"primer papel con una imagen ajena del mismo número ({siguiente}) en la carpeta: genera el suyo y la pisa [{rp.status_code}]",
      rp.status_code == 200 and q("select numero_legal from remitos where id=?", h(ajeno))[0][0] == siguiente and b"imagen ajena" not in rp.content
      and open(os.path.join(IMAGENES, f"remito_{siguiente.replace('-', '_')}.pdf"), "rb").read() == rp.content)

# ---- (3) anular y deshacer
rnum = guid(rid)
r = cli.post("/remitos/armar", json={"pedido_id": pend[1][0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": pend[1][1], "cantidad": pend[1][2]}]})
sin_num = r.json()["id"] if r.status_code == 200 else ""
r = cli.post(f"/remitos/{sin_num}/anular", json={"motivo": "x"})
check(f"un remito sin número no se anula: 409 REMITO_SIN_NUMERO (se descarta) [{r.status_code}]", r.status_code == 409 and "REMITO_SIN_NUMERO" in r.text)
r = cli.post(f"/remitos/{rnum}/anular", json={"motivo": "  "})
check(f"anular sin motivo: 422 [{r.status_code}]", r.status_code == 422 and "MOTIVO_OBLIGATORIO" in r.text)
entregado_antes = q("select coalesce(sum(ri.cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id where ri.pedido_item_id=? and r.estado<>'ANULADO'", i1)[0][0]
r = cli.post(f"/remitos/{rnum}/anular", json={"motivo": "Se imprimió con el domicilio equivocado"})
check(f"anular con motivo [{r.status_code}]: ANULADO + FUE_ANULADO, nota con el estado anterior", r.status_code == 200 and gen(rid)["estado"] == "ANULADO"
      and "FUE_ANULADO" in gen(rid)["marcas"] and any(n.startswith("[SISTEMA] Remito anulado (estado anterior: BORRADOR). Motivo: Se imprimió") for n in notas(rid)))
entregado_desp = q("select coalesce(sum(ri.cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id where ri.pedido_item_id=? and r.estado<>'ANULADO'", i1)[0][0]
check(f"las cantidades vuelven a quedar pendientes en el pedido ({entregado_antes:g} -> {entregado_desp:g})", entregado_desp == entregado_antes - x1)
r = cli.post(f"/remitos/{rnum}/anular", json={"motivo": "otra vez"})
check(f"anular un anulado: 409 [{r.status_code}]", r.status_code == 409 and "REMITO_YA_ANULADO" in r.text)
r = cli.post(f"/remitos/{rnum}/deshacer-anulacion", json={"motivo": "Fue un error, el papel estaba bien"})
check(f"deshacer la anulación sin sustituto [{r.status_code}]: vuelve a BORRADOR (su estado anterior), EMITIDO, y FUE_ANULADO queda",
      r.status_code == 200 and r.json()["estado"] == "BORRADOR" and gen(rid)["estado"] == "EMITIDO" and "FUE_ANULADO" in gen(rid)["marcas"]
      and any(n.startswith("[SISTEMA] Anulación revertida (vuelve a BORRADOR)") for n in notas(rid)))
# con sustituto: se anula, se hace otro remito por lo mismo, y deshacer se bloquea
cli.post(f"/remitos/{rnum}/anular", json={"motivo": "de nuevo"})
r = cli.post("/remitos/armar", json={"pedido_id": p1, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": i1, "cantidad": x1}]})
sust = r.json()["id"] if r.status_code == 200 else ""
cli.get(f"/remitos/{sust}/pdf")
num_sust = q("select numero_legal from remitos where id=?", h(sust))[0][0]
check(f"el remito sustituto toma otro número ({num_sust}), no el del anulado ({num})", num_sust and num_sust != num)
r = cli.post(f"/remitos/{rnum}/deshacer-anulacion", json={"motivo": "intento"})
check(f"deshacer con un sustituto que cubrió las cantidades: 409 REMITO_SUSTITUIDO diciendo cuál [{r.status_code}]",
      r.status_code == 409 and "REMITO_SUSTITUIDO" in r.text and num_sust in r.text)
# facturado de verdad en P: el vínculo facturas_remitos (la columna FACTURA del listado). El banco lo encontró: la primera guarda miraba solo
# cantidad_facturada, que en P casi nunca está cargada, y dejaba anular el 3032 con su factura 0001-00002619.
r32 = q("select id from remitos where numero_legal='0015-00003032'")[0][0]
f32 = q("""select printf('%04d-%08d', f.punto_venta, f.numero_comprobante) from facturas f join facturas_remitos fr on fr.factura_id=f.id
           where replace(fr.remito_id,'-','')=? and f.numero_comprobante is not null and upper(coalesce(f.estado,'')) not like 'ANULAD%'""", h(r32))
r = cli.post(f"/remitos/{guid(r32)}/anular", json={"motivo": "x"})
check(f"anular el 3032, amparado por su factura {f32[0][0] if f32 else '?'}: 409 REMITO_FACTURADO diciendo cuál, primero la nota de crédito [{r.status_code}]",
      f32 and r.status_code == 409 and "REMITO_FACTURADO" in r.text and f32[0][0] in r.text and q("select estado from remitos where id=?", r32)[0][0] != "ANULADO")
r30 = q("select id from remitos where numero_legal='0015-00003030'")[0][0]   # sin factura vinculada: se prueba lo facturado por renglón
q("update remitos_items set cantidad_facturada = cantidad_remitida where id = (select min(id) from remitos_items where remito_id=?)", r30)
r = cli.post(f"/remitos/{guid(r30)}/anular", json={"motivo": "x"})
check(f"anular el 3030 (sin factura vinculada, con un renglón facturado): 409 REMITO_FACTURADO [{r.status_code}]",
      r.status_code == 409 and "REMITO_FACTURADO" in r.text and q("select estado from remitos where id=?", r30)[0][0] != "ANULADO")

# ---- (4) no se borra ni se edita con número
r = cli.delete(f"/remitos/{sust}")
check(f"el tacho no borra un remito con número: 409 REMITO_CON_NUMERO [{r.status_code}]", r.status_code == 409 and "REMITO_CON_NUMERO" in r.text)
r = cli.patch(f"/remitos/{sust}", json={"bultos": 5})
check(f"no se edita un remito con número: 400 REMITO_EMITIDO [{r.status_code}]", r.status_code == 400 and "REMITO_EMITIDO" in r.text)
r = cli.patch(f"/remitos/{sust}", json={"estado": "BORRADOR", "numero_legal": "0015-00000001"})
check(f"tampoco por la puerta de `estado` (antes dejaba cambiar hasta el número) [{r.status_code}]",
      r.status_code == 400 and q("select numero_legal from remitos where id=?", h(sust))[0][0] == num_sust)
r = cli.delete(f"/remitos/{sin_num}")
check(f"un remito SIN número sí se descarta con el tacho [{r.status_code}]", r.status_code == 200 and not q("select 1 from remitos where id=?", h(sin_num)))

# ---- (5) pantallas (estática)
lista = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "RemitoListView.vue"), encoding="utf-8").read()
split = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "LogisticaSplitter.vue"), encoding="utf-8").read()
check("listado: vista previa solo sin número, «Reimprimir» si está IMPRESO (bit 44 leído con aritmética), Anular / Deshacer con motivo",
      'data-accion="vista-previa"' in lista and "pdf?vista_previa=1" in lista and "tieneBit(remito.flags_estado, 44)" in lista and "Math.pow(2, n)" in lista
      and 'data-accion="anular"' in lista and 'data-accion="deshacer-anulacion"' in lista and "api.post(`/remitos/${anulacion.remito.id}/${ruta}`" in lista)
check("listado: un remito con número no abre la edición y el tacho es solo para los que no tienen número",
      "ya tiene número: no se edita" in lista and 'v-if="!editingRemito?.numero_legal" @click="deleteRemito(editingRemito)"' in lista)
check("pantalla de entregas: el botón dice «Reimprimir» si ya se imprimió, y hay vista previa sin número",
      "impresoRemito(remito) ? 'Reimprimir' : 'Imprimir PDF'" in split and "vistaPreviaRemito(remito)" in split)

# ---- limpieza
del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos[SALIDA]) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
