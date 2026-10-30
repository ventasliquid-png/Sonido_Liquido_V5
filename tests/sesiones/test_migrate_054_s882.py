r"""migrate_054 (S882): Poblet OC 3502 (#97 y remito 0015-3015 anulados, renglones del 0016-2577). Sobre COPIAS de la base de P del 08/10 12:24."""
import sys, os, shutil, sqlite3, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_1224.db"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
S054 = "migrate_054_poblet_oc3502.py"
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
MAXRI = q(ORIG, "select max(id) from remitos_items")[0][0]
def resto(db):
    """lo que la 054 NO debe tocar"""
    return (q(db, "select id, estado, pedido_id, total, flags_estado, notas_auditoria from facturas order by id"),
            q(db, "select id, estado, pedido_id, flags_estado from remitos where numero_legal not in ('0015-00003015') order by id"),
            q(db, "select id, estado, total, flags_estado, nota from pedidos where id not in (97, 82, 58) order by id"),
            q(db, "select id, cantidad from pedidos_items order by id"),
            q(db, "select id, cantidad_remitida from remitos_items where id <= ? order by id", MAXRI),
            q(db, "select count(*) from facturas_items")[0][0])

check("partida: #97 pendiente con remito 0015-3015 de 100; remito 0016-2577 vacio",
      q(ORIG, "select estado from pedidos where id=97")[0][0] == "PENDIENTE" and q(ORIG, "select count(*) from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002577'")[0][0] == 0)

# ---------- 1) aplica ----------
A = copia("test_054_a.db")
antes = resto(A)
rc, out = correr(A, S054)
check(f"corre sin error, hace A y B y se registra [{rc}] {[l for l in out.splitlines() if 'OK --' in l]}",
      rc == 0 and "A: pedido #97 y remito 0015-3015 (Poblet): HECHO" in out and "B: renglones del remito 0016-2577 (pedido #82): HECHO" in out and bool(q(A, "select 1 from _migraciones_aplicadas where id like '054%'")))
# resultados
p97 = q(A, "select estado, flags_estado, nota from pedidos where id=97")[0]
check(f"#97: ANULADO (bit 35 prendido, sin bits 32-34), con nota; su remito 0015-3015 ANULADO con nota",
      p97[0] == "ANULADO" and p97[1] & (1 << 35) and not p97[1] & ((1 << 32) | (1 << 33) | (1 << 34)) and "duplicado" in p97[2]
      and q(A, "select estado from remitos where numero_legal='0015-00003015'")[0][0] == "ANULADO"
      and q(A, "select count(*) from remitos_notas n join remitos r on r.id=n.remito_id where r.numero_legal='0015-00003015' and n.texto like '%Laboratorio de Medicina%'")[0][0] == 1)
r77 = q(A, "select ri.pedido_item_id, ri.cantidad_remitida, ri.cantidad_declarada from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002577' order by ri.pedido_item_id")
check(f"remito 0016-2577 (#82): ahora trae 40 / 80 / 100 enganchados a los renglones 179 / 180 / 181 {r77}", r77 == [(179, 40.0, 40.0), (180, 80.0, 80.0), (181, 100.0, 100.0)])
f82 = q(A, "select flags_estado from pedidos where id=82")[0][0]
check(f"#82: entrega PARCIAL (bit 20, sin bit 21): 100 de 200 bolsas, 80/80 y 40/40 ({bool(f82 & (1<<20))}, {bool(f82 & (1<<21))})", bool(f82 & (1 << 20)) and not f82 & (1 << 21))
check("OC 3502 ahora: #82 = 200 pedidas / 100 entregadas (2577) y el #97 ya no suma; el entregado de la OC es 100, no 200",
      q(A, """select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' join pedidos_items pi on pi.id=ri.pedido_item_id
              join pedidos p on p.id=pi.pedido_id and p.estado!='ANULADO' where p.oc='3502' and pi.producto_id=(select producto_id from pedidos_items where id=181)""")[0][0] == 100.0)
d = resto(A)
check("facturas, renglones de pedido y de factura NO cambian", d[0] == antes[0] and d[3] == antes[3] and d[5] == antes[5])
rc3, out3 = correr(A, S054); check(f"tercera corrida: se saltea [{rc3}]", rc3 == 0 and "SKIP" in out3)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '054%'"); con.commit(); con.close()
snap = resto(A)
rc4, out4 = correr(A, S054)
check(f"sin el registro: las dos partes reconocen que ya estan hechas y no tocan nada [{rc4}]", rc4 == 0 and out4.count(": YA") == 2 and resto(A) == snap)

# ---------- 3) guardas ----------
def guarda(desc, sql, parte, previo=None):
    G = copia("test_054_g.db")
    if previo: correr(G, previo)
    con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    s0 = resto(G); rcg, outg = correr(G, S054); s1 = resto(G)
    linea = [l for l in outg.splitlines() if l.strip().startswith("[migrate_054]   " + parte)]
    check(f"guarda: {desc} -> esa parte queda PENDIENTE y no toca nada [{rcg}] {linea[0].split(': ', 1)[1][:80] if linea else outg[:80]}",
          rcg == 0 and linea and ": PENDIENTE" in linea[0])
    os.remove(G)
guarda("el #97 tiene otro remito vigente", "insert into remitos (id, pedido_id, domicilio_entrega_id, estado, numero_legal, flags_estado) select 'rx1', 97, domicilio_entrega_id, 'BORRADOR', '0015-00009999', 0 from remitos where numero_legal='0015-00003015'", "A:", None)
guarda("el #97 tiene una factura con CAE", "insert into facturas (id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fx1', cliente_id, '97', 'FACTURA_A', 1, 99998, 'AUTORIZADA_AFIP', 1, '77', 3 from pedidos where id=97", "A:")
guarda("el #97 ya no esta pendiente", "update pedidos set estado='FACTURADO' where id=97", "A:")
guarda("la OC del #82 ya no es 3502", "update pedidos set oc='1' where id=82", "A:")
G = copia("test_054_g2.db")
con = sqlite3.connect(G); con.execute("insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) select id, 181, 7, 7 from remitos where numero_legal='0016-00002577'"); con.commit(); con.close()
rcg, outg = correr(G, S054)
check(f"si el remito 2577 ya tiene renglones (cargados a mano) NO los pisa: la parte B figura 'ya' y queda con lo que tenia [{rcg}]",
      rcg == 0 and "B: renglones del remito 0016-2577 (pedido #82): YA" in outg and q(G, "select count(*), sum(cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0016-00002577'")[0] == (1, 7.0))
os.remove(G)
guarda("la factura 2577 ya no dice 100/80/40", "update facturas_items set cantidad=90 where cantidad=100 and factura_id in (select id from facturas where numero_comprobante=2577)", "B:")

for p in (A,):
    try: os.remove(p)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
