r"""migrate_052 (S882): pasa a AUTORIZADA_AFIP las facturas con CAE real que la ingesta vieja dejo en BORRADOR + delete_remito ya no borra facturas con CAE.
Sobre COPIAS de la base de P del 08/10 12:24 (ya con 048, 049 y 050; las facturas todavia en BORRADOR)."""
import sys, os, shutil, sqlite3, subprocess, json
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos (los mappers se resuelven entre si)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db"   # estado ANTES de la 052 (la copia mas nueva ya la tendra)
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_052_facturas_con_cae_a_autorizada.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v

J = json.load(open(os.path.join(RAIZ, "scripts", "data", "correcciones_facturas_s881.json"), encoding="utf-8"))["correcciones"]
CON_CAE = "cae is not null and trim(cae) != ''"

# ---------- 1) aplica ----------
A = copia("test_052_a.db")
check("partida: 34 facturas con CAE en BORRADOR (+ la 2576 tipo B, que no esta en el archivo) y 29 autorizadas de Factura A",
      q(A, f"select count(*) from facturas where estado='BORRADOR' and {CON_CAE}")[0][0] == 35
      and q(A, f"select count(*) from facturas where estado='AUTORIZADA_AFIP' and tipo_comprobante='FACTURA_A'")[0][0] == 29)
antes = {r[0]: r for r in q(A, f"select id, cliente_id, pedido_id, tipo_comprobante, total, neto_gravado, iva_21, fecha_emision, cae, flags_estado, numero_comprobante from facturas where {CON_CAE}")}
items0 = q(A, "select count(*), sum(cantidad), sum(subtotal_neto) from facturas_items")[0]
peds0 = q(A, "select count(*), sum(total), group_concat(estado), group_concat(flags_estado) from pedidos")[0]
rem0 = q(A, "select count(*), sum(valor_declarado), group_concat(estado), group_concat(pedido_id) from remitos")[0]
x0 = q(A, "select count(*) from facturas where cae is null or trim(cae)=''")[0][0]
dup0 = q(A, "select id, tipo_comprobante, estado, total, notas_auditoria from facturas where numero_comprobante=2576 order by tipo_comprobante")
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "pasadas a AUTORIZADA_AFIP 34" in out and "ya estaban 9" in out and "saltadas 0" in out and "con error 0" in out)
check("ahora hay 64 facturas con CAE autorizadas (29 + 34 + la 2576 tipo X que ya lo estaba) y queda UNA en BORRADOR con CAE: la 2576 tipo B",
      q(A, f"select count(*) from facturas where estado='AUTORIZADA_AFIP' and {CON_CAE}")[0][0] == 64   # 63 + la 2576 tipo X que ya estaba autorizada
      and q(A, f"select numero_comprobante, tipo_comprobante from facturas where estado='BORRADOR' and {CON_CAE}") == [(2576, "FACTURA_B")])
despues = {r[0]: r for r in q(A, f"select id, cliente_id, pedido_id, tipo_comprobante, total, neto_gravado, iva_21, fecha_emision, cae, flags_estado, numero_comprobante from facturas where {CON_CAE}")}
check("cliente, pedido, tipo, importes, fecha, CAE y flags de las 65 facturas NO cambian (solo el estado)", antes == despues)
nota = q(A, "select notas_auditoria from facturas where numero_comprobante=2594 and cae is not null")[0][0]
check("la 2594 conserva su nota anterior y suma la marca [SISTEMA]", "Corregida desde el PDF de ARCA" in nota and "[SISTEMA] Pasada de BORRADOR a AUTORIZADA_AFIP" in nota)
check("renglones de factura, pedidos y remitos NO cambian", q(A, "select count(*), sum(cantidad), sum(subtotal_neto) from facturas_items")[0] == items0
      and q(A, "select count(*), sum(total), group_concat(estado), group_concat(flags_estado) from pedidos")[0] == peds0
      and q(A, "select count(*), sum(valor_declarado), group_concat(estado), group_concat(pedido_id) from remitos")[0] == rem0)
check("los presupuestos X sin CAE (borradores legitimos) no se tocan", q(A, "select count(*) from facturas where cae is null or trim(cae)=''")[0][0] == x0
      and q(A, "select count(*) from facturas where (cae is null or trim(cae)='') and estado!='BORRADOR'")[0][0] == 0)
check("la 2576 (registrada dos veces) no se toca", q(A, "select id, tipo_comprobante, estado, total, notas_auditoria from facturas where numero_comprobante=2576 order by tipo_comprobante") == dup0)
# el efecto buscado: ahora cuentan como facturado en el renglon del pedido
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.pedidos.cantidades import facturado_por_renglon
it2577 = q(A, "select fi.pedido_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2577 and f.cae is not null and fi.pedido_item_id is not null")
def facturado(db):
    e = create_engine("sqlite:///" + db); s = sessionmaker(bind=e)(); v = facturado_por_renglon(s, [i[0] for i in it2577]); s.close(); e.dispose(); return v
