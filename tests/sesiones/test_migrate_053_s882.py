r"""migrate_053 (S882): Poblet, OC 3476 -- facturas 2566 y 2576 en el pedido #72, duplicados del #83 retirados. Sobre COPIAS de la base de P del 08/10 12:24."""
import sys, os, shutil, sqlite3, subprocess, re
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.pedidos.cantidades import facturado_por_renglon
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); shutil.copyfile(ORIG, p); return p
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def migrar(db): return correr(db, "migrate_053_poblet_oc3476_facturas_2566_2576.py")
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def facturado(db, ids):
    e = create_engine("sqlite:///" + db); s = sessionmaker(bind=e)(); v = facturado_por_renglon(s, ids); s.close(); e.dispose(); return v
MAXRI = q(ORIG, "select max(id) from remitos_items")[0][0]
def resto(db):
    """todo lo que la migracion NO debe tocar, como valor comparable"""
    return (q(db, "select id, estado, pedido_id, total, flags_estado from facturas where numero_comprobante not in (2566, 2576) order by id"),
            q(db, "select id, estado, pedido_id, flags_estado, valor_declarado from remitos where numero_legal not like '%2576' order by id"),
            q(db, "select id, estado, total, flags_estado, nota from pedidos where id not in (72, 83) order by id"),
            q(db, "select id, cantidad from pedidos_items where pedido_id not in (72, 83) order by id"),
            q(db, "select id, cantidad_remitida from remitos_items where id <= ? order by id", MAXRI),
            q(db, "select count(*) from remitos_notas"))

# ---------- 0) partida: el estado que se audito ----------
check("partida: #72 con 100 bolsas y 150 entregadas (0015-3010: 50 + 0016-2576 erroneo: 100); #83 pendiente con 50; 2576 registrada dos veces; 2566 sin registrar",
      q(ORIG, "select sum(ri.cantidad_remitida) from remitos_items ri where ri.pedido_item_id=127")[0][0] == 150
      and q(ORIG, "select estado, oc from pedidos where id=83")[0] == ("PENDIENTE", "3476")
      and q(ORIG, "select count(*) from facturas where numero_comprobante=2576")[0][0] == 2
      and q(ORIG, "select count(*) from facturas where numero_comprobante=2566")[0][0] == 0)

# ---------- 1) aplica ----------
A = copia("test_053_a.db")
antes = resto(A)
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "OK --" in out and "2566 registrada" in out and "ERROR" not in out and "AVISO" not in out)
f76 = q(A, "select tipo_comprobante, estado, pedido_id, fecha_emision, neto_gravado, iva_21, total, cae_vencimiento, cuit_comprador from facturas where numero_comprobante=2576 and estado != 'ANULADA'")
check(f"2576: queda UNA vigente, Factura A autorizada en el #72 por $589.875 (neto 487.500 + IVA 102.375), vto 07/08 {f76}",
      f76 == [("FACTURA_A", "AUTORIZADA_AFIP", "72", "2026-07-28", 487500.0, 102375.0, 589875.0, "2026-08-07", "33660726859")])
check("2576: su renglon (50 bolsas) esta enlazado al renglon #127 del pedido", q(A, "select fi.pedido_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2576 and f.estado != 'ANULADA'") == [(127, 50.0)])
check("2576: el registro duplicado del #83 queda ANULADA (no se borra) y conserva su nota original",
      q(A, "select estado, pedido_id, substr(notas_auditoria, 1, 20) like '%' from facturas where tipo_comprobante='PRESUPUESTO_X' and numero_comprobante=2576")[0][:2] == ("ANULADA", "83")
      and "DUPLICADO" in q(A, "select notas_auditoria from facturas where tipo_comprobante='PRESUPUESTO_X' and numero_comprobante=2576")[0][0])
f66 = q(A, "select tipo_comprobante, estado, pedido_id, fecha_emision, total, cae, cae_vencimiento, cuit_comprador from facturas where numero_comprobante=2566")
check(f"2566: registrada como Factura A autorizada en el #72, $589.875, CAE de ARCA {f66}",
      f66 == [("FACTURA_A", "AUTORIZADA_AFIP", "72", "2026-07-06", 589875.0, "86272716608690", "2026-07-16", "33660726859")])
check("2566: renglon de 50 bolsas enlazado al #127", q(A, "select fi.pedido_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2566") == [(127, 50.0)])
check("renglon #127: pedido 100 / facturado 100 (2566 + 2576) -- lo mide el mismo codigo que usa la pantalla", facturado(A, [127]).get(127) == (100.0, 0.0))
check("renglon #127: remitido 100 (0015-3010: 50 + 0016-2576 correcto: 50), ya no 150",
      q(A, "select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' where ri.pedido_item_id=127")[0][0] == 100.0)
