r"""S894, Carlos 27/10 («un pedido puede cambiar de estado, incluso uno cumplido... hay campos como la OC o las notas que sí deberían ser pasibles de edición»),
con el Sello de Oro de Nike del 27/10 (CONSULTA_NIKE_oc_pedido_cerrado_2026-10-27.md):
- PATCH /pedidos/{id}/oc-y-nota edita la OC y la nota en cualquier estado, cerrado incluido. No toca bits, ni el total, ni los renglones de las facturas
  (PATCH /pedidos/{id} sí vuelve a copiar los renglones a la factura borrador). Si la OC cambia con el pedido cerrado, deja una nota [SISTEMA].
- El papel del remito omite las líneas [SISTEMA] de la nota del pedido (son trazas internas; Card #181, «el mínimo posible»: filtrar con la función de
  backend/informes/notas.py sin mover dónde se guardan); la nota del pedido las conserva.
- La pantalla del pedido cerrado guarda solo la OC y las notas.
- La OC que cambia en el pedido pasa a sus remitos vigentes, por los dos caminos (/oc-y-nota y el guardado de siempre), con nota [SISTEMA] en
  cada remito: «OC agregada» si no tenía, «OC corregida: cambió X por Y» si salió con otra (Carlos 27/10: «lo importante no es la reimpresión
  sino la auditoría: qué entregué de qué OC»; «si cambia, el tratamiento es el mismo que si estaba en blanco»: un número viejo corregido a mano
  en lo del cliente no se arregla anulando el remito). Si el remito tenía la imagen de su papel, se archiva y el próximo papel sale con la OC.
  Una OC vacía o «S/N» no se pasa (no borra la del remito).
Sobre una COPIA de P con migrate_066, 067, 068 y 069 (las del despliegue)."""
import sys, os, shutil, sqlite3, glob, subprocess, io
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_oc_pedido_cerrado_s894"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
rc = [correr(n).returncode for n in ("migrate_066_remitos_genoma_fecha_emision.py", "migrate_067_remitos_calificadores_46_47.py",
                                     "migrate_068_remitos_oc.py", "migrate_069_remitos_items_correccion.py")]
check(f"setup: copia de P ({os.path.basename(ORIG)}) con migrate_066, 067, 068 y 069 {rc}", rc == [0, 0, 0, 0])
asegurar_esquema(T)

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
_aparte = imagenes_aparte(BASE); _aparte.__enter__()
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()

def foto(pid):
    """lo que la edición de OC y nota no debe tocar: bits, total, estado, renglones del pedido y de sus facturas"""
    return (q("select flags_estado, total, estado from pedidos where id=?", pid),
            q("select id, cantidad, precio_unitario, subtotal from pedidos_items where pedido_id=? order by id", pid),
            q("select fi.id, fi.cantidad, fi.subtotal_neto from facturas_items fi join facturas f on f.id=fi.factura_id where f.pedido_id=? order by fi.id", pid))

# ---- pedido CUMPLIDO: preferimos uno con factura, para ver que sus renglones no se tocan
cumplidos = q("""select p.id, (select count(*) from facturas f where f.pedido_id=p.id) from pedidos p where p.estado='CUMPLIDO' order by 2 desc, p.id desc""")
check(f"hay pedidos CUMPLIDOS en la copia ({len(cumplidos)}; el primero con {cumplidos[0][1] if cumplidos else 0} factura/s)", len(cumplidos) > 0)
pc = cumplidos[0][0]
oc0, nota0 = q("select coalesce(oc,''), coalesce(nota,'') from pedidos where id=?", pc)[0]
propia0 = q("select id, oc from remitos where pedido_id=? and estado<>'ANULADO' and coalesce(trim(oc),'')<>''", pc)   # salieron con su OC
antes = foto(pc)
r = cli.patch(f"/pedidos/{pc}/oc-y-nota", json={"oc": " OC-S894-77 ", "nota": nota0 + "\nLlamar a Compras antes de facturar"})
oc1, nota1 = q("select oc, nota from pedidos where id=?", pc)[0]
check(f"pedido CUMPLIDO #{pc}: la OC y la nota se guardan [{r.status_code}] (OC sin espacios: «{oc1}»)",
      r.status_code == 200 and oc1 == "OC-S894-77" and "Llamar a Compras antes de facturar" in nota1)
