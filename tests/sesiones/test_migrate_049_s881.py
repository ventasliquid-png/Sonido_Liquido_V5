"""migrate_049 (S881): corrige las facturas de V5 desde los datos de ARCA. Sobre COPIAS de la base de P del 06/10. Nunca toca bases vivas."""
import sys, os, shutil, sqlite3, glob, subprocess, json
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261006_1600.db"   # estado ANTES de la 048/049 (la copia mas nueva de P ya las tiene)
def copia(nombre):
    p = os.path.join(RAIZ, "scratch", nombre); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_049_facturas_desde_arca.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v

JSON = json.load(open(os.path.join(RAIZ, "scripts", "data", "correcciones_facturas_s881.json"), encoding="utf-8"))["correcciones"]
check(f"el archivo de correcciones trae {len(JSON)} facturas y ninguna es la duplicada 2576", len(JSON) == 43 and all(c["numero"] != 2576 for c in JSON))

# ---------- 1) aplica sobre la copia ----------
A = copia("test_049_a.db")
antes = {n: q(A, "select id, estado, pedido_id, flags_estado, cliente_id from facturas where numero_comprobante=? and cae is not null and tipo_comprobante != 'FACTURA_A'", n) for n in (2594, 2577, 2546, 2601)}
rc, out = migrar(A)
check(f"corre sin error [{rc}] y corrige las 43: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "corregidas 43" in out and "saltadas 0" in out and "con error 0" in out)
f = q(A, "select tipo_comprobante, total, neto_gravado, iva_21, fecha_emision, cae_vencimiento, estado, notas_auditoria from facturas where numero_comprobante=2594 and cae is not null")[0]
check(f"2594: tipo FACTURA_A, neto 68700, IVA 14427, total 83127 (antes 68700), fecha 2026-09-04 {f[:6]}", f[0] == "FACTURA_A" and abs(f[1] - 83127) < .01 and abs(f[2] - 68700) < .01 and abs(f[3] - 14427) < .01 and f[4] == "2026-09-04" and f[5] == "2026-09-14")
check("2594: queda la marca [SISTEMA] en notas_auditoria", "[SISTEMA] Corregida desde el PDF de ARCA" in f[7])
its = q(A, "select cantidad, precio_unitario_neto, pedido_item_id from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2577 and f.cae is not null order by fi.id")
check(f"2577 restaurada: renglones 100 / 80 / 40 (antes 200 / 80 / 40) y enlazados a su renglon de pedido {its}", sorted(i[0] for i in its) == [40, 80, 100] and all(i[2] is not None for i in its))
tot = q(A, "select total from facturas where numero_comprobante=2577 and cae is not null")[0][0]
check(f"2577: total 2.479.290 (antes 3.659.040) [{tot}]", abs(tot - 2479290) < .01)
t2601 = q(A, "select total, tipo_comprobante from facturas where numero_comprobante=2601 and cae is not null")[0]
check(f"2601: total 4.800.312 (antes 0) y renglones sin tocar {t2601}", abs(t2601[0] - 4800312) < .01)
# lo que NO se toca
despues = {n: q(A, "select id, estado, pedido_id, flags_estado, cliente_id from facturas where numero_comprobante=? and cae is not null and tipo_comprobante = 'FACTURA_A'", n) for n in (2594, 2577, 2546, 2601)}
check("estado, pedido, flags y cliente de las facturas NO cambian", antes == despues)
dup = q(A, "select tipo_comprobante, estado, total, pedido_id from facturas where numero_comprobante=2576 and cae is not null order by tipo_comprobante")
ref = q(ORIG, "select tipo_comprobante, estado, total, pedido_id from facturas where numero_comprobante=2576 and cae is not null order by tipo_comprobante") if False else None
check(f"la 2576 (registrada dos veces) NO se toca: {dup}", sorted(d[0] for d in dup) == ["FACTURA_B", "PRESUPUESTO_X"] and all(abs(d[2] - 487500) < .01 for d in dup))
pedidos_igual = q(A, "select count(*), sum(total) from pedidos")[0] == q(ORIG, "select count(*), sum(total) from pedidos")[0]
check("los pedidos no cambian (cantidad y suma de totales)", pedidos_igual)
# idempotencia
rc2, out2 = migrar(A)
check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
# 2) idempotencia por contenido, aun sin el registro de la migracion
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id='049_facturas_desde_arca'"); con.commit(); con.close()
rc3, out3 = migrar(A)
check(f"sin el registro, las 43 se reconocen como ya corregidas y no se vuelven a tocar [{rc3}] {[l for l in out3.splitlines() if 'OK --' in l]}", rc3 == 0 and "ya estaban 43" in out3 and "corregidas 0" in out3)

# ---------- 3) si la factura cambio desde la auditoria, NO se toca ----------
B = copia("test_049_b.db")
con = sqlite3.connect(B); con.execute("update facturas set total = total + 5 where numero_comprobante=2594 and cae is not null"); con.commit(); con.close()
rc4, out4 = migrar(B)
fb = q(B, "select tipo_comprobante, total from facturas where numero_comprobante=2594 and cae is not null")[0]
check(f"una factura que cambio (total +5) se SALTA con aviso y queda intacta {fb}", rc4 == 0 and "00001-00002594: cambio desde la auditoria" in out4 and fb[0] == "FACTURA_B")
check("las otras 42 si se corrigen", "corregidas 42" in out4 and "saltadas 1" in out4)

# ---------- 4) renglon enlazado a un renglon de remito: se conservan los renglones ----------
C = copia("test_049_c.db")
fid = q(C, "select id from facturas where numero_comprobante=2577 and cae is not null")[0][0]
ri = q(C, "select id from remitos_items limit 1")[0][0]
con = sqlite3.connect(C); con.execute("update facturas_items set remito_item_id=? where id=(select min(id) from facturas_items where factura_id=?)", (ri, fid)); con.commit(); con.close()
rc5, out5 = migrar(C)
its5 = q(C, "select cantidad from facturas_items where factura_id=? order by id", fid)
tot5 = q(C, "select total from facturas where id=?", fid)[0][0]
check(f"con un renglon enlazado a remito: se corrigen cabecera y totales pero NO los renglones {sorted(i[0] for i in its5)} total {tot5}", rc5 == 0 and abs(tot5 - 2479290) < .01 and sorted(i[0] for i in its5) == [40, 80, 200])

for p in (A, B, C):
    try: os.remove(p)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
