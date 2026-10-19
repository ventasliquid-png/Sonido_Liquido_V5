r"""S883, paso 1 de «un domicilio, muchos clientes»: GET /clientes/hub/similares encuentra el mismo lugar escrito distinto, con quien lo usa y si se puede usar tal cual; y /fork de un domicilio de un solo
cliente edita en el lugar (sin duplicado ni huerfano). Sobre una COPIA de la base de P de las 15:51."""
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261009_1551.db"
T = os.path.join(RAIZ, "scratch", "test_similares_tmp.db"); copiar_p(ORIG, T)
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
def uu(x): return f"{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}"
def h(x): return x.replace("-", "")
def sim(**p):
    r = cli.get("/clientes/hub/similares", params=p); return r.status_code, (r.json() if r.status_code == 200 else r.text)
CP = "069bd7c5be294d88a1df92c856239a7f"
GELATO = q("select id from clientes where razon_social='GELATO SA'")[0][0]
snap = (q("select count(*) from domicilios")[0][0], q("select count(*) from domicilios_clientes")[0][0])

# ---- 1) un domicilio repetido del mismo cliente (Centro Pet, Vieytes 1549)
st, js = sim(calle="Vieytes", numero="1549", localidad="CABA", excluir_cliente_id=uu(CP))
check(f"Vieytes 1549 de Centro Pet: encuentra las 2 filas IGUAL, ambas ya son de este cliente [{st}] {[(x['nivel'], x['ya_es_de_este_cliente']) for x in js][:3]}",
      st == 200 and len(js) == 2 and all(x["nivel"] == "IGUAL" and x["ya_es_de_este_cliente"] and x["compatible"] for x in js))
# ---- 2) escrito distinto (como lo escribiria ARCA), sobre una direccion real de P (Gelato y Lacteos: Vuelta de Obligado 1947)
st, js = sim(calle="Obligado, Vuelta de Av", numero="N°1947", localidad="Capital Federal")
check(f"«Obligado, Vuelta de Av N°1947, Capital Federal» encuentra «Vuelta de Obligado 1947 CABA» [{st}] {[(x['nivel'], [u['razon_social'] for u in x['usado_por']]) for x in js]}",
      st == 200 and len(js) >= 1 and js[0]["nivel"] == "IGUAL" and {u["razon_social"] for u in js[0]["usado_por"]} == {"GELATO SA", "Lácteos de Poblet SA"})
_, como_entrega = sim(calle="Vuelta de Obligado", numero="1947", localidad="CABA", es_fiscal="false")
_, como_fiscal = sim(calle="Vuelta de Obligado", numero="1947", localidad="CABA", es_fiscal="true")
check(f"la usan OTROS clientes: como entrega es compatible; como fiscal NO, con el motivo {str(como_fiscal[0]['motivo_incompatible'])[:80]}",
      como_entrega[0]["compatible"] is True and como_fiscal[0]["compatible"] is False and "GELATO SA" in como_fiscal[0]["motivo_incompatible"])
# ---- 3) repetido entre clientes (M&M), calle numerada
st, js = sim(calle="Av 72", numero="796", localidad="La Plata")
check(f"Av 72 N° 796 La Plata: encuentra las filas de M&M [{st}] {len(js)}", st == 200 and len(js) >= 1 and all(x["nivel"] == "IGUAL" for x in js))
# ---- 3b) cada provincia tiene dos codigos en la tabla («B» y «BA» son Buenos Aires): se comparan por nombre, no por codigo
n_ba, n_b, n_x = (len(sim(calle="Av 72", numero="796", localidad="La Plata", provincia_id=c)[1]) for c in ("BA", "B", "X"))
check(f"provincia «B» o «BA» (las dos son Buenos Aires) encuentran lo mismo ({n_ba} / {n_b}); «X» (Cordoba) no encuentra nada ({n_x})", n_ba >= 1 and n_ba == n_b and n_x == 0)
_, caba_c = sim(calle="Vuelta de Obligado", numero="1947", localidad="", provincia_id="C")
_, caba_n = sim(calle="Vuelta de Obligado", numero="1947", localidad="", provincia_id="CABA")
check(f"CABA con codigo «C» o «CABA» encuentra lo mismo ({len(caba_c)} / {len(caba_n)})", len(caba_c) >= 1 and len(caba_c) == len(caba_n))
# ---- 4) otra altura u otra calle: nada
check("la misma calle con otra altura (Vieytes 1594) no trae nada", sim(calle="Vieytes", numero="1594", localidad="CABA")[1] == [])
check("una direccion que no existe no trae nada", sim(calle="Calle Inventada", numero="9999", localidad="Mar del Plata")[1] == [])
# ---- 5) es solo lectura y valida los parametros
check("no cambia la base (solo lectura)", (q("select count(*) from domicilios")[0][0], q("select count(*) from domicilios_clientes")[0][0]) == snap)
check("sin calle: 422 (no se puede buscar nada)", cli.get("/clientes/hub/similares").status_code == 422)

