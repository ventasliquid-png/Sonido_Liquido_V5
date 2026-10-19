"""migrate_051 (S882): remitos 0016 al pedido de su factura. Sobre COPIAS de la base de P de hoy (ya con 048, 049 y 050)."""
import sys, os, shutil, sqlite3, glob, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db"   # estado ANTES de las migraciones 051-058 (la copia mas nueva ya las tiene)
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); shutil.copyfile(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_051_remitos_0016_al_pedido_de_su_factura.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def remito(db, n): return q(db, "select id, pedido_id, estado, numero_legal from remitos where numero_legal like ? order by pedido_id", f"0016%{n:08d}")

A = copia("test_051_a.db")
# la base de partida es la real: los 5 casos que describe el informe
check("partida: 0016-2533 en #34, 2538 en #39, 2549 en #58, 2562 en #4 (los remitos NO se movieron con la 050)",
      [remito(A, n)[0][1] for n in (2533, 2538, 2549, 2562)] == [34, 39, 58, 4])
estado0 = {n: remito(A, n) for n in (2533, 2538, 2549, 2562, 2546, 2547, 2576)}
cant0 = q(A, "select sum(cantidad_remitida), count(*) from remitos_items")[0]
nrem0 = q(A, "select count(*), sum(valor_declarado) from remitos")[0]
flags0 = {r[0]: r[1] for r in q(A, "select id, flags_estado from pedidos")}
ped_tot0 = q(A, "select count(*), sum(total), group_concat(estado) from pedidos")[0]
fac0 = q(A, "select count(*), sum(total), group_concat(pedido_id) from facturas")[0]
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "remitos movidos 3" in out and "con error 0" in out)
# los 3 movidos
d = {n: remito(A, n)[0] for n in (2533, 2538, 2549)}
check(f"2533 -> #33, 2538 -> #32, 2549 -> #53 {[d[n][1] for n in (2533, 2538, 2549)]}", [d[n][1] for n in (2533, 2538, 2549)] == [33, 32, 53])
check("numero legal y estado de los movidos NO cambian", all(d[n][2] == estado0[n][0][2] and d[n][3] == estado0[n][0][3] for n in (2533, 2538, 2549)))
for n, pedido in ((2538, 32), (2549, 53)):
    its = q(A, "select ri.cantidad_remitida, pi.pedido_id from remitos_items ri join pedidos_items pi on pi.id=ri.pedido_item_id where ri.remito_id=?", d[n][0])
    check(f"{n}: el renglon quedo enganchado a un renglon de SU pedido nuevo (#{pedido}) con la misma cantidad {its}", its and all(i[1] == pedido for i in its))
check("las cantidades remitidas y la cantidad de renglones no cambian (suma y cuenta)", q(A, "select sum(cantidad_remitida), count(*) from remitos_items")[0] == cant0)
check("la cantidad de remitos y el valor declarado no cambian", q(A, "select count(*), sum(valor_declarado) from remitos")[0] == nrem0)
check("queda una nota [SISTEMA] en cada remito movido", all(q(A, "select count(*) from remitos_notas where remito_id=? and texto like '%migrate_051%'", d[n][0])[0][0] == 1 for n in (2533, 2538, 2549)))
# bits
fl = {r[0]: r[1] for r in q(A, "select id, flags_estado from pedidos")}
B20, B21 = 1 << 20, 1 << 21
check(f"#32 y #53 quedan con entrega COMPLETA (bit 21) y sin bit 20: {bool(fl[32] & B21)}, {bool(fl[53] & B21)}", bool(fl[32] & B21) and bool(fl[53] & B21) and not (fl[32] & B20) and not (fl[53] & B20))
check("#39 y #58 (perdieron la entrega) quedan sin bits 20 ni 21", not (fl[39] & (B20 | B21)) and not (fl[58] & (B20 | B21)))
otros = [p for p in flags0 if p not in (32, 33, 34, 39, 53, 58) and flags0[p] != fl[p]]
check(f"ningun OTRO pedido cambia de flags ({otros})", not otros)
check("los pedidos no cambian (cantidad, total, estados) ni las facturas", q(A, "select count(*), sum(total), group_concat(estado) from pedidos")[0] == ped_tot0 and q(A, "select count(*), sum(total), group_concat(pedido_id) from facturas")[0] == fac0)
# los que NO se tocan
check("2562 (remito 20 vs factura 10) queda en el pedido #4, intacto", remito(A, 2562) == estado0[2562] and "DISCREPANCIA" in out and "20" in out)
check("2576 (factura registrada 2 veces): los dos remitos intactos", remito(A, 2576) == estado0[2576] and "registrada 2 veces" in out)
check("2546 y 2547 (remito y factura apuntan al MISMO pedido inexistente, #44 y #51): intactos", remito(A, 2546) == estado0[2546] and remito(A, 2547) == estado0[2547])
check("hay exactamente 3 avisos (2562 y los dos de la 2576) y 35 remitos ya correctos", out.count("AVISO") == 3 and "saltados 3" in out and "factura 35" in out)
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '051%'"); con.commit(); con.close()
rc3, out3 = migrar(A)
check(f"sin el registro: los 3 movidos ya estan en su pedido (38 correctos), no se mueve nada {[l for l in out3.splitlines() if 'OK --' in l]}", rc3 == 0 and "remitos movidos 0" in out3 and "estaban en el pedido de su factura 38" in out3)

# ---- guardas ----
B = copia("test_051_b.db")
con = sqlite3.connect(B)
con.execute("update pedidos set cliente_id=(select id from clientes where id != (select cliente_id from pedidos where id=32) limit 1) where id=32")        # (a) otro cliente
con.execute("update remitos_items set cantidad_remitida=3 where remito_id=(select id from remitos where numero_legal like '0016%00002549')")                # (c) remito != factura
con.commit(); con.close()
rcB, outB = migrar(B)
check(f"guardas: (a) cliente distinto y (c) remito distinto de la factura -> el 2538 y el 2549 se SALTAN, solo se mueve el 2533 {[l for l in outB.splitlines() if 'OK --' in l]}",
      rcB == 0 and "remitos movidos 1" in outB and remito(B, 2538)[0][1] == 39 and remito(B, 2549)[0][1] == 58 and remito(B, 2533)[0][1] == 33)
C = copia("test_051_c.db")
con = sqlite3.connect(C)
it53 = con.execute("select id from pedidos_items where pedido_id=53").fetchone()[0]
rid_prev = con.execute("select id from remitos where numero_legal like '0015%' limit 1").fetchone()[0]
con.execute("insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) values (?, ?, 100, 100)", (rid_prev, it53))      # (b) el pedido destino ya tiene entrega previa
con.commit(); con.close()
rcC, outC = migrar(C)
check("guarda: si el pedido destino quedaria con mas remitido que pedido, el 2549 se SALTA", rcC == 0 and remito(C, 2549)[0][1] == 58 and "quedaria con mas remitido" in outC)

for p in (A, B, C):
    try: os.remove(p)
    except Exception: pass
falla = [d_ for d_, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d_) for d_ in falla]
sys.exit(1 if falla else 0)
