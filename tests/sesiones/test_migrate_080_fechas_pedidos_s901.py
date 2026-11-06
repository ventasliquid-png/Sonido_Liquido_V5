r"""S901, H27 + mapa del flujo documental (Card #217 F4; Carlos 06/11: «sí a la migración de fechas»). migrate_080 corrige la fecha de los dos pedidos de la base de produccion que nacieron de una
factura por la Ingesta clasica y quedaron con la fecha de CARGA: el #153 (Medi Cient: factura 2612 del 06/10, pedido del 03/11) y el #155 (Doc Baires: factura 2603 del 16/09, pedido del 05/11).
Les pone la fecha de la factura (a las 00:00) y UNA linea [SISTEMA] con la fecha anterior; no toca nada mas (ni estado, flags, total, renglones, remitos, facturas, otros pedidos); solo si cada uno sigue como
se audito. Sobre COPIAS de la base de P: la del 06/11 15:55 (los dos como se auditaron, con la 079 ya aplicada) y la del 05/11 10:21 (el #155 todavia no existia); el arranque de P la aplica con auto_migrar."""
import sys, os, sqlite3, subprocess, hashlib
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
FIJAS = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS"
ORIG = FIJAS + r"\desde_S901\PRODUCCION_P_al_20261106_1555.db"   # en una subcarpeta: varias pruebas viejas toman la copia MAS NUEVA de FIJAS por nombre (glob) y esperan la del 05/11
ANTES = FIJAS + r"\PRODUCCION_P_al_20261105_1021.db"
B38, B39 = 1 << 38, 1 << 39
SCRIPT = "migrate_080_fechas_pedidos_nacidos_de_factura.py"
MID = "080_fechas_pedidos_nacidos_de_factura"
def copia(origen, n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(origen, p); return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(db, sql, *a):
    con = sqlite3.connect(db); con.execute(sql, a); con.commit(); con.close()
def correr(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", SCRIPT)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def huella(db, sql, *a):
    return hashlib.md5(repr(q(db, sql, *a)).encode("utf-8")).hexdigest()
def ped(db, pid): return q(db, "select fecha, estado, flags_estado, total, nota from pedidos where id=?", pid)[0]
MARCA = "[SISTEMA] Fecha corregida el "
RESTO = {"pedidos (menos #153 y #155)": "select * from pedidos where id not in (153, 155) order by id", "renglones": "select * from pedidos_items order by id", "remitos": "select * from remitos order by id",
         "facturas": "select * from facturas order by id", "vinculos": "select * from facturas_remitos order by id"}

# ---------- partida: los dos como los dejo la carga ----------
a = copia(ORIG, "t080_a.db")
p153, p155 = ped(a, 153), ped(a, 155)
check("partida: el #153 (Medi Cient) nació de una factura (bit 38), no es retroactivo y lleva la fecha de CARGA 03/11/2026 12:06",
      p153[2] & B38 and not p153[2] & B39 and p153[0].startswith("2026-11-03 12:06") and MARCA not in p153[4])
check("partida: el #155 (Doc Baires) nació de una factura (bit 38), no es retroactivo y lleva la fecha de CARGA 05/11/2026 10:28",
      p155[2] & B38 and not p155[2] & B39 and p155[0].startswith("2026-11-05 10:28") and MARCA not in p155[4])
check("partida: sus facturas son la 2612 (06/10/2026) y la 2603 (16/09/2026), vinculadas por los remitos de cada pedido",
      q(a, "select count(*) from facturas f join facturas_remitos fr on fr.factura_id=f.id join remitos r on r.id=fr.remito_id where r.pedido_id=153 and f.numero_comprobante=2612 and f.fecha_emision like '2026-10-06%'")[0][0] == 1
      and q(a, "select count(*) from facturas f join facturas_remitos fr on fr.factura_id=f.id join remitos r on r.id=fr.remito_id where r.pedido_id=155 and f.numero_comprobante=2603 and f.fecha_emision like '2026-09-16%'")[0][0] == 1)
rem0 = q(a, "select id, fecha_creacion, fecha_emision, fecha_salida from remitos where pedido_id in (153, 155) order by id")
antes = {k: huella(a, s) for k, s in RESTO.items()}

# ---------- la migración ----------
rc, out = correr(a)
n153, n155 = ped(a, 153), ped(a, 155)
check(f"migrate_080 sale 0, corrige los dos pedidos y se registra [{rc}]", rc == 0 and "OK -- pedido #153" in out and "OK -- pedido #155" in out and f"{MID} registrada (2 corregidos)" in out
      and q(a, "select count(*) from _migraciones_aplicadas where id=?", MID)[0][0] == 1)
check("el #153 queda con la fecha de la factura 06/10/2026 a las 00:00 (el formato de contra natura) y el #155 con la del 16/09/2026",
      n153[0] == "2026-10-06 00:00:00.000000" and n155[0] == "2026-09-16 00:00:00.000000")
check("lo demás de los dos pedidos igual: estado, flags (el bit 38 sigue, sin bit 39), total",
      n153[1:4] == p153[1:4] and n155[1:4] == p155[1:4])
check("la nota conserva todo lo anterior y suma UNA línea [SISTEMA] con la fecha anterior, el número y la fecha de la factura y la aclaración de que los remitos conservan la suya",
      n153[4].startswith(p153[4]) and n153[4].count(MARCA) == 1 and "factura 2612 del 06/10/2026" in n153[4] and "(03/11/2026 12:06)" in n153[4] and "migrate_080" in n153[4] and "Los remitos conservan su fecha" in n153[4]
      and n155[4].startswith(p155[4]) and n155[4].count(MARCA) == 1 and "factura 2603 del 16/09/2026" in n155[4] and "(05/11/2026 10:28)" in n155[4])
check("ningún otro pedido, renglón, remito (ni sus fechas), factura ni vínculo cambió", all(huella(a, s) == antes[k] for k, s in RESTO.items())
      and q(a, "select id, fecha_creacion, fecha_emision, fecha_salida from remitos where pedido_id in (153, 155) order by id") == rem0)

# ---------- idempotente ----------
rc2, out2 = correr(a)
check(f"segunda corrida: SKIP, sin cambios [{rc2}]", rc2 == 0 and "SKIP" in out2 and ped(a, 153) == n153 and ped(a, 155) == n155)
x(a, "delete from _migraciones_aplicadas where id=?", MID)
rc3, out3 = correr(a)
check(f"aunque se borre el registro, el criterio de estado la frena: «ya lleva la fecha de la factura», sin duplicar la línea [{rc3}]",
      rc3 == 0 and out3.count("ya lleva la fecha de la factura") == 2 and ped(a, 153) == n153 and ped(a, 155) == n155 and f"{MID} registrada (0 corregidos)" in out3)

# ---------- no está como se auditó: no se toca ----------
b = copia(ORIG, "t080_b.db"); x(b, "update pedidos set flags_estado = flags_estado & ? where id=153", ~B38 & ((1 << 62) - 1))
rcb, outb = correr(b)
check(f"el #153 sin el bit 38 (no nació de una factura) no se toca, y el #155 sí se corrige [{rcb}]",
      rcb == 0 and "AVISO -- el pedido #153 no esta como se audito" in outb and ped(b, 153)[0] == p153[0] and ped(b, 155)[0] == "2026-09-16 00:00:00.000000")
c = copia(ORIG, "t080_c.db"); x(c, "update pedidos set flags_estado = flags_estado | ? where id=155", B39)
rcc, outc = correr(c)
check(f"el #155 retroactivo (bit 39) no se toca [{rcc}]", rcc == 0 and "AVISO -- el pedido #155 no esta como se audito" in outc and ped(c, 155)[0] == p155[0] and ped(c, 155)[4] == p155[4] and ped(c, 153)[0] == "2026-10-06 00:00:00.000000")
d = copia(ORIG, "t080_d.db"); x(d, "update facturas set numero_comprobante = 9999 where numero_comprobante = 2603")
rcd, outd = correr(d)
check(f"si la factura no es la auditada (otro número) no se toca el #155 [{rcd}]", rcd == 0 and "AVISO -- el pedido #155 no esta como se audito" in outd and ped(d, 155) == p155)
e = copia(ORIG, "t080_e.db"); x(e, "update pedidos set fecha = '2026-11-04 09:00:00.000000' where id=153")
rce, oute = correr(e)
check(f"si la fecha de carga ya no es la auditada (alguien la tocó) no se toca [{rce}]", rce == 0 and "AVISO -- el pedido #153 no esta como se audito" in oute and ped(e, 153)[0] == "2026-11-04 09:00:00.000000")

# ---------- la base anterior (el #155 todavía no existía) ----------
f = copia(ANTES, "t080_f.db")
rcf, outf = correr(f)
check(f"con la copia del 05/11 10:21 el #153 se corrige y del #155 dice que no está en esta base [{rcf}]",
      rcf == 0 and "OK -- pedido #153" in outf and "el pedido #155 no esta en esta base" in outf and ped(f, 153)[0] == "2026-10-06 00:00:00.000000" and f"{MID} registrada (1 corregido)" in outf)

# ---------- otras bases ----------
vacia = os.path.join(RAIZ, "scratch", "t080_vacia.db")
try: os.remove(vacia)
except OSError: pass
con = sqlite3.connect(vacia)
con.execute("create table pedidos (id integer primary key, fecha text, flags_estado integer, nota text)")
con.execute("create table facturas (id text primary key, pedido_id text, numero_comprobante integer, fecha_emision text)")
con.execute("create table facturas_remitos (id text primary key, factura_id text, remito_id text)")
con.execute("create table remitos (id text primary key, pedido_id integer)"); con.commit(); con.close()
rcg, outg = correr(vacia)
check(f"en una base sin esos pedidos (la de D, la de B) informa y se registra sin tocar nada [{rcg}]", rcg == 0 and outg.count("no esta en esta base") == 2 and f"{MID} registrada (0 corregidos)" in outg)
sinfac = os.path.join(RAIZ, "scratch", "t080_sin_facturas.db")
try: os.remove(sinfac)
except OSError: pass
con = sqlite3.connect(sinfac); con.execute("create table pedidos (id integer primary key, fecha text, flags_estado integer, nota text)"); con.commit(); con.close()
rch, outh = correr(sinfac)
check(f"en una base a medio armar (sin la tabla facturas) avisa y NO se registra: se reintenta en el próximo arranque [{rch}]",
      rch == 0 and "falta la tabla 'facturas'" in outh and q(sinfac, "select count(*) from _migraciones_aplicadas where id=?", MID)[0][0] == 0)

# ---------- auto_migrar ----------
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
disp = dict(auto_migrar.migraciones_disponibles())
aplicadas = {row[0] for row in q(ORIG, "select id from _migraciones_aplicadas")}
pend = sorted(m for m in disp if m >= "070" and m not in aplicadas)
check("auto_migrar (el arranque de P) descubre la 080 y, sobre la base de P del 06/11 15:55, es la única migración pendiente de la serie 07x/08x",
      pend == [MID] and disp[MID].endswith(SCRIPT))
check("y va después de la 079 en el orden en que las corre", [m for m in sorted(disp, key=lambda m: os.path.basename(disp[m])) if m >= "078"] == ["078_facturas_no_se_cargan", "079_pedido_98_reapertura_reconstruida", MID])

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("t080_"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d_ for d_, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d_) for d_ in falla]
sys.exit(1 if falla else 0)
