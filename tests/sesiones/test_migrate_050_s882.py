"""migrate_050 (S882): registra en V5 las facturas emitidas con pedido ALTA y corrige enlaces. Sobre COPIAS de la base de P del 08/10 (ya con 048 y 049)."""
import sys, os, shutil, sqlite3, glob, subprocess, json, csv, io, re
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
SCR = r"C:\Users\Carlos\AppData\Local\Temp\claude\E--Backup-PreWin11\78f9e817-31bc-4751-a881-e0b91a3d502c\scratchpad"
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_0929.db"   # estado ANTES de la 050 (con 048 y 049); la copia mas nueva ya tiene la 050
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_050_facturas_a_pedidos.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v

D = json.load(open(os.path.join(RAIZ, "scripts", "data", "asignacion_facturas_s882.json"), encoding="utf-8"))
REG, ENL = D["registrar"], D["enlaces"]
check(f"el archivo trae {len(REG)} facturas a registrar y {len(ENL)} enlaces; ninguna es la duplicada 2576", len(REG) == 20 and len(ENL) == 4 and all(r["numero"] != 2576 for r in REG + ENL))
# CSV oficial de ARCA
txt = open(os.path.join(SCR, "arca_csv", "arca_emitidos.csv"), encoding="utf-8-sig").read(); rows = list(csv.reader(io.StringIO(txt), delimiter=";")); h = rows[0]
f = lambda x: float(x.replace(".", "").replace(",", ".")) if x else 0.0
ARCA = {(int(x[2]), int(x[3]), x[5]): (f(x[h.index("Imp. Total")]), f(x[h.index("Imp. Neto Gravado Total")]), f(x[h.index("Total IVA")]), x[0]) for x in rows[1:] if x and x[1] == "1"}
ok_arca = all((r["pv"], r["numero"], r["cae"]) in ARCA and abs(ARCA[(r["pv"], r["numero"], r["cae"])][0] - r["totales"]["total"]) < .01
              and abs(ARCA[(r["pv"], r["numero"], r["cae"])][1] - r["totales"]["neto_gravado"] - r["totales"]["exento"]) < .01
              and ARCA[(r["pv"], r["numero"], r["cae"])][3] == r["fecha"] for r in REG)
check("los datos a registrar coinciden con el CSV oficial de ARCA (total, neto y fecha) en las 20", ok_arca)

# ---------- 1) aplica ----------
A = copia("test_050_a.db")
n0 = q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0]
peds0 = q(A, "select count(*), sum(total), group_concat(estado) from pedidos")[0]
flags0 = q(A, "select group_concat(flags_estado) from pedidos")[0][0]
remitos0 = q(A, "select count(*), sum(valor_declarado) from remitos")[0]
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "registradas 20" in out and "enlaces corregidos 4" in out and "saltadas 0" in out and "con error 0" in out)
n1 = q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0]
check(f"facturas con CAE: {n0} -> {n1} (+20)", n1 == n0 + 20)
r0 = REG[0]
fila = q(A, "select tipo_comprobante, estado, total, neto_gravado, iva_21, fecha_emision, cae_vencimiento, pedido_id, flags_estado, cuit_comprador, notas_auditoria from facturas where numero_comprobante=? and cae=?", r0["numero"], r0["cae"])[0]
check(f"{r0['numero']}: Factura A, AUTORIZADA_AFIP, total {r0['totales']['total']}, pedido {r0['pedido_id']}, flags 3, con marca [SISTEMA] {fila[:9]}",
      fila[0] == "FACTURA_A" and fila[1] == "AUTORIZADA_AFIP" and abs(fila[2] - r0["totales"]["total"]) < .01 and str(fila[7]) == r0["pedido_id"] and fila[8] == 3 and "[SISTEMA] Registrada" in fila[10])
cl = q(A, "select c.cuit from facturas f join clientes c on c.id=f.cliente_id where f.numero_comprobante=? and f.cae=?", r0["numero"], r0["cae"])[0][0]
check("el cliente de la factura es el del pedido (mismo CUIT que el PDF)", re.sub(r"\D", "", cl or "") == r0["cuit"])
con_items = [r for r in REG if r["items"]]
bien = 0
for r in con_items:
    its = q(A, "select fi.cantidad, fi.pedido_item_id from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=? and f.cae=?", r["numero"], r["cae"])
    pi_ok = all(i[1] is not None and q(A, "select pedido_id from pedidos_items where id=?", i[1])[0][0] == int(r["pedido_id"]) for i in its)
    if len(its) == len(r["items"]) and pi_ok: bien += 1
check(f"las {len(con_items)} con renglones: cada renglon queda enlazado a un renglon de SU pedido ({bien}/{len(con_items)})", bien == len(con_items))
sin = [r for r in REG if not r["items"]]
check(f"las {len(sin)} sin renglones quedan con cabecera y totales, y lo dicen en la nota", all(q(A, "select count(*) from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=? and f.cae=?", r["numero"], r["cae"])[0][0] == 0
      and "Renglones NO cargados" in q(A, "select notas_auditoria from facturas where numero_comprobante=? and cae=?", r["numero"], r["cae"])[0][0] for r in sin))
