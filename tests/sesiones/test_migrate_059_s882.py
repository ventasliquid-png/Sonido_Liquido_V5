r"""migrate_059 (S882, Card #164): corrige las facturas espejo que la ingesta vieja dejo mal (BORRADOR con CAE, Factura B, total = neto), leyendo el PDF guardado en ingesta_facturas_raw.
Sobre COPIAS de la base de P de las 16:21 (con las migraciones 051-058 ya aplicadas por P)."""
import sys, os, shutil, sqlite3, subprocess, glob, json
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.pedidos.cantidades import facturado_por_renglon
from backend.informes.router import _filas_cumplimiento_oc
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_1621.db"   # estado ANTES de la 059 (la copia mas nueva ya la tiene)
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_059_facturas_espejo_desde_raw.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def resto(db):
    return (q(db, "select id, estado, total, tipo_comprobante from facturas where numero_comprobante not in (2614, 2615) order by id"), q(db, "select id, estado, pedido_id, flags_estado from remitos order by id"),
            q(db, "select id, estado, total, flags_estado from pedidos order by id"), q(db, "select id, cantidad from pedidos_items order by id"),
            q(db, "select id, cantidad_remitida from remitos_items order by id"))

check("partida (copia de P de las 16:21): las facturas 2614 y 2615 estan en BORRADOR, FACTURA_B y con el total sin IVA",
      q(ORIG, "select numero_comprobante, tipo_comprobante, estado, round(total,2) from facturas where numero_comprobante in (2614, 2615) order by 1") == [(2614, "FACTURA_B", "BORRADOR", 1854000.0), (2615, "FACTURA_B", "BORRADOR", 263000.0)])
A = copia("test_059_a.db"); antes = resto(A)
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "corregidas 2" in out and "con error 0" in out and "AVISO" not in out)
f = q(A, "select numero_comprobante, tipo_comprobante, estado, fecha_emision, round(neto_gravado,2), round(iva_21,2), round(total,2), cae_vencimiento from facturas where numero_comprobante in (2614, 2615) order by 1")
check(f"2614 y 2615: Factura A, AUTORIZADA_AFIP, fecha del PDF, neto + IVA 21 % = total de ARCA (2.243.340 y 318.230), vencimiento del CAE {f}",
      f == [(2614, "FACTURA_A", "AUTORIZADA_AFIP", "2026-10-08", 1854000.0, 389340.0, 2243340.0, "2026-10-18"), (2615, "FACTURA_A", "AUTORIZADA_AFIP", "2026-10-08", 263000.0, 55230.0, 318230.0, "2026-10-18")])
check("la nota de auditoria conserva la original y suma la marca [SISTEMA]", all("GENERADA POR MODO ESPEJO" in n and "[SISTEMA] Datos fiscales leidos del PDF de ARCA" in n for (n,) in q(A, "select notas_auditoria from facturas where numero_comprobante in (2614, 2615)")))
its = q(A, "select f.numero_comprobante, fi.pedido_item_id, fi.remito_item_id is not null, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante in (2614, 2615) order by 1, fi.id")
check(f"los 5 renglones quedan enlazados a su renglon de pedido y de remito {[(a, b, c) for a, b, c, d in its]}", len(its) == 5 and all(b is not None and c for a, b, c, d in its))
e = create_engine("sqlite:///" + A); s = sessionmaker(bind=e)(); oc = [x for x in _filas_cumplimiento_oc(s, None, None, False) if x["oc"] in ("3713", "5096")]; fb = facturado_por_renglon(s, [b for a, b, c, d in its]); s.close(); e.dispose()
check(f"Cumplimiento de OC: las OC 3713 y 5096 (las de hoy) cierran: ya no figuran 'falta facturar' {[(x['oc'], x['renglon'][:18], x['pedido'], x['facturado'], x['situacion']) for x in oc]}",
      oc and all(x["situacion"] == "CERRADA" for x in oc) and all(fb[b][0] == d for a, b, c, d in its))
check("nada mas cambia: las demas facturas, remitos, pedidos y renglones", resto(A) == antes)
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '059%'"); con.commit(); con.close()
snap = resto(A); rc3, out3 = migrar(A)
check(f"sin el registro: no hay nada que corregir (la marca lo evita) y no toca nada [{rc3}]", rc3 == 0 and "0 factura(s)" in out3 and "corregidas 0" in out3 and resto(A) == snap)
os.remove(A)

# ---------- guardas ----------
casos = [("el registro de ingesta de la 2614 no existe (PROCESADO)", "update ingesta_facturas_raw set audit_status='ERROR' where filename like '%00002614%'", 1, "2614"),
         ("el CAE del PDF no es el de la factura", "update facturas set cae='11111111111111' where numero_comprobante=2615", 1, "2615"),
         ("alguien ya cambio el total de la 2614", "update facturas set total=1000000 where numero_comprobante=2614", 1, "2614"),
         ("la factura 2615 ya esta AUTORIZADA (nada que hacer, no se la cuenta)", "update facturas set estado='AUTORIZADA_AFIP' where numero_comprobante=2615", 1, None)]
for desc, sql, esperadas_saltadas, num in casos:
    G = copia("test_059_g.db"); con = sqlite3.connect(G); con.execute(sql); con.commit(); con.close()
    rcg, outg = migrar(G)
    otra = 2615 if num == "2614" else 2614
    ok_otra = q(G, "select tipo_comprobante, estado from facturas where numero_comprobante=?", otra)[0] == ("FACTURA_A", "AUTORIZADA_AFIP")
    afectada_igual = (num is None) or q(G, "select tipo_comprobante from facturas where numero_comprobante=?", int(num))[0][0] == "FACTURA_B" or "tocó" in desc
    check(f"guarda: {desc} -> esa no se toca ({'avisa' if num else 'solo corrige la otra'}) y la otra si se corrige [{rcg}]",
          rcg == 0 and ok_otra and (num is None or ("AVISO" in outg and f"00001-0000{num}" in outg)) and afectada_igual)
    os.remove(G)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
