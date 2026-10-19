r"""S885, Cards #172 y #173: GUARDIA DE ROLES de los domicilios compartidos + regla «un cliente Blanco y Responsable Inscripto no puede quedar sin domicilio fiscal».
Caso de Carlos (09/10): Gelato y Lacteos tienen el MISMO fiscal (Ruta Provincial 36 y 630) y comparten Vuelta de Obligado 1947 como entrega; si Lacteos pasa su fiscal a Obligado, Gelato no se entera.
Sobre COPIAS de la base de P de las 15:51 (una por grupo de escenarios)."""
import sys, os, shutil, sqlite3
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
T = os.path.join(RAIZ, "scratch", "test_guardia_tmp.db")
class U: id = 1; username = "tmp"; is_active = True
estado = {"eng": None, "S": None}
cli = None
def nuevo_banco():
    global cli
    if estado["eng"] is not None: estado["eng"].dispose()
    for suf in ("", "-wal", "-shm"):
        try: os.remove(T + suf)
        except Exception: pass
    shutil.copyfile(ORIG, T)
    estado["eng"] = create_engine(f"sqlite:///{T}"); estado["S"] = sessionmaker(bind=estado["eng"])
    def ov():
        db = estado["S"]()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
    cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def ex(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
def uu(x): return f"{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}"
def h(x): return x.replace("-", "")
def n_dom(): return q("select count(*) from domicilios")[0][0]
def fiscales(c): return q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.es_fiscal=1 and d.activo=1", c)
GEL = "2fbeb6ebffc649ff81d1e324f410eed6"; LAC = "d3747f3facc04c1a85025f14984a69ed"; JOM = "ff6e98c3710f46f89ecf9045b26ea1aa"
def preparar():
    """Estado «despues de unificar»: Gelato y Lacteos comparten el fiscal (la fila Ruta 36 y 630 de Lacteos) y Obligado 1947 (entrega)."""
    pob = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.es_fiscal=1", LAC)[0][0]
    obl = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.calle like 'Vuelta de Obligado%'", LAC)[0][0]
    ex("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 2097152, 0)", GEL, pob)
    ex("update domicilios set es_fiscal=0 where id in (select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.es_fiscal=1 and d.id != ?)", GEL, pob)
    return pob, obl
def ficha(**extra):
    p = {"es_fiscal": False, "es_entrega": True, "flags": 2097152}; p.update(extra); return p

# ======================================================== GRUPO 1: el caso de Carlos
nuevo_banco(); POB, OBL = preparar()
check("0: preparacion: Gelato y Lacteos comparten el fiscal (Poblet) y Obligado; los dos son Blanco + Responsable Inscripto",
      len(fiscales(GEL)) == 1 and len(fiscales(LAC)) == 1 and fiscales(GEL) == fiscales(LAC)
      and q("select count(*) from domicilios_clientes where domicilio_id=?", OBL)[0][0] == 2
      and all(q("select c.flags_estado&15 in (13,15) and ci.nombre='Responsable Inscripto' from clientes c join condiciones_iva ci on ci.id=c.condicion_iva_id where c.id=?", c)[0][0] for c in (GEL, LAC)))
d0 = n_dom()
ex("insert into vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo) values (?, 'CLIENTE', ?, ?, 'OBLIGADO', 0, 1)", "ab" * 16, LAC, OBL)
r = cli.put(f"/clientes/{uu(LAC)}/domicilios/{uu(OBL)}", json=ficha(es_fiscal=True))
nuevo = r.json().get("id", "") if r.status_code == 200 else ""
check(f"1: Lacteos marca Obligado como fiscal: 200 y devuelve su copia propia (otro id) [{r.status_code}]", r.status_code == 200 and nuevo and h(nuevo) != OBL)
check("1: Obligado original queda como estaba para Gelato (entrega, no fiscal) y Gelato sigue usandolo",
      q("select es_fiscal, es_entrega from domicilios where id=?", OBL) == [(0, 1)] and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", GEL, OBL)[0][0] == 1)
check("1: el fiscal de Gelato NO se movio: sigue siendo Poblet, intacto, y es el unico", fiscales(GEL) == [(POB,)] and q("select es_fiscal from domicilios where id=?", POB) == [(1,)])
check("1: Lacteos tiene UN solo fiscal: su copia de Obligado (la fila de Poblet que usa pasa a su copia, no fiscal)",
      len(fiscales(LAC)) == 1 and fiscales(LAC) == [(h(nuevo),)] and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", LAC, POB)[0][0] == 0)
check("1: solo se crearon 2 copias (la de Obligado y la de Poblet para Lacteos), no se rompio nada mas", n_dom() == d0 + 2)
check("1: la copia de Obligado conserva TODAS las columnas del original (calle, numero, provincia, entrega, vinculo)",
      q("select calle, numero, provincia_id, es_entrega from domicilios where id=?", h(nuevo)) == q("select calle, numero, provincia_id, es_entrega from domicilios where id=?", OBL))
check("1: el vinculo geografico de Lacteos acompaña a su copia (quedo apuntando a la copia de Obligado)",
      q("select count(*) from vinculos_geograficos where entidad_tipo='CLIENTE' and entidad_id=? and domicilio_id=?", LAC, h(nuevo))[0][0] == 1
      and q("select count(*) from vinculos_geograficos where entidad_tipo='CLIENTE' and entidad_id=? and domicilio_id=?", LAC, OBL)[0][0] == 0
      and q("select flags_relacion & 1 from vinculos_geograficos where entidad_id=? and domicilio_id=?", LAC, h(nuevo)) == [(1,)])

# ======================================================== GRUPO 2: roles en domicilios de UN cliente y no-cambios
nuevo_banco(); POB, OBL = preparar(); d0 = n_dom()
falso = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.calle='Calle Falsa'", LAC)[0][0]
r = cli.put(f"/clientes/{uu(LAC)}/domicilios/{uu(falso)}", json=ficha(es_entrega=True))
check(f"2: cambiar el rol de un domicilio de UN solo cliente se hace en el lugar (mismo id, 0 copias) [{r.status_code}]",
      r.status_code == 200 and h(r.json()["id"]) == falso and n_dom() == d0 and q("select es_entrega from domicilios where id=?", falso) == [(1,)])
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(OBL)}", json=ficha())
check(f"3: una edicion que NO cambia ningun rol de un domicilio compartido (la ficha manda siempre todos los roles) no copia nada [{r.status_code}]",
      r.status_code == 200 and h(r.json()["id"]) == OBL and n_dom() == d0)

# ======================================================== GRUPO 3: la regla del fiscal de los Blanco + RI
nuevo_banco(); POB, OBL = preparar(); d0 = n_dom()
# Poblet lo usan los dos: sacarle el fiscal a Gelato lo copia (sale 'sin fiscal' para Gelato) -> debe frenarse por la regla
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(POB)}", json=ficha(es_fiscal=False))
check(f"4: sacarle el fiscal a Gelato (Blanco + RI, unico fiscal, domicilio compartido) -> 409 FISCAL_OBLIGATORIO [{r.status_code}]", r.status_code == 409 and "FISCAL_OBLIGATORIO" in r.text)
check("4: y no queda nada hecho (ni copias ni cambios de rol)", n_dom() == d0 and fiscales(GEL) == [(POB,)] and fiscales(LAC) == [(POB,)])
ex("delete from domicilios_clientes where cliente_id=? and domicilio_id=?", LAC, POB)   # Poblet pasa a ser solo de Gelato
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(POB)}", json=ficha(es_fiscal=False))
check(f"5: sacar el fiscal en el lugar (domicilio de un solo cliente) tambien se frena [{r.status_code}]", r.status_code == 409 and q("select es_fiscal from domicilios where id=?", POB) == [(1,)])
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(POB)}", json=ficha(es_fiscal=True, activo=False))
check(f"5: darlo de baja (activo=false) tambien [{r.status_code}]", r.status_code == 409 and q("select activo from domicilios where id=?", POB) == [(1,)])
r = cli.delete(f"/clientes/{uu(GEL)}/domicilios/{uu(POB)}")
check(f"5: DELETE de la baja tambien [{r.status_code}]", r.status_code == 409 and q("select activo from domicilios where id=?", POB) == [(1,)])
r = cli.delete(f"/clientes/hub/{uu(POB)}/links/{uu(GEL)}")
check(f"5: desvincular desde el Hub el ultimo fiscal tambien [{r.status_code}]", r.status_code == 409 and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", GEL, POB)[0][0] == 1)
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(POB)}", json=ficha(es_fiscal=True, notas_logistica="Portón azul"))
check(f"5: lo demas se sigue pudiendo editar (notas del fiscal) [{r.status_code}]", r.status_code == 200 and q("select notas_logistica from domicilios where id=?", POB) == [("Portón azul",)])
# cambiar el fiscal a otro domicilio SI se puede (el servidor desmarca el anterior solo; la pantalla ya no lo hace aparte)
otro = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.id != ? and (select count(*) from domicilios_clientes x where x.domicilio_id=d.id) = 1 limit 1", GEL, POB)[0][0]
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(otro)}", json=ficha(es_fiscal=True))
check(f"6: cambiar el fiscal de Gelato a otro de sus domicilios: 200 y queda UN solo fiscal (el nuevo) [{r.status_code}]", r.status_code == 200 and fiscales(GEL) == [(otro,)])
# un cliente que NO es Blanco + RI puede quedar sin fiscal
ex("update clientes set flags_estado = (flags_estado & ~15) | 9 where id=?", GEL)
r = cli.put(f"/clientes/{uu(GEL)}/domicilios/{uu(otro)}", json=ficha(es_fiscal=False))
check(f"7: un cliente Rosa (no Blanco) puede quedar sin fiscal [{r.status_code}]", r.status_code == 200 and fiscales(GEL) == [])
# la regla vale para TODO Blanco (Carlos 13/10: «por definicion el sistema no puede borrar domicilio fiscal»), no solo para los Responsables Inscriptos
cf = q("""select c.id, d.id from clientes c join condiciones_iva ci on ci.id=c.condicion_iva_id join domicilios_clientes dc on dc.cliente_id=c.id join domicilios d on d.id=dc.domicilio_id
          where c.activo=1 and ci.nombre='Consumidor Final' and (c.flags_estado & 15) in (13,15) and d.es_fiscal=1 and d.activo=1
          and (select count(*) from domicilios_clientes x where x.domicilio_id=d.id)=1 limit 1""")
