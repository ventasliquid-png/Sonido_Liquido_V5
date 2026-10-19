r"""migrate_060 (S883): unifica las dos fichas de Expreso Demonte del padron de transportes de P. Sobre COPIAS de la base de P de las 17:51 (con las migraciones 051-059 aplicadas)."""
import sys, os, shutil, sqlite3, subprocess, json
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1751.db"
ACT, DUP = "db42f9b049394c16b3ab93e1a3b5f6ae", "b26c8617e8734c2c94194e0ee537ba5a"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); shutil.copyfile(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_060_unificar_expreso_demonte.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def emp(db, id_):
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    r = con.execute("select * from empresas_transporte where id=?", (id_,)).fetchone(); con.close(); return dict(r) if r else None
def todo_menos(db):
    """lo que NO deberia cambiar: las otras fichas de transporte y el contenido de las tablas que apuntan a transportes, salvo las columnas de transporte"""
    return (q(db, "select * from empresas_transporte where id not in (?,?) order by id", ACT, DUP),
            q(db, "select id, estado, total from pedidos order by id"), q(db, "select id, estado from remitos order by id"),
            q(db, "select count(*) from domicilios"), q(db, "select count(*) from clientes"), q(db, "select id, estado, total from facturas order by id"))

check("partida: dos fichas con el mismo CUIT, una activa y una inactiva, y una fila de domicilios_legacy apuntando a la duplicada",
      q(ORIG, "select count(*) from empresas_transporte where cuit='30709651257'")[0][0] == 2
      and q(ORIG, "select flags_estado & 2 from empresas_transporte where id=?", DUP)[0][0] == 0 and q(ORIG, "select flags_estado & 2 from empresas_transporte where id=?", ACT)[0][0] == 2
      and q(ORIG, "select count(*) from domicilios_legacy where transporte_id=?", DUP)[0][0] == 1)
A = copia("test_060_a.db"); antes = todo_menos(A); act0, dup0 = emp(A, ACT), emp(A, DUP)
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "una sola ficha activa" in out and "ERROR" not in out and "AVISO" not in out)
a, d = emp(A, ACT), emp(A, DUP)
check(f"la ficha activa pasa a llamarse «Expreso Demonte», conserva su CUIT, su WhatsApp ({a['whatsapp']}) y su telefono ({a['telefono_reclamos']}) y sigue activa", a["nombre"] == "Expreso Demonte" and a["cuit"] == act0["cuit"] and a["whatsapp"] == act0["whatsapp"] and a["telefono_reclamos"] == act0["telefono_reclamos"] and a["flags_estado"] & 2 == 2)
check(f"toma el sitio de seguimiento de la otra y anota la razon social de ARCA, el CUIT y el otro telefono [{a['web_tracking']}]", a["web_tracking"] == "https://www.expresodemonte.com/web/" and "TRANSPORTE A DEMONTE SRL" in a["observaciones"] and "30-70965125-7" in a["observaciones"] and "379 5001507" in a["observaciones"])
check("la duplicada NO se borra: queda inactiva, con su nombre original y una nota [SISTEMA] que dice en cual se unifico", d is not None and d["nombre"] == "Expreso Damonte" and d["flags_estado"] & 2 == 0 and "[SISTEMA]" in d["observaciones"] and ACT in d["observaciones"])
check("la fila de domicilios_legacy que apuntaba a la duplicada apunta ahora a la unica", q(A, "select count(*) from domicilios_legacy where transporte_id=?", ACT)[0][0] == 1 and q(A, "select count(*) from domicilios_legacy where transporte_id=?", DUP)[0][0] == 0)
check("no hay referencias a la ficha duplicada en ninguna tabla",
      all(q(A, f"select count(*) from {t} where {c}=?", DUP)[0][0] == 0 for t, c in [("domicilios", "transporte_id"), ("domicilios", "intermediario_id"), ("domicilios_legacy", "transporte_id"), ("domicilios_legacy", "intermediario_id"), ("clientes", "transporte_habitual_id"), ("pedidos", "transporte_id"), ("remitos", "transporte_id")]))