# enlaces
bien_e = 0
for e in ENL:
    pid = q(A, "select pedido_id from facturas where numero_comprobante=? and cae=?", e["numero"], e["cae"])[0][0]
    its = q(A, "select pedido_item_id from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=? and f.cae=?", e["numero"], e["cae"])
    if str(pid) == e["pedido_nuevo"] and all(i[0] is None or q(A, "select pedido_id from pedidos_items where id=?", i[0])[0][0] == int(e["pedido_nuevo"]) for i in its): bien_e += 1
check(f"los 4 enlaces: la factura y sus renglones pasan al pedido correcto ({bien_e}/4)", bien_e == 4)
# lo que NO se toca
check("los pedidos no cambian (cantidad, suma de totales, estados)", q(A, "select count(*), sum(total), group_concat(estado) from pedidos")[0] == peds0)
check("los bits de los pedidos no cambian", q(A, "select group_concat(flags_estado) from pedidos")[0][0] == flags0)
check("los remitos no cambian", q(A, "select count(*), sum(valor_declarado) from remitos")[0] == remitos0)
check("la 2576 (duplicada) no se toca", q(A, "select count(*) from facturas where numero_comprobante=2576 and cae is not null")[0][0] == 2)
# idempotencia
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id='050_facturas_a_pedidos'"); con.commit(); con.close()
rc3, out3 = migrar(A)
check(f"sin el registro: las 20 ya estaban y los 4 enlaces tambien, no se duplica nada {[l for l in out3.splitlines() if 'OK --' in l]}", rc3 == 0 and "registradas 0" in out3 and "ya estaban 24" in out3)
check("sigue habiendo +20 facturas, no +40", q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0] == n0 + 20)

# ---------- 2) guardas ----------
B = copia("test_050_b.db")
r1 = REG[1]
con = sqlite3.connect(B)
# (a) el pedido ya cubierto por otra factura vigente
con.execute("insert into facturas (id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fake1', cliente_id, ?, 'FACTURA_A', 1, 99999, 'AUTORIZADA_AFIP', ?, '11111111111111', 3 from pedidos where id=?",
            (r1["pedido_id"], r1["pedido_total"], int(r1["pedido_id"])))
# (b) el CUIT del cliente del pedido no coincide
r2 = REG[2]
con.execute("update clientes set cuit='99999999999' where id=(select cliente_id from pedidos where id=?)", (int(r2["pedido_id"]),))
# (c) pedido anulado
r3 = REG[3]
con.execute("update pedidos set estado='ANULADO' where id=?", (int(r3["pedido_id"]),))
# (d) la factura del enlace ya no esta en el pedido auditado
e0 = ENL[0]
con.execute("update facturas set pedido_id='7' where numero_comprobante=? and cae=?", (e0["numero"], e0["cae"]))
con.commit(); con.close()
rcB, outB = migrar(B)
avisos = [l for l in outB.splitlines() if "AVISO" in l]
check(f"guardas: (a) pedido ya cubierto, (b) CUIT distinto, (c) pedido anulado, (d) enlace ya movido -> las 4 se SALTAN con aviso {len(avisos)}", rcB == 0 and "saltadas 4" in outB and "registradas 17" in outB and "enlaces corregidos 3" in outB)
check("las saltadas no crean nada", all(q(B, "select count(*) from facturas where numero_comprobante=? and cae=?", r["numero"], r["cae"])[0][0] == 0 for r in (r1, r2, r3)))
check("la factura del enlace movido a mano queda en el pedido 7", str(q(B, "select pedido_id from facturas where numero_comprobante=? and cae=?", e0["numero"], e0["cae"])[0][0]) == "7")

# ---------- 3) la auditoria posterior ----------
env = dict(os.environ, PYTHONIOENCODING="utf-8")
sal = os.path.join(SCR, "ensayo_049", "auditoria_050.xlsx"); os.makedirs(os.path.dirname(sal), exist_ok=True)
r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "auditoria_facturas.py"), "--db", A, "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\OF", "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\P",
                    "--arca-csv", os.path.join(SCR, "arca_csv", "arca_emitidos.csv"), "--salida", sal], capture_output=True, text=True, encoding="utf-8", env=env)
m_ok = re.search(r"OK: (\d+)", r.stdout); m_dif = re.search(r"DIFERENCIAS: (\d+)", r.stdout)
check(f"auditoria posterior: {m_ok.group(1) if m_ok else '?'} OK (antes 40; +17 con renglones) y {m_dif.group(1) if m_dif else '?'} con diferencias (3 viejas + las 3 sin renglones)",
      m_ok and int(m_ok.group(1)) == 57 and m_dif and int(m_dif.group(1)) == 6)

for p in (A, B):
    try: os.remove(p)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