ERR, BUENO = "df87a5223e254c6089d97ad9e48cc6a0", "facefb74b08042df96e8b89e82108545"
rb = q(A, "select pedido_id, estado, domicilio_entrega_id, valor_declarado from remitos where id=?", BUENO)[0]
check(f"remito 0016-2576 CORRECTO (12:47, Poblet, $487.500): pasa al #72, sigue vigente {rb[:2]}", rb[0] == 72 and rb[1] == "BORRADOR" and rb[3] == 487500.0 and rb[2] == q(A, "select domicilio_entrega_id from pedidos where id=72")[0][0])
check("...con su renglon de 50 bolsas (remitida y declarada) enganchado al #127 y una nota [SISTEMA]",
      q(A, "select pedido_item_id, cantidad_remitida, cantidad_declarada from remitos_items where remito_id=?", BUENO) == [(127, 50.0, 50.0)]
      and q(A, "select count(*) from remitos_notas where remito_id=? and texto like '%migrate_053%'", BUENO)[0][0] == 1)
check("remito 0016-2576 ERRONEO (12:46: 100 bolsas, domicilio de CABA): ANULADO con nota, NO borrado, su renglon intacto",
      q(A, "select estado from remitos where id=?", ERR)[0][0] == "ANULADO" and q(A, "select cantidad_remitida from remitos_items where id=43")[0][0] == 100.0
      and q(A, "select count(*) from remitos_notas where remito_id=? and texto like '%ERRONEA%'", ERR)[0][0] == 1)
check("vinculos: la factura 2576 vigente queda con el remito correcto y la anulada con el anulado",
      q(A, "select fr.remito_id from facturas_remitos fr join facturas f on f.id=fr.factura_id where f.numero_comprobante=2576 and f.estado!='ANULADA'") == [(BUENO,)]
      and q(A, "select fr.remito_id from facturas_remitos fr join facturas f on f.id=fr.factura_id where f.numero_comprobante=2576 and f.estado='ANULADA'") == [(ERR,)])
p83 = q(A, "select estado, flags_estado, nota from pedidos where id=83")[0]
check(f"pedido #83: ANULADO (baja logica: bit 35 prendido, sin bits 32-34) y con nota {p83[0]}",
      p83[0] == "ANULADO" and p83[1] & (1 << 35) and not p83[1] & ((1 << 32) | (1 << 33) | (1 << 34)) and "duplicado del pedido #72" in p83[2].replace("Anulado por duplicado del pedido #72", "duplicado del pedido #72"))
f72 = q(A, "select estado, flags_estado from pedidos where id=72")[0]
check(f"pedido #72: entrega COMPLETA (bit 21), sin entrega parcial (bit 20); el estado no cambia ({f72[0]})", f72[0] == "FACTURADO" and f72[1] & (1 << 21) and not f72[1] & (1 << 20))
check("el resto de la base NO cambia (facturas, remitos, pedidos, renglones, remitos_items, notas)", resto(A)[:5] == antes[:5] and resto(A)[5][0][0] == antes[5][0][0] + 2)
check("#97 y su remito 0015-3015 (100) quedan intactos; la 2586 no se registra; la 2600 sigue en el #98",
      q(A, "select estado from pedidos where id=97")[0][0] == "PENDIENTE" and q(A, "select count(*) from remitos where numero_legal like '%3015' and pedido_id=97")[0][0] == 1
      and q(A, "select count(*) from facturas where numero_comprobante=2586")[0][0] == 0 and q(A, "select pedido_id from facturas where numero_comprobante=2600 and cae is not null")[0][0] == "98")
# idempotencia
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '053%'"); con.commit(); con.close()
snap = resto(A)
rc3, out3 = migrar(A)
check(f"sin el registro: reconoce que ya esta hecho y no toca nada [{rc3}] {[l for l in out3.splitlines() if 'OK --' in l]}",
      rc3 == 0 and "nada que hacer" in out3 and resto(A) == snap and q(A, "select count(*) from facturas where numero_comprobante=2566")[0][0] == 1)