check("nada mas cambia: las otras fichas de transporte, pedidos, remitos, facturas, clientes y domicilios", todo_menos(A) == antes)
check("la cantidad de fichas es la misma (6): se unifica, no se borra", q(A, "select count(*) from empresas_transporte")[0][0] == 6)

# el padron que ve la pantalla (GET /logistica/empresas?status=active): una sola Demonte
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{A}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
r = cli.get("/logistica/empresas?status=active"); nombres = sorted(e["nombre"] for e in r.json()) if r.status_code == 200 else r.text[:100]
check(f"la lista de transportes activos de la pantalla muestra una sola Demonte [{r.status_code}] {nombres}", r.status_code == 200 and [n for n in nombres if "emonte" in n.lower() or "amonte" in n.lower()] == ["Expreso Demonte"] and len(nombres) == 5)
r2 = cli.get("/logistica/empresas?status=inactive"); check("la duplicada figura entre las inactivas (se puede recuperar)", r2.status_code == 200 and any(e["nombre"] == "Expreso Damonte" for e in r2.json()))
r3 = cli.post("/logistica/empresas", json={"nombre": "Expreso Damonte"}); check(f"y no se puede volver a crear a mano «Expreso Damonte» (control de nombre) [{r3.status_code}]", r3.status_code == 409)
del cli; eng.dispose()

rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '060%'"); con.commit(); con.close()
snap = (emp(A, ACT), emp(A, DUP)); rc3, out3 = migrar(A)
check(f"sin el registro: la marca de la ficha evita repetir y no toca nada [{rc3}]", rc3 == 0 and "ya tiene la marca" in out3 and (emp(A, ACT), emp(A, DUP)) == snap)
os.remove(A)

# ---------- referencias que aparezcan en otras tablas tambien se mueven ----------
B = copia("test_060_b.db"); con = sqlite3.connect(B)
dom = con.execute("select id from domicilios where transporte_id is null limit 1").fetchone()[0]; ped = con.execute("select id from pedidos limit 1").fetchone()[0]
con.execute("update domicilios set transporte_id=? where id=?", (DUP, dom)); con.execute("update pedidos set transporte_id=? where id=?", (DUP, ped)); con.commit(); con.close()
rc, out = migrar(B)
check(f"si un domicilio o un pedido ya apuntaban a la duplicada, pasan a la unica [{rc}] {[l for l in out.splitlines() if 'Referencias' in l][:1]}",
      rc == 0 and q(B, "select transporte_id from domicilios where id=?", dom)[0][0] == ACT and q(B, "select transporte_id from pedidos where id=?", ped)[0][0] == ACT)
os.remove(B)

# ---------- guardas: no se toca nada ----------
casos = [("el CUIT de la duplicada no es el esperado", "update empresas_transporte set cuit='20111111112' where id='%s'" % DUP),
         ("alguien le cambio el nombre a la ficha activa", "update empresas_transporte set nombre='OTRA COSA SA' where id='%s'" % ACT),
         ("ya existe otra ficha llamada «Expreso Demonte»", "insert into empresas_transporte (id, nombre, flags_estado) values ('x1', 'Expreso Demonte', 3)"),
         ("la ficha que iba a quedar no esta activa", "update empresas_transporte set flags_estado=1 where id='%s'" % ACT),
         ("falta una de las dos fichas", "delete from empresas_transporte where id='%s'" % DUP)]
for desc, sql in casos:
    G = copia("test_060_g.db"); con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    s0 = (emp(G, ACT), emp(G, DUP), q(G, "select count(*) from domicilios_legacy where transporte_id=?", DUP)[0][0]); rc, out = migrar(G)
    check(f"guarda: {desc} -> avisa y no toca nada [{rc}]", rc == 0 and "AVISO" in out and (emp(G, ACT), emp(G, DUP), q(G, "select count(*) from domicilios_legacy where transporte_id=?", DUP)[0][0]) == s0)
    os.remove(G)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