check("7b: P tiene un cliente Blanco que es Consumidor Final (no RI) con fiscal", len(cf) == 1)
r = cli.put(f"/clientes/{uu(cf[0][0])}/domicilios/{uu(cf[0][1])}", json=ficha(es_fiscal=False))
check(f"7b: a un Blanco Consumidor Final tampoco se le puede sacar el fiscal: 409 [{r.status_code}]", r.status_code == 409 and q("select es_fiscal from domicilios where id=?", cf[0][1]) == [(1,)])
# un Blanco + RI que YA estaba sin fiscal (los 4 de P) puede editar lo demas y puede AGREGAR un fiscal
jom_dom = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? limit 1", JOM)[0][0]
check("8: Jomax (Blanco + RI) arranca sin fiscal, como en P", fiscales(JOM) == [])
r = cli.put(f"/clientes/{uu(JOM)}/domicilios/{uu(jom_dom)}", json=ficha(notas_logistica="Recepcion de 8 a 12"))
check(f"8: Jomax puede editar notas aunque no tenga fiscal (la regla frena SACAR el fiscal, no bloquea todo) [{r.status_code}]", r.status_code == 200)
r = cli.put(f"/clientes/{uu(JOM)}/domicilios/{uu(jom_dom)}", json=ficha(es_fiscal=True, depto="A"))
check(f"8: y puede marcar su domicilio como fiscal (la correccion de la migrate_062) [{r.status_code}]", r.status_code == 200 and fiscales(JOM) == [(jom_dom,)])

