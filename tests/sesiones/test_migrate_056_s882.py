r"""migrate_056 (S882): Centro Pet, el pedido #58 es un duplicado creado por la ingesta de la factura 2549. Sobre COPIAS de la base de P del 08/10 12:24."""
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
S056, S051 = "migrate_056_centropet_58_duplicado.py", "migrate_051_remitos_0016_al_pedido_de_su_factura.py"
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def resto(db):
    return (q(db, "select id, estado, pedido_id, total from facturas order by id"), q(db, "select id, estado, pedido_id from remitos order by id"),
            q(db, "select id, estado, total from pedidos where id != 58 order by id"), q(db, "select id, cantidad from pedidos_items order by id"))
A = copia("test_056_a.db")
rc, out = correr(A, S056)
check(f"antes de la 051 (el #58 todavia tiene el remito 0016-2549): no toca nada, avisa y NO se registra [{rc}]",
      rc == 0 and "PENDIENTE" in out and "NO se registra" in out and q(A, "select estado from pedidos where id=58")[0][0] == "PENDIENTE" and not q(A, "select 1 from _migraciones_aplicadas where id like '056%'"))
rc51, o51 = correr(A, S051)
antes = resto(A)
rc2, out2 = correr(A, S056)
p58 = q(A, "select estado, flags_estado, nota from pedidos where id=58")[0]
check(f"despues de la 051 (remito en el #53): anula el #58 con nota y se registra [{rc51}{rc2}] {[l for l in out2.splitlines() if 'OK --' in l]}",
      rc51 == 0 and rc2 == 0 and p58[0] == "ANULADO" and p58[1] & (1 << 35) and not p58[1] & ((1 << 32) | (1 << 33) | (1 << 34)) and "#53" in p58[2] and bool(q(A, "select 1 from _migraciones_aplicadas where id like '056%'")))
check("el #53 y la factura 2549 siguen vigentes; remito 0016-2549 ya en el #53; nada mas cambia (facturas, remitos, otros pedidos, renglones)",
      q(A, "select estado from pedidos where id=53")[0][0] == "PENDIENTE" and q(A, "select estado, pedido_id from facturas where numero_comprobante=2549 and cae is not null")[0] == ("AUTORIZADA_AFIP", "53")
      and q(A, "select pedido_id from remitos where numero_legal='0016-00002549'")[0][0] == 53 and resto(A) == antes)
rc3, out3 = correr(A, S056); check(f"segunda corrida: se saltea [{rc3}]", rc3 == 0 and "SKIP" in out3)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '056%'"); con.commit(); con.close()
snap = resto(A); rc4, out4 = correr(A, S056)
check(f"sin el registro: reconoce que ya esta hecho y no toca nada [{rc4}]", rc4 == 0 and ": YA" in out4 and resto(A) == snap)
def guarda(desc, sql):
    G = copia("test_056_g.db"); correr(G, S051)
    con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    est0 = q(G, "select estado from pedidos where id=58")[0][0]
    rcg, outg = correr(G, S056)
    check(f"guarda: {desc} -> no anula el #58, avisa y NO se registra [{rcg}]", rcg == 0 and "PENDIENTE" in outg and q(G, "select estado from pedidos where id=58")[0][0] == est0 and est0 != "ANULADO" and not q(G, "select 1 from _migraciones_aplicadas where id like '056%'"))
    os.remove(G)
guarda("el #58 ya tiene una factura con CAE", "insert into facturas (id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fx2', cliente_id, '58', 'FACTURA_A', 1, 99997, 'AUTORIZADA_AFIP', 1, '78', 3 from pedidos where id=58")
guarda("el #58 ya no es de 240", "update pedidos_items set cantidad=100 where pedido_id=58")
guarda("el #53 esta anulado", "update pedidos set estado='ANULADO' where id=53")
guarda("el #58 ya no esta pendiente", "update pedidos set estado='FACTURADO' where id=58")
try: os.remove(A)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