linea = [l for l in nota1.splitlines() if l.startswith("[SISTEMA] OC cambiada")]
check(f"y queda la nota [SISTEMA] con la OC anterior y la nueva: «{linea[0] if linea else ''}»",
      len(linea) == 1 and "pedido CUMPLIDO" in linea[0] and "«OC-S894-77»" in linea[0] and f"«{oc0.strip() or 'vacía'}»" in linea[0] and "tmp" in linea[0])
check("no se tocan los bits, el total, el estado, los renglones del pedido ni los de sus facturas (Nike: ningún bit)", foto(pc) == antes)
check("la respuesta trae el pedido con la OC y la nota nuevas (la pantalla las toma de ahí)", r.json().get("oc") == "OC-S894-77" and "[SISTEMA] OC cambiada" in (r.json().get("nota") or ""))
r = cli.patch(f"/pedidos/{pc}/oc-y-nota", json={"oc": "OC-S894-77"})
check(f"la misma OC otra vez no agrega otra nota [{r.status_code}]", r.status_code == 200 and q("select nota from pedidos where id=?", pc)[0][0].count("[SISTEMA] OC cambiada") == 1)
r = cli.patch(f"/pedidos/{pc}/oc-y-nota", json={"nota": "solo la nota"})
check(f"solo la nota: la OC no se toca [{r.status_code}]", r.status_code == 200 and q("select oc, nota from pedidos where id=?", pc)[0] == ("OC-S894-77", "solo la nota"))

# ---- ANULADO y abierto
an = q("select id from pedidos where estado='ANULADO' order by id desc limit 1")
if an:
    an = an[0][0]; antes = foto(an)
    r = cli.patch(f"/pedidos/{an}/oc-y-nota", json={"oc": "OC-ANULADO-1"})
    check(f"pedido ANULADO #{an}: también se cambia la OC, con su nota [{r.status_code}], sin tocar nada más",
          r.status_code == 200 and "pedido ANULADO" in (q("select nota from pedidos where id=?", an)[0][0] or "") and foto(an) == antes)
else:
    check("(la copia no tiene pedidos ANULADOS: se saltea)", True)
ab = q("select id from pedidos where estado='PENDIENTE' order by id desc limit 1")[0][0]
antes = foto(ab)
r = cli.patch(f"/pedidos/{ab}/oc-y-nota", json={"oc": "OC-ABIERTO-1"})
check(f"pedido abierto #{ab}: cambia la OC [{r.status_code}] sin nota [SISTEMA] (la nota es para el pedido cerrado) y sin tocar nada más",
      r.status_code == 200 and q("select oc from pedidos where id=?", ab)[0][0] == "OC-ABIERTO-1"
      and "[SISTEMA] OC cambiada" not in (q("select nota from pedidos where id=?", ab)[0][0] or "") and foto(ab) == antes)
r = cli.patch(f"/pedidos/{ab}/oc-y-nota", json={"oc": "X", "items": []})
check(f"un campo que no es OC ni nota es un 422 (no se ignora en silencio) [{r.status_code}]", r.status_code == 422)
r = cli.patch("/pedidos/999999/oc-y-nota", json={"oc": "X"})
check(f"pedido inexistente: 404 [{r.status_code}]", r.status_code == 404)

# ---- el papel del remito omite las líneas [SISTEMA]
import backend.remitos.remito_engine as _engine
_real = _engine.generar_remito_pdf
visto = {}
def _espia(cliente_data, *a, **k):
    visto["obs"] = cliente_data.get("observaciones"); return _real(cliente_data, *a, **k)
_engine.generar_remito_pdf = _espia
pend = q("""select p.id, pi.id from pedidos p join pedidos_items pi on pi.pedido_id=p.id where p.estado='PENDIENTE' and (p.flags_estado>>12)&1=0
            and pi.cantidad > coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
            where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) order by p.id desc limit 1""")[0]
