r"""migrate_058 (S882): remito 0016-2562 de Jomax: del pedido #4 (20) al #69 con 10 bolsas. Sobre COPIAS de la base de P del 08/10 12:24."""
import sys, os, shutil, sqlite3, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.informes.router import _filas_cumplimiento_oc
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_1224.db"
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
S058, S051 = "migrate_058_remito_2562_jomax_10.py", "migrate_051_remitos_0016_al_pedido_de_su_factura.py"
def copia(n, previas=("migrate_052_facturas_con_cae_a_autorizada.py",)):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p)
    for s in previas: correr(p, s)
    return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def resto(db):
    return (q(db, "select id, estado, pedido_id, total, flags_estado from facturas order by id"), q(db, "select id, estado, numero_legal, flags_estado from remitos order by id"),
            q(db, "select id, estado, total, flags_estado from pedidos where id not in (4, 69) order by id"), q(db, "select id, cantidad from pedidos_items order by id"),
            q(db, "select id, cantidad_remitida, cantidad_declarada, cantidad_recibida from remitos_items where id != 32 order by id"))

check("partida: el remito 0016-2562 esta en el #4 con 20 bolsas; el #69 (10 bolsas, factura 2562) no tiene remito",
      q(ORIG, "select pedido_id from remitos where numero_legal='0016-00002562'")[0][0] == 4 and q(ORIG, "select pedido_item_id, cantidad_remitida from remitos_items where id=32")[0] == (6, 20.0)
      and not q(ORIG, "select 1 from remitos where pedido_id=69"))
A = copia("test_058_a.db"); rc51, o51 = correr(A, S051)
check("la 051 saltea el 2562 por la discrepancia (remito 20, factura 10)", rc51 == 0 and "0016-00002562: DISCREPANCIA" in o51)
antes = resto(A); f4a = q(A, "select flags_estado from pedidos where id=4")[0][0]; f69a = q(A, "select flags_estado from pedidos where id=69")[0][0]
rc, out = correr(A, S058)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "pasado al pedido #69 con 10 bolsas (declarada 20)" in out and "AVISO" not in out and "ERROR" not in out)
r = q(A, "select pedido_id, estado, numero_legal from remitos where id='10cba68028714c1d8e02e10592085d0e'")[0]
check(f"el remito sigue siendo el 0016-00002562, mismo estado, ahora en el #69 {r}", r == (69, "BORRADOR", "0016-00002562"))
it = q(A, "select pedido_item_id, cantidad_declarada, cantidad_remitida, cantidad_recibida from remitos_items where id=32")[0]
check(f"renglon: enganchado al #122, declarada 20 (el papel), remitida 10, recibida sin cargar {it}", it == (122, 20.0, 10.0, None))
check("nota [SISTEMA] en el remito con el relato", q(A, "select count(*) from remitos_notas where remito_id='10cba68028714c1d8e02e10592085d0e' and texto like '%migrate_058%' and texto like '%10 bolsas%'")[0][0] == 1)
f4, f69 = q(A, "select flags_estado from pedidos where id=4")[0][0], q(A, "select flags_estado from pedidos where id=69")[0][0]
check(f"#69: entrega COMPLETA (bit 21); #4: sin entrega (bits 20 y 21 apagados); el estado de ambos no cambia ({q(A, 'select estado from pedidos where id=4')[0][0]} / {q(A, 'select estado from pedidos where id=69')[0][0]})",
      f69 & (1 << 21) and not f69 & (1 << 20) and not f4 & ((1 << 20) | (1 << 21)) and q(A, "select estado from pedidos where id=4")[0][0] == "FACTURADO" and q(A, "select estado from pedidos where id=69")[0][0] == "PENDIENTE"
      and (f4 & ~((1 << 20) | (1 << 21))) == (f4a & ~((1 << 20) | (1 << 21))) and (f69 & ~((1 << 20) | (1 << 21))) == (f69a & ~((1 << 20) | (1 << 21))))
