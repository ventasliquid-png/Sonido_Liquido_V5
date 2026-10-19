r"""S883, Card #170: el domicilio de una empresa de transporte se guarda (Domicilio + VinculoGeografico 'TRANSPORTE') con POST/PUT/DELETE /logistica/empresas/{id}/domicilios.
Sobre una COPIA de la base de P de las 17:51."""
import sys, os, shutil, sqlite3
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1751.db"
T = os.path.join(RAIZ, "scratch", "test_transp_dom_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v

SM = "2b6e334d-8f73-470b-9f06-dc3847575401"          # TRANSPORTE SANTA MARTA
SM_HEX = SM.replace("-", "")
OTRA = q("select id from empresas_transporte where id != ? limit 1", SM_HEX)[0][0]
prov = q("select id from provincias where upper(nombre) like 'CHACO%' limit 1")[0][0]
n_dom0, n_vg0 = q("select count(*) from domicilios")[0][0], q("select count(*) from vinculos_geograficos")[0][0]
check("partida: Santa Marta no tiene ningun domicilio ni vinculo geografico", q("select count(*) from vinculos_geograficos where entidad_id=?", SM_HEX)[0][0] == 0)
snap_otros = (q("select id, nombre, telefono_reclamos from empresas_transporte order by id"), q("select count(*) from pedidos")[0][0], q("select count(*) from clientes")[0][0])

# ---- 1) alta de la direccion fiscal (lo que hizo Tomy)
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "Ruta 11", "numero": "Km 1007", "localidad": "Resistencia", "provincia_id": prov, "alias": "Casa central", "es_fiscal": True})
j = r.json() if r.status_code == 201 else {}
check(f"POST: el domicilio fiscal se crea [{r.status_code}] {r.text[:90] if r.status_code != 201 else ''}", r.status_code == 201 and j.get("domicilio", {}).get("calle") == "Ruta 11")
dom1 = j.get("domicilio_id", "")
v = q("select entidad_tipo, flags_relacion, activo, alias from vinculos_geograficos where entidad_id=?", SM_HEX)
d = q("select calle, numero, localidad, provincia_id, es_fiscal, activo from domicilios where id=?", dom1.replace("-", ""))
check(f"queda el vinculo TRANSPORTE con el bit FISCAL y el domicilio con su direccion {v} {d}", v == [("TRANSPORTE", 1, 1, "Casa central")] and d == [("Ruta 11", "Km 1007", "Resistencia", prov, 1, 1)])
e = cli.get(f"/logistica/empresas/{SM}").json()
check("GET de la empresa devuelve la direccion en vinculos_geograficos (es lo que dibuja la ficha)", [x["domicilio"]["calle"] for x in e["vinculos_geograficos"]] == ["Ruta 11"] and e["vinculos_geograficos"][0]["flags_relacion"] == 1)

# ---- 2) una sede de entrega (sin indicacion: bit PRINCIPAL_ENTREGA)
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "Deposito Norte 55", "localidad": "Corrientes"})
dom2 = r.json().get("domicilio_id", "") if r.status_code == 201 else ""
check(f"POST sin indicacion: sede de entrega (bit 2) [{r.status_code}] {q('select flags_relacion from vinculos_geograficos where domicilio_id=?', dom2.replace('-', ''))}", r.status_code == 201 and q("select flags_relacion from vinculos_geograficos where domicilio_id=?", dom2.replace("-", "")) == [(2,)])

# ---- 3) un solo fiscal: otra direccion fiscal le saca el bit a la anterior
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "Nueva fiscal 1", "localidad": "Resistencia", "es_fiscal": True})
dom3 = r.json().get("domicilio_id", "") if r.status_code == 201 else ""
fisc = q("select domicilio_id from vinculos_geograficos where entidad_id=? and flags_relacion & 1 = 1", SM_HEX)
check(f"un solo domicilio fiscal por empresa: queda solo el nuevo [{len(fisc)}]", len(fisc) == 1 and fisc[0][0] == dom3.replace("-", "") and q("select es_fiscal from domicilios where id=?", dom1.replace("-", "")) == [(0,)])

# ---- 4) edicion: cambia la calle; el resto queda igual (un solo domicilio, no se duplica)
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom3}", json={"calle": "Ruta 11 Km 1007,5", "numero": "S/N"})
check(f"PUT cambia la calle y no duplica [{r.status_code}] {q('select calle, numero, es_fiscal from domicilios where id=?', dom3.replace('-', ''))}",
      r.status_code == 200 and q("select calle, numero, es_fiscal from domicilios where id=?", dom3.replace("-", "")) == [("Ruta 11 Km 1007,5", "S/N", 1)] and q("select count(*) from domicilios")[0][0] == n_dom0 + 3)
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom2}", json={"es_fiscal": True})
check(f"PUT es_fiscal=true sobre otra sede: pasa a ser la fiscal y la anterior la pierde [{r.status_code}]", r.status_code == 200 and q("select domicilio_id from vinculos_geograficos where entidad_id=? and flags_relacion & 1 = 1", SM_HEX) == [(dom2.replace("-", ""),)])

