r"""migrate_057 (S882): remito 0016-2597 (Cassara, OC 19211): impreso 1.500, salieron y se recibieron 1.480. Sobre COPIAS de la base de P del 08/10 12:24 (con 052 y 055)."""
import sys, os, shutil, sqlite3, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.pedidos.cantidades import facturado_por_renglon
from backend.informes.router import _filas_cumplimiento_oc
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db"
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
S057 = "migrate_057_remito_2597_cassara_1480.py"
def copia(n, previas=True):
    p = os.path.join(RAIZ, "scratch", n); shutil.copyfile(ORIG, p)
    if previas:
        correr(p, "migrate_052_facturas_con_cae_a_autorizada.py"); correr(p, "migrate_055_facturas_aceptadas_y_nc_cassara.py")
    return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def resto(db):
    return (q(db, "select id, estado, pedido_id, total from facturas order by id"), q(db, "select id, estado, pedido_id, flags_estado from remitos order by id"),
            q(db, "select id, estado, total, flags_estado, nota from pedidos where id != 109 order by id"), q(db, "select id, cantidad from pedidos_items order by id"),
            q(db, "select id, cantidad_remitida, cantidad_declarada, cantidad_recibida from remitos_items where remito_id not in (select id from remitos where numero_legal='0016-00002597') order by id"))

check("partida: el remito 0016-2597 esta sin renglones; el pedido #109 (CUMPLIDO, OC 19211) pide 1.480 y la factura 2597 trae 1.500",
      q(ORIG, "select count(*) from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002597'")[0][0] == 0
      and q(ORIG, "select estado, oc from pedidos where id=109")[0] == ("CUMPLIDO", "19211") and q(ORIG, "select cantidad from pedidos_items where id=215")[0][0] == 1480.0
      and q(ORIG, "select sum(fi.cantidad) from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2597 and f.cae is not null")[0][0] == 1500.0)

A = copia("test_057_a.db")
antes = resto(A); flags0 = q(A, "select flags_estado from pedidos where id=109")[0][0]
rc, out = correr(A, S057)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "declarada 1500, remitida 1480, recibida 1480" in out and "ERROR" not in out and "AVISO" not in out)
it = q(A, "select ri.pedido_item_id, ri.cantidad_declarada, ri.cantidad_remitida, ri.cantidad_recibida from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002597'")
check(f"el renglon queda enganchado al #215 con declarada 1.500 / remitida 1.480 / recibida 1.480 {it}", it == [(215, 1500.0, 1480.0, 1480.0)])
check("queda una nota [SISTEMA] en el remito con el relato", q(A, "select count(*) from remitos_notas n join remitos r on r.id=n.remito_id where r.numero_legal='0016-00002597' and n.texto like '%1.500%' and n.texto like '%migrate_057%'")[0][0] == 1)
f1 = q(A, "select estado, flags_estado from pedidos where id=109")[0]
check(f"#109: entrega COMPLETA (bit 21), sin bit 20, y sigue CUMPLIDO ({f1[0]}); los demas bits no cambian", f1[0] == "CUMPLIDO" and f1[1] & (1 << 21) and not f1[1] & (1 << 20) and (f1[1] & ~(1 << 21)) == (flags0 & ~(1 << 21)))
d = resto(A)
check("nada mas cambia: facturas, remitos, otros pedidos, renglones y los demas renglones de remito", d[0] == antes[0] and d[1] == antes[1] and d[2] == antes[2] and d[3] == antes[3] and d[4] == antes[4])
# la OC cierra: pedido 1.480 / entregado 1.480 / facturado 1.500 - 20 = 1.480
e = create_engine("sqlite:///" + A); S = sessionmaker(bind=e); s = S()
fact = facturado_por_renglon(s, [215]).get(215)
filas = [f for f in _filas_cumplimiento_oc(s, None, "19211", False)]
s.close(); e.dispose()
check(f"OC 19211: facturado bruto 1.500, acreditado 20 -> neto 1.480 {fact}", fact == (1500.0, 20.0))
check(f"Cumplimiento de OC: 1.480 pedidas / 1.480 entregadas / 1.480 facturadas -> CERRADA {[(f['pedido'], f['entregado'], f['facturado'], f['situacion']) for f in filas]}",
      len(filas) == 1 and (filas[0]["pedido"], filas[0]["entregado"], filas[0]["facturado"], filas[0]["a_entregar"], filas[0]["a_facturar"], filas[0]["situacion"]) == (1480.0, 1480.0, 1480.0, 0.0, 0.0, "CERRADA"))
rc2, out2 = correr(A, S057); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '057%'"); con.commit(); con.close()
snap = resto(A); rc3, out3 = correr(A, S057)
check(f"sin el registro: reconoce que el remito ya tiene renglones y no toca nada [{rc3}]", rc3 == 0 and "nada que hacer" in out3 and resto(A) == snap and q(A, "select count(*) from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002597'")[0][0] == 1)

# ---------- guardas ----------
casos = [("el pedido #109 esta anulado", "update pedidos set estado='ANULADO' where id=109"),
         ("la OC del #109 ya no es 19211", "update pedidos set oc='1' where id=109"),
         ("el renglon del pedido ya no pide 1.480", "update pedidos_items set cantidad=1500 where id=215"),
         ("la factura 2597 ya no trae 1.500 en el renglon", "update facturas_items set cantidad=1000 where factura_id in (select id from facturas where numero_comprobante=2597 and tipo_comprobante='FACTURA_A')"),
         ("el CUIT del cliente no es el de Cassara", "update clientes set cuit='20111111112' where id=(select cliente_id from pedidos where id=109)"),
         ("el renglon ya tiene 10 bolsas remitidas en otro remito", "insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) select id, 215, 10, 10 from remitos where numero_legal='0015-00003010'")]
for desc, sql in casos:
    G = copia("test_057_g.db"); con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    s0 = q(G, "select count(*) from remitos_items")[0][0]; fl0 = q(G, "select flags_estado from pedidos where id=109")[0][0]
    rcg, outg = correr(G, S057)
    check(f"guarda: {desc} -> no toca nada, avisa y NO se registra [{rcg}]", rcg == 0 and "AVISO" in outg and q(G, "select count(*) from remitos_items")[0][0] == s0
          and q(G, "select flags_estado from pedidos where id=109")[0][0] == fl0 and not q(G, "select 1 from _migraciones_aplicadas where id like '057%'"))
    os.remove(G)
try: os.remove(A)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