d = resto(A)
check("nada mas cambia: facturas, otros remitos, otros pedidos, renglones, otros renglones de remito", d == antes)
check("el vinculo factura 2562 - remito 2562 sigue y ahora los dos estan en el mismo pedido", q(A, "select count(*) from facturas_remitos fr join remitos r on r.id=fr.remito_id join facturas f on f.id=fr.factura_id where r.numero_legal='0016-00002562' and f.numero_comprobante=2562 and cast(f.pedido_id as text)=cast(r.pedido_id as text)")[0][0] == 1)
e = create_engine("sqlite:///" + A); s = sessionmaker(bind=e)(); fi = [f for f in _filas_cumplimiento_oc(s, None, None, False) if f["pedido_id"] == 69]; s.close(); e.dispose()
check(f"Cumplimiento de OC (el #69 no tiene OC cargada: se mira por SQL) -- entregado 10 y facturado 10 contra 10 pedidas",
      q(A, "select coalesce(sum(ri.cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' where ri.pedido_item_id=122")[0][0] == 10.0
      and q(A, "select coalesce(sum(fi.cantidad),0) from facturas_items fi join facturas f on f.id=fi.factura_id and f.estado='AUTORIZADA_AFIP' where fi.pedido_item_id=122")[0][0] == 10.0)
rc2, out2 = correr(A, S058); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '058%'"); con.commit(); con.close()
snap = resto(A); rc3, out3 = correr(A, S058)
check(f"sin el registro: reconoce que ya esta hecho y no toca nada [{rc3}]", rc3 == 0 and "nada que hacer" in out3 and resto(A) == snap)

# orden inverso: 058 antes que 051 -> la 051 ya no avisa por el 2562
B = copia("test_058_b.db"); rcb, outb = correr(B, S058); rcb51, ob51 = correr(B, S051)
check(f"si la 058 corre ANTES que la 051, la 051 reconoce el 2562 en el pedido de su factura (sin aviso) [{rcb}{rcb51}]", rcb == 0 and "OK --" in outb and rcb51 == 0 and "2562" not in ob51)
os.remove(B)

# guardas
casos = [("el pedido #69 esta anulado", "update pedidos set estado='ANULADO' where id=69"),
         ("el #69 ya no pide 10 bolsas", "update pedidos_items set cantidad=12 where id=122"),
         ("los renglones #6 y #122 ya no son el mismo producto", "update pedidos_items set producto_id=(select min(id) from productos where id != 175) where id=122"),
         ("el renglon del remito ya tiene cantidad recibida", "update remitos_items set cantidad_recibida=20 where id=32"),
         ("el remito ya no esta en el #4", "update remitos set pedido_id=1 where numero_legal='0016-00002562'"),
         ("el renglon #122 ya tiene otro remito", "insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) select id, 122, 3, 3 from remitos where numero_legal='0016-00002595'"),
         ("la factura 2562 ya no trae 10 en el renglon", "update facturas_items set cantidad=4 where factura_id in (select id from facturas where numero_comprobante=2562 and cae is not null)"),
         ("el CUIT del cliente no es el de Jomax", "update clientes set cuit='20111111112' where id=(select cliente_id from pedidos where id=69)")]
for desc, sql in casos:
    G = copia("test_058_g.db"); con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    p0 = q(G, "select pedido_id from remitos where numero_legal='0016-00002562'")[0][0]; fl0 = q(G, "select flags_estado from pedidos where id=69")[0][0]
    rcg, outg = correr(G, S058)
    check(f"guarda: {desc} -> no toca nada, avisa y NO se registra [{rcg}]", rcg == 0 and "AVISO" in outg and q(G, "select pedido_id from remitos where numero_legal='0016-00002562'")[0][0] == p0
          and q(G, "select flags_estado from pedidos where id=69")[0][0] == fl0 and not q(G, "select 1 from _migraciones_aplicadas where id like '058%'"))
    os.remove(G)
try: os.remove(A)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