# ---- 6) /fork de un domicilio de UN solo cliente: se edita en el lugar (la pantalla lo llama en cada guardado de un domicilio espejado)
prov = q("select id from provincias where upper(nombre) like 'BUENOS%' limit 1")[0][0]
r = cli.post(f"/clientes/{uu(CP)}/domicilios", json={"calle": "Fork de Prueba", "numero": "10", "localidad": "CABA", "provincia_id": prov, "es_entrega": True}); d1 = r.json()["id"]
n0 = q("select count(*) from domicilios")[0][0]
r = cli.post(f"/clientes/{uu(CP)}/domicilios/{d1}/fork", json={"calle": "Fork de Prueba", "numero": "10", "localidad": "CABA", "notas_logistica": "Llamar antes", "id": d1, "cliente_id": uu(CP)})
check(f"/fork de un domicilio de un solo cliente devuelve el MISMO domicilio, editado [{r.status_code}]", r.status_code == 200 and r.json().get("id") == d1 and q("select notas_logistica from domicilios where id=?", h(d1)) == [("Llamar antes",)])
check("y no deja duplicado ni huerfano (la cantidad de domicilios no cambia, el vinculo apunta al mismo, flags de espejo apagadas)",
      q("select count(*) from domicilios")[0][0] == n0 and q("select domicilio_id, flags from domicilios_clientes where cliente_id=? and domicilio_id=?", CP, h(d1)) == [(h(d1), 0)])
# ---- 7) /fork de un domicilio COMPARTIDO: copy-on-write de siempre
con = sqlite3.connect(T); con.execute("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 2097152, 0)", (GELATO, h(d1))); con.commit(); con.close()
r = cli.post(f"/clientes/{uu(CP)}/domicilios/{d1}/fork", json={"calle": "Fork de Prueba", "numero": "10", "localidad": "CABA", "notas_logistica": "Solo Centro Pet"})
nuevo = r.json().get("id") if r.status_code == 200 else None
check(f"/fork de un domicilio compartido clona: Centro Pet pasa a su copia y el otro cliente conserva el original [{r.status_code}]",
      bool(nuevo) and nuevo != d1 and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", GELATO, h(d1))[0][0] == 1
      and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", CP, h(nuevo))[0][0] == 1 and q("select notas_logistica from domicilios where id=?", h(d1)) == [("Llamar antes",)])
# ---- 8) «usar el domicilio que ya existia»: el vinculo queda SIN alias (no la etiqueta «VÍNCULO HUB»); el Hub de siempre (sin alias en la llamada) conserva su etiqueta
dom_obl = q("select id from domicilios where calle like 'Vuelta de Obligado%' and numero='1947' limit 1")[0][0]
otro_cli = [r[0] for r in q("select id from clientes where id not in (select cliente_id from domicilios_clientes where domicilio_id=?) limit 2", dom_obl)]
r1 = cli.post(f"/clientes/hub/{dom_obl}/links/{uu(otro_cli[0])}", params={"alias": "", "flags": 2097152})
r2 = cli.post(f"/clientes/hub/{dom_obl}/links/{uu(otro_cli[1])}", params={"flags": 2097152})
check(f"vinculo pedido sin alias queda sin alias, y el del Hub de siempre conserva «VÍNCULO HUB» [{r1.status_code}/{r2.status_code}]",
      r1.status_code == 200 and r2.status_code == 200
      and q("select alias from domicilios_clientes where domicilio_id=? and cliente_id=?", dom_obl, otro_cli[0]) == [("",)]
      and q("select alias from domicilios_clientes where domicilio_id=? and cliente_id=?", dom_obl, otro_cli[1]) == [("VÍNCULO HUB",)])
del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [x for x, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", x) for x in falla]
sys.exit(1 if falla else 0)
