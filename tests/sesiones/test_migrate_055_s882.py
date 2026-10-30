r"""migrate_055 (S882): registra las facturas 2500, 2529, 2582 y 2607 en su pedido y las NC 72 y 73 sobre la 2597. Sobre COPIAS de la base de P del 08/10 12:24 (con la 052 aplicada)."""
import sys, os, shutil, sqlite3, subprocess, json, csv, io, re
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.pedidos.cantidades import facturado_por_renglon
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
SCR = r"C:\Users\Carlos\AppData\Local\Temp\claude\E--Backup-PreWin11\78f9e817-31bc-4751-a881-e0b91a3d502c\scratchpad"
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_1224.db"
def copia(n, con052=True):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p)
    if con052: correr(p, "migrate_052_facturas_con_cae_a_autorizada.py")
    return p
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
S055 = "migrate_055_facturas_aceptadas_y_nc_cassara.py"
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def fact(db, ids):
    e = create_engine("sqlite:///" + db); s = sessionmaker(bind=e)(); v = facturado_por_renglon(s, ids); s.close(); e.dispose(); return v
def resto(db):
    return (q(db, "select id, estado, pedido_id, total from facturas where numero_comprobante is null or numero_comprobante not in (2500, 2529, 2531, 2582, 2607, 72, 73) order by id"),
            q(db, "select id, estado, pedido_id, flags_estado from remitos order by id"),
            q(db, "select id, estado, total, flags_estado, nota from pedidos order by id"),
            q(db, "select id, cantidad from pedidos_items order by id"))

D = json.load(open(os.path.join(RAIZ, "scripts", "data", "registro_facturas_nc_s882.json"), encoding="utf-8"))
REG, NCS = D["registrar"], D["notas_credito"]
check("el archivo trae 5 facturas (2500, 2529, 2531, 2582, 2607) y 2 notas de credito (72 y 73)", [r["numero"] for r in REG] == [2500, 2529, 2531, 2582, 2607] and [n["numero"] for n in NCS] == [72, 73])
rows = list(csv.reader(io.StringIO(open(os.path.join(SCR, "arca_csv", "arca_emitidos.csv"), encoding="utf-8-sig").read()), delimiter=";")); h = rows[0]
f = lambda x: float(x.replace(".", "").replace(",", ".")) if x else 0.0
ARCA = {(int(x[2]), int(x[3]), x[5], x[1]): (f(x[h.index("Imp. Total")]), f(x[h.index("Imp. Neto Gravado Total")]), f(x[h.index("Total IVA")]), x[0]) for x in rows[1:] if x}
ok = all(ARCA[(r["pv"], r["numero"], r["cae"], "1")][0] == r["totales"]["total"] and ARCA[(r["pv"], r["numero"], r["cae"], "1")][3] == r["fecha"] and abs(ARCA[(r["pv"], r["numero"], r["cae"], "1")][1] - r["totales"]["neto_gravado"] - r["totales"]["exento"]) < .01 for r in REG)
ok &= all(ARCA[(n["pv"], n["numero"], n["cae"], "3")][0] == n["totales"]["total"] and ARCA[(n["pv"], n["numero"], n["cae"], "3")][3] == n["fecha"] and abs(ARCA[(n["pv"], n["numero"], n["cae"], "3")][1] - n["totales"]["neto_gravado"]) < .01 for n in NCS)
check("los datos de las 7 coinciden con el CSV oficial de ARCA (total, neto, fecha y CAE)", ok)

# ---------- 1) aplica ----------
A = copia("test_055_a.db")
antes = resto(A); n0 = q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0]
rc, out = correr(A, S055)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "facturas registradas 5, notas de credito 2" in out and "saltadas 0" in out and "con error 0" in out)
check(f"facturas con CAE: {n0} -> +7 (5 facturas + 2 NC)", q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0] == n0 + 7)
for r in REG:
    fila = q(A, "select tipo_comprobante, estado, pedido_id, total, neto_gravado, iva_21, fecha_emision, cae_vencimiento, flags_estado from facturas where numero_comprobante=? and cae=?", r["numero"], r["cae"])
    t = r["totales"]
    check(f"{r['numero']}: Factura A autorizada en el pedido #{r['pedido_id']}, total {t['total']:,.0f}, con la nota [SISTEMA] {fila[0][:3] if fila else None}",
          fila and fila[0][0] == "FACTURA_A" and fila[0][1] == "AUTORIZADA_AFIP" and fila[0][2] == r["pedido_id"] and abs(fila[0][3] - t["total"]) < .01 and abs(fila[0][4] - t["neto_gravado"]) < .01 and abs(fila[0][5] - t["iva_21"]) < .01
          and "[SISTEMA] Registrada" in q(A, "select notas_auditoria from facturas where numero_comprobante=? and cae=?", r["numero"], r["cae"])[0][0])
    its = q(A, "select fi.pedido_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=? and f.cae=? order by fi.id", r["numero"], r["cae"])
    check(f"{r['numero']}: {len(its)} renglon(es) enlazados a renglones de SU pedido",
          len(its) == len(r["items"]) and all(i[0] is not None and q(A, "select pedido_id from pedidos_items where id=?", i[0])[0][0] == int(r["pedido_id"]) for i in its))