v1 = facturado(A)
check(f"la 2577 (pedido #82): sus {len(it2577)} renglones ahora cuentan como facturados con la cantidad de la factura", it2577 and all(abs(v1.get(pid, (0, 0))[0] - cant) < 1e-6 for pid, cant in it2577))
check("antes de la migracion esos mismos renglones figuraban con 0 facturado", not facturado(ORIG_COPY := copia("test_052_orig.db")))
# idempotencia
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id='052_facturas_con_cae_a_autorizada'"); con.commit(); con.close()
rc3, out3 = migrar(A)
check(f"sin el registro: las 43 ya estan autorizadas, no se toca nada {[l for l in out3.splitlines() if 'OK --' in l]}", rc3 == 0 and "pasadas a AUTORIZADA_AFIP 0" in out3 and "ya estaban 43" in out3
      and q(A, "select count(*) from facturas where notas_auditoria like '%migrate_052%'")[0][0] == 34)

# ---------- 2) guardas ----------
B = copia("test_052_b.db")
con = sqlite3.connect(B)
con.execute("update facturas set total = total + 5 where numero_comprobante=2594 and cae is not null")                              # (a) cambio el total
con.execute("update facturas set tipo_comprobante='FACTURA_B' where numero_comprobante=2595 and cae is not null")                   # (b) cambio el tipo
con.execute("update facturas set estado='ANULADA' where numero_comprobante=2596 and cae is not null")                               # (c) anulada
con.execute("insert into facturas (id, cliente_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) "
            "select 'fake1', cliente_id, 'PRESUPUESTO_X', punto_venta, numero_comprobante, 'BORRADOR', total, cae, 3 from facturas where numero_comprobante=2598 and cae is not null")   # (d) mismo numero y CAE dos veces
con.commit(); con.close()
rcB, outB = migrar(B)
check(f"guardas: (a) total distinto, (b) tipo distinto, (c) anulada, (d) registrada dos veces -> las 4 se SALTAN con aviso; las otras 30 pasan {[l for l in outB.splitlines() if 'OK --' in l]}",
      rcB == 0 and "saltadas 4" in outB and "pasadas a AUTORIZADA_AFIP 30" in outB and outB.count("AVISO") == 4)
check("las saltadas quedan como estaban", q(B, "select estado from facturas where numero_comprobante=2594 and tipo_comprobante='FACTURA_A'")[0][0] == "BORRADOR"
      and q(B, "select estado from facturas where numero_comprobante=2596 and cae is not null")[0][0] == "ANULADA")

# ---------- 3) delete_remito ya no borra una factura con CAE ----------
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from fastapi.testclient import TestClient
C = copia("test_052_c.db")
eng = create_engine(f"sqlite:///{C}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
rid, fid = q(C, "select r.id, f.id from facturas f join facturas_remitos fr on fr.factura_id=f.id join remitos r on r.id=fr.remito_id where f.estado='BORRADOR' and f.cae is not null and trim(f.cae) != '' and r.estado='BORRADOR' and f.numero_comprobante=2551")[0]
# [S891] el tacho solo descarta remitos SIN número (uno con número se anula): con número da 409; para probar la cascada con la factura se le
# saca el número en la copia
def sin_numero(remito_id):
    con = sqlite3.connect(C); con.execute("update remitos set numero_legal=NULL where id=?", (remito_id,)); con.commit(); con.close()
r = cli.delete(f"/remitos/{rid}")
check(f"[S891] con su número 0016-2551 el tacho no lo borra: 409 REMITO_CON_NUMERO [{r.status_code}]", r.status_code == 409 and "REMITO_CON_NUMERO" in r.text)
sin_numero(rid)
r = cli.delete(f"/remitos/{rid}")
check(f"borrar el remito 0016-2551 (BORRADOR) con su factura en BORRADOR pero CON CAE [{r.status_code}]: el remito se va y la factura se QUEDA",
      r.status_code == 200 and not q(C, "select 1 from remitos where id=?", rid) and q(C, "select numero_comprobante, cae from facturas where id=?", fid) != [] and q(C, "select count(*) from facturas_items where factura_id=?", fid)[0][0] >= 1)
# sin CAE (el espejo legitimo) se sigue borrando como antes
fila = q(C, "select r.id, f.id from facturas f join facturas_remitos fr on fr.factura_id=f.id join remitos r on r.id=fr.remito_id where f.estado='BORRADOR' and (f.cae is null or trim(f.cae)='') and r.estado='BORRADOR' limit 1")
if fila:
    sin_numero(fila[0][0])
    r2 = cli.delete(f"/remitos/{fila[0][0]}")
    check(f"un remito con factura BORRADOR SIN CAE se borra junto con ella, como antes [{r2.status_code}]", r2.status_code == 200 and not q(C, "select 1 from facturas where id=?", fila[0][1]))
else:
    # la base de P no tiene ese caso: se arma uno en la copia
    con = sqlite3.connect(C)
    rid2, fid2 = con.execute("select r.id, f.id from facturas f join facturas_remitos fr on fr.factura_id=f.id join remitos r on r.id=fr.remito_id where f.estado='BORRADOR' and f.cae is not null and r.estado='BORRADOR' limit 1").fetchone()
    con.execute("update facturas set cae=null where id=?", (fid2,)); con.commit(); con.close()
    sin_numero(rid2)
    r2 = cli.delete(f"/remitos/{rid2}")
    check(f"(caso armado en la copia) un remito con factura BORRADOR SIN CAE se borra junto con ella, como antes [{r2.status_code}]", r2.status_code == 200 and not q(C, "select 1 from facturas where id=?", fid2))
del cli; eng.dispose()

for p in (A, B, C, ORIG_COPY):
    try: os.remove(p)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
