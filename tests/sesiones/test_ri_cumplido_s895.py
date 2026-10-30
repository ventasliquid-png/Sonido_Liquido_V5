r"""S895, Carlos 29/10 («parar la pelota antes del RI»): un Rosa no necesita un remito interno como documento (sin pago no hay entrega; el respaldo, si hace falta,
es un 0015 no facturable), pero sí un registro de que salió. Al poner «Cumplido» a un pedido ROSA, el sistema genera en silencio un RI numerado (serie RI01-00000001...) por
lo que faltaba remitir, con rastro (nota [SISTEMA] con el usuario); un Blanco sigue con el cartel de cierre con discrepancia; si el Rosa sale de Cumplido o se anula, el
RI que generó el Cumplido se anula. Papel del RI con su leyenda. Sobre una COPIA de la base de P del 28/10 16:51 (pedido #141 de Ana Robles, Rosa, sin remitos;
#148 de Jofre, Blanco, sin remitos)."""
import sys, os, re, sqlite3
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from backend.remitos.constants import RemitoFlags
from backend.remitos.pdf_parser import extract_text_from_pdf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
_aparte = imagenes_aparte(r"C:\dev\Sonido_Liquido_V5"); _aparte.__enter__()   # el PDF del RI deja su imagen: no en la carpeta real de D
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1651.db"
T = os.path.join(RAIZ, "scratch", "test_ri_cumplido_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "ana_prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
app.dependency_overrides[get_current_user_optional] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
B20, B21 = 1 << 20, 1 << 21
def bits(pid): return int(q("select flags_estado from pedidos where id=?", pid)[0][0])
def ris(pid): return q("select id, numero_legal, estado, flags_estado, fecha_salida, metodo_entrega from remitos where pedido_id=? and numero_legal like 'RI%' order by numero_legal", pid)

check("partida: #141 (Ana Robles) es Rosa, PENDIENTE y sin remitos; #148 (Jofre) es Blanco, PENDIENTE y sin remitos",
      q("select estado, (flags_estado>>12)&1 from pedidos where id=141")[0] == ("PENDIENTE", 1) and q("select estado, (flags_estado>>12)&1 from pedidos where id=148")[0] == ("PENDIENTE", 0)
      and not q("select 1 from remitos where pedido_id in (141, 148) and estado!='ANULADO'"))
check("partida: ningún RI en la base", q("select count(*) from remitos where numero_legal like 'RI%'")[0][0] == 0)

# ---------- Rosa: Cumplido genera el RI en silencio ----------
r = c.patch("/pedidos/141", json={"estado": "CUMPLIDO"})
check(f"Rosa #141: PATCH estado CUMPLIDO da 200, sin el cartel de cierre con discrepancia [{r.status_code}] {r.text[:120] if r.status_code != 200 else ''}", r.status_code == 200)
fila = ris(141)
check(f"se creó UN remito RI01-00000001, ENTREGADO, con fecha de salida {[(a[1], a[2]) for a in fila]}", len(fila) == 1 and fila[0][1] == "RI01-00000001" and fila[0][2] == "ENTREGADO" and fila[0][4])
f = int(fila[0][3]) if fila else 0
check("clase INTERNO (bit 32), EMITIDO (33), RECIBIDO (39), con el color congelado (CIRCUITO_ROSA) y sin ser CIRCULACION_ROSA (no es un 0015)",
      f & int(RemitoFlags.INTERNO) and f & int(RemitoFlags.EMITIDO) and f & int(RemitoFlags.RECIBIDO) and f & int(RemitoFlags.CIRCUITO_ROSA) and not f & int(RemitoFlags.EGRESO) and not f & int(RemitoFlags.CIRCULACION_ROSA))
its = q("select pi.cantidad, ri.cantidad_declarada, ri.cantidad_remitida, ri.cantidad_facturada from remitos_items ri join pedidos_items pi on pi.id=ri.pedido_item_id where ri.remito_id=?", fila[0][0])
check(f"el RI lleva TODO lo que faltaba (2 renglones de 1), sin facturar (no aplica, NULL) {its}", len(its) == 2 and all(i[0] == i[2] == i[1] for i in its) and all(i[3] is None for i in its))
check("el pedido quedó CUMPLIDO, con la entrega completa (bit 21), sin entrega parcial (bit 20) y SIN la marca de cierre con ajuste (bit 46)",
      q("select estado from pedidos where id=141")[0][0] == "CUMPLIDO" and bits(141) & B21 and not bits(141) & B20 and not bits(141) & (1 << 46))
nota_r = q("select texto from remitos_notas where remito_id=?", fila[0][0])
nota_p = q("select nota from pedidos where id=141")[0][0] or ""
check(f"rastro: nota [SISTEMA] en el remito y en el pedido, con el usuario {[n[0][:90] for n in nota_r]}",
      any(n[0].startswith("[SISTEMA] RI generado al marcar Cumplido el pedido #141: RI01-00000001") and "ana_prueba" in n[0] for n in nota_r)
      and "[SISTEMA] RI generado al marcar Cumplido el pedido #141" in nota_p)

# ---------- el RI sale en el informe y su papel lleva la leyenda ----------
rp = c.get(f"/remitos/{fila[0][0]}/pdf")
texto = extract_text_from_pdf(rp.content)[0] if rp.status_code == 200 else ""
check(f"el papel del RI (si se imprime) lleva el número RI01-00000001 y la leyenda «REMITO INTERNO - NO VÁLIDO COMO FACTURA» [{rp.status_code}]",
      rp.status_code == 200 and "RI01-00000001" in texto and "REMITO INTERNO" in texto and "COMO FACTURA" in texto)
from backend.informes.router import _num_remito
check("el informe de remitos ordena el RI por su número (no lo manda al fondo como «mal formado»)", _num_remito("RI01-00000003") == (3, 0) and _num_remito("0015-00003034") == (3034, 15) and _num_remito("") == (-1, -1))

# ---------- el talonario RI01 (Carlos 29/10: «RI01, con 99 talonarios hay espacio de sobra»; el circuito no formal) ----------
from backend.remitos.constants import es_numero_ri, TALONARIO_RI
from backend.remitos.genoma import calcular_flags
check("talonario RI01 + 8 dígitos (como «0015-00003034»), con el número en la misma forma que el fiscal; el viejo «RI-» y otros talonarios RI02..RI99 se entienden; un 0015 o un 0016 no",
      TALONARIO_RI == "RI01" and fila[0][1] == "RI01-00000001" and all(es_numero_ri(n) for n in ("RI01-00000001", "RI02-00000007", "RI99-00000001", "RI-00000001"))
      and not any(es_numero_ri(n) for n in ("0015-00003034", "0016-00002551", "RIO1-00000001", "", None)))
check("el genoma lee la clase INTERNO de cualquier talonario RI, sin CIRCULACION_ROSA (no es un 0015), y un 0015 de un Rosa sigue siendo EGRESO + CIRCULACION_ROSA",
      all(calcular_flags(0, n, "ENTREGADO", 1 << 12) & int(RemitoFlags.INTERNO) and not calcular_flags(0, n, "ENTREGADO", 1 << 12) & int(RemitoFlags.CIRCULACION_ROSA) for n in ("RI01-00000001", "RI02-00000001", "RI-00000001"))
      and calcular_flags(0, "0015-00003034", "BORRADOR", 1 << 12) & int(RemitoFlags.CIRCULACION_ROSA))

# ---------- reabrir: el RI se anula; volver a Cumplido genera otro con el siguiente número ----------
r = c.patch("/pedidos/141", json={"estado": "PENDIENTE"})
fila = ris(141)
check(f"reabrir el pedido (Cumplido → Pendiente): el RI queda ANULADO con nota y la entrega vuelve a estar pendiente [{r.status_code}] {[(a[1], a[2]) for a in fila]}",
      r.status_code == 200 and fila[0][2] == "ANULADO" and not bits(141) & B21
      and any("[SISTEMA] Remito anulado (estado anterior: ENTREGADO). Motivo: el pedido salió de Cumplido" in n[0] for n in q("select texto from remitos_notas where remito_id=?", fila[0][0])))
r = c.patch("/pedidos/141", json={"estado": "CUMPLIDO"})
fila = ris(141)
check(f"volver a Cumplido genera un RI nuevo con el número siguiente (el quemado no se reusa) {[(a[1], a[2]) for a in fila]}", r.status_code == 200 and [(a[1], a[2]) for a in fila] == [("RI01-00000001", "ANULADO"), ("RI01-00000002", "ENTREGADO")])
r = c.patch("/pedidos/141", json={"estado": "CUMPLIDO"})
check("Cumplido otra vez sin cambio de estado no genera otro RI", len(ris(141)) == 2)

# ---------- anular el pedido anula su RI ----------
r = c.patch("/pedidos/141", json={"estado": "ANULADO"})
check(f"anular el pedido anula el RI generado por el Cumplido [{r.status_code}]", r.status_code == 200 and all(a[2] == "ANULADO" for a in ris(141)))

# ---------- Rosa con una entrega parcial previa: el RI cubre solo el resto ----------
pi_ids = [a[0] for a in q("select id from pedidos_items where pedido_id=141 order by id")]
x("update pedidos set estado='PENDIENTE', flags_estado=(flags_estado & ~(15 << 32)) | (1 << 33) where id=141")
for rid, in q("select id from remitos where pedido_id=141 and numero_legal like 'RI%'"): x("update remitos set estado='ANULADO' where id=?", rid)
dom = q("select domicilio_entrega_id from pedidos where id=141")[0][0]
rj = c.post("/remitos/armar", json={"pedido_id": 141, "metodo_entrega": "TRANSPORTE_PROPIO", "domicilio_entrega_id": dom, "items": [{"pedido_item_id": pi_ids[0], "cantidad": 1}]})
check(f"un parcial armado antes (1 de 2 renglones) [{rj.status_code}] {rj.text[:100] if rj.status_code != 200 else ''}", rj.status_code == 200 and bits(141) & B20)
r = c.patch("/pedidos/141", json={"estado": "CUMPLIDO"})
nuevo = [a for a in ris(141) if a[2] != "ANULADO"]
its = q("select ri.pedido_item_id, ri.cantidad_remitida from remitos_items ri where ri.remito_id=?", nuevo[0][0]) if nuevo else []
check(f"el RI cubre SOLO el renglón que faltaba (el otro ya estaba remitido) [{r.status_code}] {its}", r.status_code == 200 and len(nuevo) == 1 and its == [(pi_ids[1], 1.0)] and bits(141) & B21)
r = c.patch("/pedidos/141", json={"estado": "PENDIENTE"})
check("reabrir anula solo el RI del Cumplido; el remito armado antes sigue vigente",
      r.status_code == 200 and q("select estado from remitos where id=?", nuevo[0][0])[0][0] == "ANULADO" and q("select estado from remitos where id=?", rj.json()["id"].replace("-", ""))[0][0] != "ANULADO")

# ---------- Rosa con TODO ya remitido: no se crea otro RI ----------
x("update pedidos set estado='PENDIENTE' where id=141")
r2 = c.post("/remitos/armar", json={"pedido_id": 141, "metodo_entrega": "TRANSPORTE_PROPIO", "domicilio_entrega_id": dom, "items": [{"pedido_item_id": pi_ids[1], "cantidad": 1}]})
n0 = q("select count(*) from remitos where numero_legal like 'RI%'")[0][0]
r = c.patch("/pedidos/141", json={"estado": "CUMPLIDO"})
check(f"con todo ya remitido por otros remitos, Cumplido no genera otro RI y no hay cartel [{r.status_code}]", r.status_code == 200 and q("select count(*) from remitos where numero_legal like 'RI%'")[0][0] == n0)

# ---------- Blanco: sigue el cartel y no se numera nada en silencio ----------
n0 = q("select count(*) from remitos where numero_legal like 'RI%' or (numero_legal is not null and pedido_id=148)")[0][0]
r = c.patch("/pedidos/148", json={"estado": "CUMPLIDO"})
check(f"Blanco #148 sin remito: Cumplido sigue dando 409 CIERRE_CON_DISCREPANCIA y no genera ningún número [{r.status_code}]",
      r.status_code == 409 and "CIERRE_CON_DISCREPANCIA" in r.text and q("select count(*) from remitos where numero_legal like 'RI%' or (numero_legal is not null and pedido_id=148)")[0][0] == n0
      and q("select estado from pedidos where id=148")[0][0] == "PENDIENTE")
r = c.patch("/pedidos/148", json={"estado": "CUMPLIDO", "cierre_confirmado": True})
check(f"confirmando el cierre (el camino de siempre) cierra con la marca de ajuste y sin remito [{r.status_code}]",
      r.status_code == 200 and bits(148) & (1 << 46) and not q("select 1 from remitos where pedido_id=148"))

# ---------- un Rosa no comercial no genera RI ----------
x("update pedidos set flags_estado = flags_estado | (1 << 11) | (1 << 12), estado='PENDIENTE' where id=147")
n0 = q("select count(*) from remitos where numero_legal like 'RI%'")[0][0]
r = c.patch("/pedidos/147", json={"estado": "CUMPLIDO", "cierre_confirmado": True})
check(f"un pedido no comercial no genera RI [{r.status_code}]", q("select count(*) from remitos where numero_legal like 'RI%'")[0][0] == n0)

# ---------- la OC por el guardado común ahora lleva autor (Card #195) ----------
r = c.patch("/pedidos/128", json={"oc": "OC-S895-1"})
n = q("select autor_id, texto from remitos_notas where texto like '%desde el pedido #128%' and texto like '%OC-S895-1%'")
check(f"la nota de OC por el guardado común del pedido #128 (con su remito 0015-00003027) lleva autor (antes salía sin autor) [{r.status_code}] {[x[0] for x in n]}", r.status_code == 200 and len(n) == 1 and n[0][0] == 1)

del c; eng.dispose()
_aparte.__exit__(None, None, None)
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