# efecto en los pedidos (mismo codigo que usa la pantalla)
v94 = fact(A, [174]); rem94 = q(A, "select coalesce(sum(ri.cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' where ri.pedido_item_id=174")[0][0]
check(f"#94: 120 pedidas / {rem94:g} entregadas / {v94.get(174, (0, 0))[0]:g} facturadas -> cierra", v94.get(174) == (120.0, 0.0) and rem94 == 120.0)
v31 = fact(A, [i for i, in q(A, 'select id from pedidos_items where pedido_id=31')])
ped31 = {i: c for i, c in q(A, "select id, cantidad from pedidos_items where pedido_id=31")}
check(f"#31 (2529 + 2531 = $602.580 = el total del pedido): cada renglon queda facturado completo {[(i, ped31[i], v31.get(i, (0, 0))[0]) for i in sorted(ped31)]}",
      all(abs(v31.get(i, (0, 0))[0] - c) < 1e-6 for i, c in ped31.items()) and len(ped31) == 4)
# NC
fn = q(A, "select numero_comprobante, tipo_comprobante, estado, pedido_id, total, flags_estado from facturas where tipo_comprobante='NOTA_CREDITO_A' and numero_comprobante in (72, 73) order by numero_comprobante")
check(f"NC 72 y 73: NOTA_CREDITO_A autorizadas, en el pedido #109, con el bit ES_NC (19) {[(x[0], x[4]) for x in fn]}",
      [(x[0], x[1], x[2], x[3], x[4]) for x in fn] == [(72, "NOTA_CREDITO_A", "AUTORIZADA_AFIP", "109", 34727.0), (73, "NOTA_CREDITO_A", "AUTORIZADA_AFIP", "109", 968000.0)] and all(x[5] & (1 << 19) for x in fn))
aj = q(A, "select n.numero_comprobante, f.numero_comprobante, a.monto_aplicado from facturas_ajustes a join facturas n on n.id=a.factura_nc_nd_id join facturas f on f.id=a.factura_ajustada_id order by n.numero_comprobante")
check(f"facturas_ajustes: las dos NC apuntan a la 2597 por su importe {aj}", [(x[0], x[1]) for x in aj] == [(72, 2597), (73, 2597)] and [x[2] for x in aj] == [34727.0, 968000.0])
check("la 2597 queda con el bit TIENE_NC (17)", q(A, "select flags_estado from facturas where numero_comprobante=2597 and tipo_comprobante='FACTURA_A'")[0][0] & (1 << 17))
v109 = fact(A, [215])
check(f"renglon #215 del #109: 1500 facturadas - 20 acreditadas = 1480 neto = lo pedido ({v109.get(215)}); la NC 73 (adelanto) no toca cantidades",
      v109.get(215) == (1500.0, 20.0) and q(A, "select cantidad from pedidos_items where id=215")[0][0] == 1480.0)
d = resto(A)
check("el resto no cambia: pedidos (estado, total, flags), remitos, renglones y las demas facturas", d == antes)
# idempotencia
rc2, out2 = correr(A, S055); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '055%'"); con.commit(); con.close()
rc3, out3 = correr(A, S055)
check(f"sin el registro: los 7 ya estaban, no se duplica nada [{rc3}]", rc3 == 0 and "ya estaban 7" in out3 and "facturas registradas 0, notas de credito 0" in out3 and q(A, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0] == n0 + 7
      and q(A, "select count(*) from facturas_ajustes")[0][0] == 2)