# ---- 4b) espejo (Bit 21): se guarda, se apaga y no se pisa al editar otra cosa
ESP = 1 << 21
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "Espejada 100", "localidad": "CABA", "es_entrega": True, "espejo": True})
dom4 = r.json().get("domicilio_id", "") if r.status_code == 201 else ""
fl = lambda d: q("select flags_relacion from vinculos_geograficos where domicilio_id=?", d.replace("-", ""))[0][0]
check(f"POST con espejo=true guarda el Bit 21 junto con el bit de entrega [{r.status_code}] flags={fl(dom4) if dom4 else None}", r.status_code == 201 and fl(dom4) == (2 | ESP))
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom4}", json={"calle": "Espejada 101"})
check(f"PUT que no menciona el espejo no lo toca [{r.status_code}] flags={fl(dom4)}", r.status_code == 200 and fl(dom4) == (2 | ESP))
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom4}", json={"espejo": False})
check(f"PUT espejo=false lo apaga y deja los otros bits [{r.status_code}] flags={fl(dom4)}", r.status_code == 200 and fl(dom4) == 2)
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom4}", json={"espejo": True})
e = cli.get(f"/logistica/empresas/{SM}").json()
check("GET de la empresa devuelve el Bit 21 en flags_relacion (la ficha lo usa para mostrar el espejo)", any(v["domicilio_id"].replace("-", "") == dom4.replace("-", "") and v["flags_relacion"] == (2 | ESP) for v in e["vinculos_geograficos"]))

# ---- 5) baja logica y recuperacion
r = cli.delete(f"/logistica/empresas/{SM}/domicilios/{dom1}")
check(f"DELETE es baja LOGICA: el domicilio y el vinculo siguen, inactivos [{r.status_code}] {q('select activo from vinculos_geograficos where domicilio_id=?', dom1.replace('-', ''))}",
      r.status_code == 200 and q("select activo from vinculos_geograficos where domicilio_id=?", dom1.replace("-", "")) == [(0,)] and q("select activo, is_active from domicilios where id=?", dom1.replace("-", "")) == [(0, 0)])
r = cli.put(f"/logistica/empresas/{SM}/domicilios/{dom1}", json={"activo": True})
check(f"se recupera con PUT activo=true [{r.status_code}]", r.status_code == 200 and q("select activo from vinculos_geograficos where domicilio_id=?", dom1.replace("-", "")) == [(1,)])

# ---- 6) guardas
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "   ", "localidad": "X"}); check(f"sin calle: 400 CALLE_REQUERIDA [{r.status_code}]", r.status_code == 400 and "CALLE_REQUERIDA" in r.text)
r = cli.post(f"/logistica/empresas/{SM}/domicilios", json={"calle": "X 1", "provincia_id": "ZZZZ"}); check(f"provincia inexistente: 400 [{r.status_code}]", r.status_code == 400 and "PROVINCIA_INEXISTENTE" in r.text)
r = cli.post("/logistica/empresas/00000000-0000-0000-0000-000000000000/domicilios", json={"calle": "X 1"}); check(f"empresa inexistente: 404 [{r.status_code}]", r.status_code == 404)
otra_uuid = f"{OTRA[:8]}-{OTRA[8:12]}-{OTRA[12:16]}-{OTRA[16:20]}-{OTRA[20:]}"
r = cli.put(f"/logistica/empresas/{otra_uuid}/domicilios/{dom1}", json={"calle": "Pisada"}); check(f"el domicilio de Santa Marta no se puede tocar desde otra empresa: 404 [{r.status_code}] y no cambia", r.status_code == 404 and q("select calle from domicilios where id=?", dom1.replace("-", "")) == [("Ruta 11",)])
r = cli.delete(f"/logistica/empresas/{SM}/domicilios/11111111-1111-1111-1111-111111111111"); check(f"domicilio inexistente: 404 [{r.status_code}]", r.status_code == 404)

# ---- 7) nada mas cambia; el telefono y los datos de la empresa siguen igual; las guardas no dejaron filas de mas
check("las otras empresas, los pedidos y los clientes no cambian", (q("select id, nombre, telefono_reclamos from empresas_transporte order by id"), q("select count(*) from pedidos")[0][0], q("select count(*) from clientes")[0][0]) == snap_otros)
check(f"solo se crearon los 4 domicilios y 4 vinculos de las pruebas (las guardas no dejaron basura) [{q('select count(*) from domicilios')[0][0] - n_dom0}, {q('select count(*) from vinculos_geograficos')[0][0] - n_vg0}]", q("select count(*) from domicilios")[0][0] == n_dom0 + 4 and q("select count(*) from vinculos_geograficos")[0][0] == n_vg0 + 4)
# la ficha manda el PUT de la empresa con el telefono: sigue funcionando
r = cli.put(f"/logistica/empresas/{SM}", json={"nombre": "TRANSPORTE SANTA MARTA", "telefono_reclamos": "0810-555-0000"})
check(f"el PUT de la empresa (telefono) sigue funcionando y no toca los domicilios [{r.status_code}]", r.status_code == 200 and q("select telefono_reclamos from empresas_transporte where id=?", SM_HEX) == [("0810-555-0000",)] and q("select count(*) from vinculos_geograficos where entidad_id=?", SM_HEX)[0][0] == 4)
del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
