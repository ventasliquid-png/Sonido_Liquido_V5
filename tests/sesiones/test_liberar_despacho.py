"""Compuerta financiera (S876, P16): POST /pedidos/{id}/liberar-despacho. Sobre una COPIA de la base migrada de P."""
import sys, os, shutil, sqlite3, gc
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_liberar_despacho_tmp.db"
copiar_p(r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_migrada_20260930.db", TMP)
eng = create_engine(f"sqlite:///{TMP}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "ana_prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(TMP); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(TMP); con.execute(sql, a); con.commit(); con.close()

# situación real de P: ningún pedido liberado
check("situación de partida: 0 pedidos liberados en la copia de P", q("select count(*) from pedidos where liberado_despacho=1")[0][0] == 0)

# un pedido PENDIENTE con renglones; le armo a mano 3 remitos: BORRADOR bloqueado, ENTREGADO bloqueado, ANULADO bloqueado
pid = q("select p.id from pedidos p where p.estado='PENDIENTE' and exists(select 1 from pedidos_items i where i.pedido_id=p.id) order by p.id limit 1")[0][0]
otro = q("select p.id from pedidos p where p.estado='PENDIENTE' and p.id<>? and exists(select 1 from pedidos_items i where i.pedido_id=p.id) order by p.id limit 1", pid)[0][0]
dom = q("select id from domicilios limit 1")[0][0]
def remito(n, estado, pedido=pid, aprob=0):
    import uuid; rid = uuid.uuid4().hex
    x("insert into remitos (id, pedido_id, domicilio_entrega_id, estado, aprobado_para_despacho, flags_estado) values (?,?,?,?,?,0)", rid, pedido, dom, estado, aprob)
    return rid
r_borr, r_ent, r_anul = remito(1, "BORRADOR"), remito(2, "ENTREGADO"), remito(3, "ANULADO")
r_ajeno = remito(4, "BORRADOR", pedido=otro)
r_ya_ok = remito(5, "BORRADOR", aprob=1)

# antes: despachar da 409 por la compuerta
r = c.post(f"/remitos/{r_borr}/despachar")
check(f"antes de liberar, despachar el PR bloqueado da 409 DESPACHO_NO_APROBADO [{r.status_code}]", r.status_code == 409 and "DESPACHO_NO_APROBADO" in r.json()["detail"])

nota0 = q("select coalesce(nota,'') from pedidos where id=?", pid)[0][0]
r = c.post(f"/pedidos/{pid}/liberar-despacho")
check(f"liberar-despacho: 200 [{r.status_code}] y la respuesta trae liberado_despacho=true", r.status_code == 200 and r.json().get("liberado_despacho") is True)
check("queda guardado en la base (liberado_despacho = 1)", q("select liberado_despacho from pedidos where id=?", pid)[0][0] == 1)
nota1 = q("select coalesce(nota,'') from pedidos where id=?", pid)[0][0]
check("la nota conserva lo que había y agrega la constancia con usuario y fecha", nota1.startswith(nota0) and "[SISTEMA] Despacho liberado por ana_prueba." in nota1 and nota1.count("[SISTEMA] Despacho liberado") == 1)
import re
check("la constancia lleva fecha y hora (AAAA-MM-DD HH:MM)", re.search(r"Despacho liberado por ana_prueba\. \d{4}-\d{2}-\d{2} \d{2}:\d{2}\.", nota1))
check("la constancia dice cuántos remitos en borrador aprobó (los bloqueados: 1)", "Remitos en borrador aprobados: 1." in nota1)
st = dict(q("select id, aprobado_para_despacho from remitos where id in (?,?,?,?,?)", r_borr, r_ent, r_anul, r_ajeno, r_ya_ok))
check("el PR en BORRADOR bloqueado del pedido quedó aprobado", st[r_borr] == 1)
check("el PR ya ENTREGADO no se toca (sigue 0)", st[r_ent] == 0)
check("el PR ANULADO no se toca (sigue 0)", st[r_anul] == 0)
check("el PR en borrador de OTRO pedido no se toca (sigue 0)", st[r_ajeno] == 0)
check("el PR que ya estaba aprobado sigue aprobado", st[r_ya_ok] == 1)
check("no se liberó ningún otro pedido (1 pedido liberado en toda la base)", q("select count(*) from pedidos where liberado_despacho=1")[0][0] == 1)

# después: la compuerta del remito ya no frena por DESPACHO_NO_APROBADO (puede frenar por REMITO_SIN_IMPRIMIR, que es la otra regla)
r = c.post(f"/remitos/{r_borr}/despachar")
check(f"después de liberar, despachar ya no da DESPACHO_NO_APROBADO [{r.status_code}: {str(r.json().get('detail'))[:40]}]", "DESPACHO_NO_APROBADO" not in str(r.json().get("detail")))

# idempotencia
r = c.post(f"/pedidos/{pid}/liberar-despacho")
nota2 = q("select coalesce(nota,'') from pedidos where id=?", pid)[0][0]
check(f"segunda vez: 200 [{r.status_code}] y NO agrega otra constancia", r.status_code == 200 and nota2 == nota1)

# pedido nuevo (sin remitos): libera sin el detalle de remitos
r = c.post(f"/pedidos/{otro}/liberar-despacho")
n_otro = q("select coalesce(nota,'') from pedidos where id=?", otro)[0][0]
check("el pedido 'otro' (con un PR bloqueado propio) libera y la constancia cuenta 1 remito", r.status_code == 200 and "Remitos en borrador aprobados: 1." in n_otro)
tercero = q("select p.id from pedidos p where p.estado='PENDIENTE' and p.id not in (?,?) and not exists(select 1 from remitos r where r.pedido_id=p.id) order by p.id limit 1", pid, otro)[0][0]
r = c.post(f"/pedidos/{tercero}/liberar-despacho")
n_t = q("select coalesce(nota,'') from pedidos where id=?", tercero)[0][0]
check("un pedido sin ningún PR: libera y la constancia no menciona remitos", r.status_code == 200 and "Despacho liberado por ana_prueba." in n_t and "Remitos en borrador" not in n_t)
check("el PR en borrador del pedido 'otro' ahora sí quedó aprobado (era suyo)", q("select aprobado_para_despacho from remitos where id=?", r_ajeno)[0][0] == 1)

# 404 y armado posterior
r = c.post("/pedidos/99999999/liberar-despacho")
check(f"pedido inexistente: 404 [{r.status_code}]", r.status_code == 404)
check("GET /pedidos/{id} informa liberado_despacho (lo que lee la pantalla de logística)", c.get(f"/pedidos/{pid}").json().get("liberado_despacho") is True)

del c; gc.collect(); eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