# ---------- 2) guardas ----------
casos = [("el pedido #29 esta anulado (2500)", "update pedidos set estado='ANULADO' where id=29", "saltadas 1", 2500),
         ("el CUIT del cliente del #31 no es el de las facturas (2529 y 2531, las dos del #31)", "update clientes set cuit='20111111112' where id=(select cliente_id from pedidos where id=31)", "saltadas 2", 2529),
         ("el #94 ya esta cubierto por otra factura (2582)", "insert into facturas (id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, total, cae, flags_estado) select 'fk1', cliente_id, '94', 'FACTURA_A', 1, 99991, 'AUTORIZADA_AFIP', 1684320, '1', 3 from pedidos where id=94", "saltadas 1", 2582),
         ("un renglon de la 2607 no es del pedido #117 (error en el archivo simulado)", "update pedidos_items set pedido_id=1 where id=226", "con error 1", 2607)]
for desc, sql, esperado, num in casos:
    G = copia("test_055_g.db"); con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    rcg, outg = correr(G, S055)
    check(f"guarda: {desc} -> solo lo afectado se salta/falla, el resto entra [{rcg}] ({esperado})",
          rcg == 0 and esperado in outg and q(G, "select count(*) from facturas where numero_comprobante=? and cae is not null", num)[0][0] == 0
          and q(G, "select count(*) from facturas where cae is not null and trim(cae)!=''")[0][0] == n0 + 7 - (2 if "saltadas 2" == esperado else 1) + (1 if "fk1" in sql else 0))
    os.remove(G)
G = copia("test_055_g.db"); con = sqlite3.connect(G); con.execute("update facturas_items set cantidad=10 where factura_id in (select id from facturas where numero_comprobante=2597 and tipo_comprobante='FACTURA_A')"); con.commit(); con.close()
rcg, outg = correr(G, S055)
check(f"guarda: la 2597 solo tiene 10 en el renglon -> la NC 72 (20 bolsas) se SALTA, la NC 73 (solo importe) entra [{rcg}]",
      rcg == 0 and "saltadas 1" in outg and "NC 00001-00000072" in outg and q(G, "select count(*) from facturas where tipo_comprobante='NOTA_CREDITO_A' and numero_comprobante=72")[0][0] == 0
      and q(G, "select count(*) from facturas where tipo_comprobante='NOTA_CREDITO_A' and numero_comprobante=73")[0][0] == 1)
os.remove(G)
G = copia("test_055_g.db"); con = sqlite3.connect(G); con.execute("update facturas set estado='ANULADA' where numero_comprobante=2597 and tipo_comprobante='FACTURA_A'"); con.commit(); con.close()
rcg, outg = correr(G, S055)
check(f"guarda: la 2597 esta anulada -> las dos NC se saltan, las 5 facturas entran [{rcg}]", rcg == 0 and "saltadas 2" in outg and "facturas registradas 5, notas de credito 0" in outg)
os.remove(G)

# ---------- 3) auditoria posterior ----------
env = dict(os.environ, PYTHONIOENCODING="utf-8"); sal = os.path.join(SCR, "ensayo_049", "auditoria_055.xlsx"); os.makedirs(os.path.dirname(sal), exist_ok=True)
r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "auditoria_facturas.py"), "--db", A, "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\OF", "--pdf", r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\P",
                    "--arca-csv", os.path.join(SCR, "arca_csv", "arca_emitidos.csv"), "--salida", sal], capture_output=True, text=True, encoding="utf-8", env=env)
m_ok = re.search(r"OK: (\d+)", r.stdout); m_dif = re.search(r"DIFERENCIAS: (\d+)", r.stdout)
print("   auditoria posterior:", m_ok.group(0) if m_ok else "?", "|", m_dif.group(0) if m_dif else "?")
import openpyxl
filas = list(openpyxl.load_workbook(sal, read_only=True)["FACTURAS"].iter_rows(values_only=True))[1:]
nuevas_dif = sorted(x[1] for x in filas if str(x[0]).startswith("DIFERENCIAS") and x[1] in ("00001-00000072", "00001-00002582", "00001-00002500", "00001-00002529", "00001-00002531", "00001-00002607", "00001-00000073"))
check(f"la auditoria posterior: las unicas 'diferencias' entre lo recien registrado son las dos intencionales: la NC 72 (PDF: 1 renglon de importe; V5: 20 bolsas) y la 2582 (PDF: precio de lista; V5: precio neto bonificado) {nuevas_dif}; OK sube a {m_ok.group(1) if m_ok else '?'}",
      nuevas_dif == ["00001-00000072", "00001-00002582"] and m_ok and int(m_ok.group(1)) >= 62)

try: os.remove(A)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