# ======================================================== GRUPO 4: baja y alta
nuevo_banco(); POB, OBL = preparar(); d0 = n_dom()
r = cli.delete(f"/clientes/{uu(LAC)}/domicilios/{uu(OBL)}")
check(f"9: Lacteos da de baja Obligado (compartido): 204 [{r.status_code}]", r.status_code == 204)
check("9: Gelato conserva Obligado ACTIVO y vinculado; el original no se toco", q("select activo from domicilios where id=?", OBL) == [(1,)] and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", GEL, OBL)[0][0] == 1)
check("9: Lacteos queda con una copia INACTIVA suya (se puede restaurar desde 'Inactivos')",
      q("select count(*) from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.activo=0 and d.calle like 'Vuelta de Obligado%'", LAC)[0][0] == 1 and n_dom() == d0 + 1)
nuevo_banco(); POB, OBL = preparar(); d0 = n_dom()
prov = q("select id from provincias where upper(nombre) like 'BUENOS%' limit 1")[0][0]
r = cli.post(f"/clientes/{uu(LAC)}/domicilios", json={"calle": "Calle Nueva", "numero": "55", "localidad": "La Plata", "provincia_id": prov, "es_fiscal": True, "es_entrega": True})
nid = r.json().get("id", "") if r.status_code == 201 else ""
check(f"10: Lacteos da de alta un domicilio fiscal nuevo [{r.status_code}]: su fiscal es el nuevo y el de Gelato (Poblet, que compartian) NO se toco",
      r.status_code == 201 and fiscales(LAC) == [(h(nid),)] and fiscales(GEL) == [(POB,)] and q("select es_fiscal from domicilios where id=?", POB) == [(1,)])

# ======================================================== GRUPO 5: Hub (maestro) y bifurcacion
nuevo_banco(); POB, OBL = preparar()
r = cli.put(f"/clientes/hub/{uu(OBL)}", json={"es_fiscal": True})
check(f"11: el maestro del Hub NO cambia el rol de un domicilio compartido: 409 ROL_DE_DOMICILIO_COMPARTIDO [{r.status_code}]", r.status_code == 409 and "ROL_DE_DOMICILIO_COMPARTIDO" in r.text and q("select es_fiscal from domicilios where id=?", OBL) == [(0,)])
r = cli.put(f"/clientes/hub/{uu(OBL)}", json={"es_fiscal": False, "es_entrega": True, "observaciones": "Dock 3"})
check(f"11: lo que no cambia un rol (o el lugar mismo) se edita sin problema [{r.status_code}]", r.status_code == 200 and q("select observaciones from domicilios where id=?", OBL) == [("Dock 3",)])
falso = q("select d.id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.calle='Calle Falsa'", LAC)[0][0]
r = cli.put(f"/clientes/hub/{uu(falso)}", json={"es_entrega": True})
check(f"11: en un domicilio de un solo cliente el Hub si cambia el rol [{r.status_code}]", r.status_code == 200 and q("select es_entrega from domicilios where id=?", falso) == [(1,)])
d0 = n_dom()
r = cli.post(f"/clientes/{uu(LAC)}/domicilios/{uu(OBL)}/fork", json={"es_fiscal": True, "notas_logistica": "Solo Lacteos"})
nuevo = r.json().get("id", "") if r.status_code == 200 else ""
check(f"12: /fork de un domicilio compartido con un rol en el payload: copia COMPLETA (calle, numero, entrega heredados), fiscal para Lacteos y Gelato intacto [{r.status_code}]",
      r.status_code == 200 and nuevo and q("select calle, numero, es_entrega, es_fiscal, notas_logistica from domicilios where id=?", h(nuevo)) == [(q("select calle from domicilios where id=?", OBL)[0][0], "1947", 1, 1, "Solo Lacteos")]
      and fiscales(LAC) == [(h(nuevo),)] and fiscales(GEL) == [(POB,)])

# ======================================================== GRUPO 6: el buscador no ofrece un domicilio dado de baja
nuevo_banco(); POB, OBL = preparar()
r = cli.get("/clientes/hub/similares", params={"calle": "Vuelta de Obligado", "numero": "1947", "localidad": "CABA"})
check(f"13: el buscador encuentra Obligado mientras esta activo [{r.status_code}] {len(r.json()) if r.status_code == 200 else '-'}", r.status_code == 200 and len(r.json()) >= 1)
ex("update domicilios set activo=0 where id=?", OBL)
r = cli.get("/clientes/hub/similares", params={"calle": "Vuelta de Obligado", "numero": "1947", "localidad": "CABA"})
check(f"13: y NO lo ofrece cuando esta dado de baja desde la ficha (activo = 0) [{r.status_code}] {len(r.json()) if r.status_code == 200 else '-'}", r.status_code == 200 and r.json() == [])

del cli
estado["eng"].dispose()
for suf in ("", "-wal", "-shm"):
    try: os.remove(T + suf)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