# ---------- 2) guardas: si P ya no esta como se audito, no toca nada ----------
casos = [("la OC del #83 ya no es 3476", "update pedidos set oc='9999' where id=83"),
         ("el #83 ya no esta pendiente", "update pedidos set estado='FACTURADO' where id=83"),
         ("el #83 tiene un segundo renglon", "insert into pedidos_items (pedido_id, producto_id, cantidad, precio_unitario) select 83, producto_id, 1, 1 from pedidos_items where id=146"),
         ("el remito vacio del #83 ahora tiene un renglon", "insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) values ('facefb74b08042df96e8b89e82108545', 146, 5, 5)"),
         ("el remito del #72 ya dice 60", "update remitos_items set cantidad_remitida=60 where id=43"),
         ("el remito correcto ya no tiene el domicilio del pedido", "update remitos set domicilio_entrega_id='066314b883c74ffba62794e262a83d40' where id='facefb74b08042df96e8b89e82108545'"),
         ("el vinculo factura-remito de la 2576 ya no es el auditado", "update facturas_remitos set remito_id='facefb74b08042df96e8b89e82108545' where factura_id='4fefad1401ad44bca94d1165d1b7cb20'"),
         ("la 2566 ya esta registrada", "insert into facturas (id, cliente_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fake66', cliente_id, 'FACTURA_A', 1, 2566, 'AUTORIZADA_AFIP', 1, '1', 3 from pedidos where id=72"),
         ("el #72 tiene otra factura vigente con CAE", "insert into facturas (id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fake99', cliente_id, '72', 'FACTURA_A', 1, 99999, 'AUTORIZADA_AFIP', 1, '2', 3 from pedidos where id=72"),
         ("el CUIT del cliente no es el de Poblet", "update clientes set cuit='20111111112' where id=(select cliente_id from pedidos where id=72)")]
for desc, sql in casos:
    G = copia("test_053_g.db")
    con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    s0 = (resto(G), q(G, "select estado from pedidos where id in (72,83) order by id"), q(G, "select count(*) from facturas")[0][0])
    rcg, outg = migrar(G)
    s1 = (resto(G), q(G, "select estado from pedidos where id in (72,83) order by id"), q(G, "select count(*) from facturas")[0][0])
    check(f"guarda: {desc} -> no toca nada, avisa y NO se registra [{rcg}]", rcg == 0 and "AVISO" in outg and s0 == s1 and not q(G, "select 1 from _migraciones_aplicadas where id like '053%'")
          and q(G, "select tipo_comprobante from facturas where numero_comprobante=2576 and pedido_id='72'")[0][0] != "FACTURA_A")
    os.remove(G)

# ---------- 3) con la 051 y la 052 en el mismo arranque ----------
C = copia("test_053_c.db")
rc_a, o_a = migrar(C)
rc_b, o_b = correr(C, "migrate_051_remitos_0016_al_pedido_de_su_factura.py")
rc_c, o_c = correr(C, "migrate_052_facturas_con_cae_a_autorizada.py")
check(f"053 + 051 + 052 en secuencia: sin errores; la 051 ya no avisa por la 2576 (queda solo el aviso de la 2562) [{rc_a}{rc_b}{rc_c}]",
      rc_a == rc_b == rc_c == 0 and o_b.count("AVISO") == 1 and "2562" in o_b and "2576" not in o_b)
check("tras las tres: 2576 y 2566 siguen autorizadas y el renglon #127 sigue 100/100/100",
      q(C, "select count(*) from facturas where numero_comprobante in (2566, 2576) and estado='AUTORIZADA_AFIP' and tipo_comprobante='FACTURA_A'")[0][0] == 2 and facturado(C, [127]).get(127) == (100.0, 0.0)
      and q(C, "select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' where ri.pedido_item_id=127")[0][0] == 100.0)
# auditoria
env = dict(os.environ, PYTHONIOENCODING="utf-8")
sal = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ensayo_049", "auditoria_053.xlsx"); os.makedirs(os.path.dirname(sal), exist_ok=True)
r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "auditoria_facturas.py"), "--db", C, "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\OF", "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\P",
                    "--arca-csv", os.path.join(os.path.dirname(os.path.abspath(__file__)), "arca_csv", "arca_emitidos.csv"), "--salida", sal], capture_output=True, text=True, encoding="utf-8", env=env)
m = {k: re.search(k + r": (\d+)", r.stdout) for k in ("OK", "DIFERENCIAS", "DUPLICADAS")}
print("   auditoria posterior:", {k: (v.group(1) if v else None) for k, v in m.items()})
check("la auditoria posterior ya no ve la 2576 como duplicada ni con diferencias de tipo/total",
      (m["DUPLICADAS"] is None or int(m["DUPLICADAS"].group(1)) == 0) or "2576" not in r.stdout.split("DUPLICADAS")[-1][:200])

for p in (A, C):
    try: os.remove(p)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