NOTA = "Entregar por la tarde\n[SISTEMA] Guardado sin OC: el cliente exige orden de compra (bit 6). 27/10/2026 10:00\n  [SISTEMA] Flete a cargo NUESTRO (bit 48).\nTocar timbre"
q("update pedidos set nota=? where id=?", NOTA, pend[0])
rr = cli.post("/remitos/armar", json={"pedido_id": pend[0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": pend[1], "cantidad": 1}]})
rid = rr.json().get("id") if rr.status_code == 200 else None
r = cli.get(f"/remitos/{rid}/pdf?vista_previa=1")
check(f"la vista previa del remito del pedido #{pend[0]} sale [{rr.status_code}, {r.status_code}] y sus observaciones no traen las líneas [SISTEMA]: {visto.get('obs')!r}",
      r.status_code == 200 and visto.get("obs") == "Entregar por la tarde\nTocar timbre")
visto.clear(); r = cli.get(f"/remitos/{rid}/pdf")
check(f"el papel de verdad (toma número) tampoco [{r.status_code}]", r.status_code == 200 and visto.get("obs") == "Entregar por la tarde\nTocar timbre")
check("la nota del pedido conserva las líneas [SISTEMA] enteras, y el papel las separa con la función de Informes (Card #181)",
      q("select nota from pedidos where id=?", pend[0])[0][0] == NOTA
      and 'fragmentos_clasificados(remito.pedido.nota) if f["categoria"] == CATEGORIA_HUMANA[0]' in io.open("backend/remitos/router.py", encoding="utf-8").read())
q("update pedidos set nota=? where id=?", "[SISTEMA] Pedido creado con advertencia duplicado nivel MEDIO.", pend[0])
rr = cli.post("/remitos/armar", json={"pedido_id": pend[0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": pend[1], "cantidad": 1}]})
visto.clear(); r = cli.get(f"/remitos/{rr.json().get('id')}/pdf?vista_previa=1") if rr.status_code == 200 else None
check(f"una nota que es solo [SISTEMA] deja las observaciones vacías [{rr.status_code}, {getattr(r, 'status_code', None)}]", r is not None and r.status_code == 200 and visto.get("obs") == "")

# ---- la OC tardía llega a los remitos (Carlos 27/10: «lo importante no es la reimpresión sino la auditoría: qué entregué de qué OC»)
_espia_viejo = _espia
def _espia(cliente_data, *a, **k):
    visto["oc"] = cliente_data.get("oc"); return _espia_viejo(cliente_data, *a, **k)
_engine.generar_remito_pdf = _espia
IMAGENES = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
ns = lambda rid: [t for (t,) in q("select texto from remitos_notas where remito_id=? order by id", rid.replace("-", ""))]
cand = q("""select p.id, r.id, r.numero_legal from pedidos p join remitos r on r.pedido_id=p.id where p.estado='CUMPLIDO' and coalesce(trim(p.oc),'')=''
            and coalesce(trim(r.oc),'')='' and r.numero_legal like '0015-%' and r.estado<>'ANULADO' order by p.id desc limit 1""")
check(f"hay un pedido CUMPLIDO sin OC con un 0015 sin OC en la copia ({cand[0] if cand else None})", bool(cand))
pz, rz, nz = cand[0]
import uuid; rz = str(uuid.UUID(str(rz))); imagen = os.path.join(IMAGENES, f"remito_{nz.replace('-', '_')}.pdf")
r = cli.get(f"/remitos/{rz}/pdf")
check(f"su papel queda guardado como imagen ({nz}) [{r.status_code}] y sale sin OC", r.status_code == 200 and os.path.exists(imagen) and not visto.get("oc"))
r = cli.patch(f"/pedidos/{pz}/oc-y-nota", json={"oc": "OC-AUDIT-1"})
nota_r = [t for t in ns(rz) if "[SISTEMA] OC agregada desde el pedido" in t]
check(f"cargar la OC en el pedido cerrado #{pz} [{r.status_code}] la pasa al remito sin OC, con una nota [SISTEMA]: «{nota_r[0] if nota_r else ''}»",
      r.status_code == 200 and q("select oc from remitos where id=?", rz.replace("-", ""))[0][0] == "OC-AUDIT-1" and len(nota_r) == 1 and f"#{pz}: «OC-AUDIT-1»" in nota_r[0])
archivadas = [n for n in os.listdir(os.path.join(IMAGENES, "Reemplazadas"))] if os.path.isdir(os.path.join(IMAGENES, "Reemplazadas")) else []
check(f"y la imagen del papel sin OC se archiva, no se borra ({archivadas})", not os.path.exists(imagen) and any(n.startswith(f"remito_{nz.replace('-', '_')}__hasta_") for n in archivadas)
      and "Reemplazadas/" in nota_r[0])
visto.clear(); r = cli.get(f"/remitos/{rz}/pdf")
check(f"el próximo papel sale con la OC [{r.status_code}, OC {visto.get('oc')!r}] y pasa a ser la imagen", r.status_code == 200 and visto.get("oc") == "OC-AUDIT-1" and os.path.exists(imagen))
r = cli.patch(f"/pedidos/{pz}/oc-y-nota", json={"oc": "OC-AUDIT-2"})
corr = [t for t in ns(rz) if "[SISTEMA] OC corregida desde el pedido" in t]
viejas = [n for n in os.listdir(os.path.join(IMAGENES, "Reemplazadas")) if n.startswith(f"remito_{nz.replace('-', '_')}__hasta_")]
check(f"si después la OC del pedido se corrige, el remito también (salió con otra: se trata igual que en blanco) [{r.status_code}]: «{corr[0] if corr else ''}»",
      r.status_code == 200 and q("select oc from remitos where id=?", rz.replace("-", ""))[0][0] == "OC-AUDIT-2" and len(corr) == 1
      and "cambió «OC-AUDIT-1» por «OC-AUDIT-2»" in corr[0] and len(viejas) == 2 and not os.path.exists(imagen))
r = cli.patch(f"/pedidos/{pz}/oc-y-nota", json={"oc": ""})
check(f"vaciar la OC del pedido no borra la del remito [{r.status_code}]", r.status_code == 200 and q("select oc from remitos where id=?", rz.replace("-", ""))[0][0] == "OC-AUDIT-2")
check(f"los remitos del pedido #{pc} que salieron con la OC vieja ({[o for _, o in propia0]}) quedan con la corregida y su nota «cambió X por Y»",
      len(propia0) > 0 and all(q("select oc from remitos where id=?", i)[0][0] == "OC-S894-77" for i, _ in propia0)
      and all(sum(f"cambió «{o}» por «OC-S894-77»" in t for t in ns(str(i))) == 1 for i, o in propia0))
# pedido abierto, por el guardado de siempre (PATCH /pedidos/{id})
ab2 = pend[0]
q("update pedidos set oc='' where id=?", ab2); q("update remitos set oc=NULL where pedido_id=?", ab2)
r = cli.patch(f"/pedidos/{ab2}/oc-y-nota", json={"oc": "S/N"})
check(f"«S/N» no es una OC: no pasa a los remitos [{r.status_code}]", r.status_code == 200 and q("select count(*) from remitos where pedido_id=? and oc is not null", ab2)[0][0] == 0)
r = cli.patch(f"/pedidos/{ab2}", json={"oc": "OC-ABIERTO-2"})
n_rem = q("select count(*) from remitos where pedido_id=? and estado<>'ANULADO'", ab2)[0][0]
check(f"pedido abierto #{ab2}: guardar el pedido con la OC nueva [{r.status_code}] la pasa a sus {n_rem} remitos sin OC",
      r.status_code == 200 and n_rem > 0 and q("select count(*) from remitos where pedido_id=? and estado<>'ANULADO' and oc='OC-ABIERTO-2'", ab2)[0][0] == n_rem)
_engine.generar_remito_pdf = _real

# ---- la pantalla (estático)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
canvas = leer("frontend/src/views/Ventas/PedidoCanvas.vue")
check("la pantalla del pedido cerrado guarda por /oc-y-nota la OC y las notas", "api.patch(`/pedidos/${route.params.id}/oc-y-nota`, { oc: nroOC.value.trim(), nota: notas.value || '' })" in canvas)
check("«Guardar» ya no se deshabilita por estar cerrado y dice «Guardar OC y notas»; «Guardar e Imprimir» sigue trabado",
      ':disabled="isSaving || items.length === 0 || !clienteSeleccionado"\n' in canvas and "'Guardar OC y notas'" in canvas
      and canvas.count("|| !clienteSeleccionado || isClosedOrder\"") == 1)
check("el aviso del pedido cerrado dice qué se puede cambiar", "solo se pueden cambiar la OC y las notas" in canvas and "y no puede editarse" not in canvas)

del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
