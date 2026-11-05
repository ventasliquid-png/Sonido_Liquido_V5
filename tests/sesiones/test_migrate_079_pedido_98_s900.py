r"""S900, Card #215 (Carlos 05/11: «el bit del 98, ¿no lo podés agregar a mano?»). migrate_079 reconstruye en el pedido #98 su reapertura (que se hizo antes de que el sistema registrara las salidas de
Cumplido): prende el bit 50 (FUE_REABIERTO) y agrega UNA línea [SISTEMA] que cuenta lo ocurrido y aclara que se escribió después del hecho. Solo si el #98 sigue como se auditó. Sobre COPIAS de la base
de P: la del 05/11 10:21 (el #98 Cumplido con ajuste y su remito 3043 anulado) y la del 04/11 16:28 (el #98 todavía Cumplido limpio); el arranque de P la aplica con auto_migrar."""
import sys, os, sqlite3, subprocess, hashlib
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
FIJAS = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS"
ORIG = FIJAS + r"\PRODUCCION_P_al_20261105_1021.db"
ORIG_LIMPIO = FIJAS + r"\PRODUCCION_P_al_20261104_1628.db"
B34, B35, B46, B50 = 1 << 34, 1 << 35, 1 << 46, 1 << 50
SCRIPT = "migrate_079_pedido_98_reapertura_reconstruida.py"
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
MARCA = "[SISTEMA] Reapertura reconstruida el "
RESTO = {"pedidos (menos el #98)": "select * from pedidos where id != 98 order by id", "renglones": "select * from pedidos_items order by id", "remitos": "select * from remitos order by id",
         "facturas": "select id, pedido_id, numero_comprobante, total, flags_estado from facturas order by id"}

# ---------- partida: el #98 como lo dejó el 05/11 ----------
a = copia(ORIG, "t079_a.db")
e0, f0, n0 = q(a, "select estado, flags_estado, nota from pedidos where id=98")[0]
check("partida: el #98 está CUMPLIDO con el bit 46 (cierre con ajuste), sin el bit 50 y con la nota del cierre «pedido 80.0, entregado 20.0» de las 10:16",
      e0 == "CUMPLIDO" and f0 & B34 and f0 & B46 and not f0 & B50 and "pedido 80.0, entregado 20.0" in n0 and "2026-11-05 10:16" in n0 and MARCA not in n0)
r43 = q(a, "select estado, flags_estado from remitos where numero_legal='0015-00003043' and pedido_id=98")
check("partida: su remito 0015-00003043 está ANULADO", r43 and ((r43[0][0] or "").upper() == "ANULADO" or int(r43[0][1]) & B35))
antes = {k: huella(a, s) for k, s in RESTO.items()}

# ---------- la migración ----------
rc, out = correr(a)
e1, f1, n1 = q(a, "select estado, flags_estado, nota from pedidos where id=98")[0]
check(f"migrate_079 sale 0, dice que corrigió el #98 y se registra [{rc}]", rc == 0 and "OK -- pedido #98" in out and "079_pedido_98_reapertura_reconstruida registrada (corregido)" in out
      and q(a, "select count(*) from _migraciones_aplicadas where id='079_pedido_98_reapertura_reconstruida'")[0][0] == 1)
check("el #98 queda con el bit 50 prendido y TODO lo demás igual: sigue CUMPLIDO, los flags son los de antes más el bit 50 (el 46 sigue), el estado no cambió",
      e1 == "CUMPLIDO" and f1 == f0 | B50 and f1 & B46 and f1 & B34)
check("la nota conserva todo lo anterior y suma UNA línea [SISTEMA]: la reapertura reconstruida, con los datos del caso y la aclaración de que se escribió después del hecho",
      n1.startswith(n0) and n1.count(MARCA) == 1 and "0015-00003043" in n1 and "04/11/2026 (16:27)" in n1 and "05/11/2026 a las 10:16" in n1 and "pedido 80, entregado 20" in n1
      and "entre el 04/11 16:28 y el 05/11 10:16" in n1 and "Línea escrita después del hecho" in n1 and "bit 50" in n1 and "migrate_079" in n1)
check("ningún otro pedido, renglón, remito ni factura cambió", all(huella(a, s) == antes[k] for k, s in RESTO.items()))
check("el pedido conserva su estado, su total y su fecha (solo cambiaron los flags y la nota)",
      q(a, "select estado, total, fecha from pedidos where id=98") == [(e0, *q(ORIG, "select total, fecha from pedidos where id=98")[0])])

# ---------- idempotente ----------
rc2, out2 = correr(a)
check(f"segunda corrida: SKIP, sin cambios [{rc2}]", rc2 == 0 and "SKIP" in out2 and q(a, "select flags_estado, nota from pedidos where id=98") == [(f1, n1)])
x(a, "delete from _migraciones_aplicadas where id='079_pedido_98_reapertura_reconstruida'")
rc3, out3 = correr(a)
check(f"aunque se borre el registro, el criterio de estado la frena: «ya tiene el bit 50», sin duplicar la línea [{rc3}]",
      rc3 == 0 and "ya tiene el bit 50" in out3 and q(a, "select flags_estado, nota from pedidos where id=98") == [(f1, n1)] and "registrada (ya estaba)" in out3)

# ---------- el #98 no está como se auditó ----------
b = copia(ORIG_LIMPIO, "t079_b.db")
fb, nb = q(b, "select flags_estado, nota from pedidos where id=98")[0]
rcb, outb = correr(b)
check(f"con el #98 todavía Cumplido limpio (copia del 04/11 16:28) no se toca: avisa «no está como se auditó» y se registra para no repetirse [{rcb}]",
      rcb == 0 and "AVISO" in outb and "no esta como se audito" in outb and q(b, "select flags_estado, nota from pedidos where id=98") == [(fb, nb)] and "registrada (saltado)" in outb)
c = copia(ORIG, "t079_c.db"); x(c, "update pedidos set flags_estado = flags_estado & ? where id=98", ~B46 & ((1 << 62) - 1))
rcc, outc = correr(c)
check(f"sin el bit 46 tampoco: no se toca [{rcc}]", rcc == 0 and "no esta como se audito" in outc and not q(c, "select flags_estado from pedidos where id=98")[0][0] & B50)
d = copia(ORIG, "t079_d.db"); x(d, "update remitos set estado='EN_CAMINO', flags_estado = flags_estado & ? where numero_legal='0015-00003043'", ~B35 & ((1 << 62) - 1))
rcd, outd = correr(d)
check(f"con el remito 3043 sin anular tampoco: no se toca [{rcd}]", rcd == 0 and "no esta como se audito" in outd and not q(d, "select flags_estado from pedidos where id=98")[0][0] & B50)

# ---------- otras bases ----------
vacia = os.path.join(RAIZ, "scratch", "t079_vacia.db")
try: os.remove(vacia)
except OSError: pass
con = sqlite3.connect(vacia); con.execute("create table pedidos (id integer primary key, estado text, flags_estado integer, nota text)")
con.execute("create table remitos (id integer primary key, pedido_id integer, numero_legal text, estado text, flags_estado integer)"); con.commit(); con.close()
rce, oute = correr(vacia)
check(f"en una base sin el #98 (la de D, la de B) informa y se registra sin tocar nada [{rce}]", rce == 0 and "no esta en esta base" in oute and "registrada (saltado)" in oute)
sinrem = os.path.join(RAIZ, "scratch", "t079_sin_remitos.db")
try: os.remove(sinrem)
except OSError: pass
con = sqlite3.connect(sinrem); con.execute("create table pedidos (id integer primary key, estado text, flags_estado integer, nota text)"); con.commit(); con.close()
rcf, outf = correr(sinrem)
check(f"en una base a medio armar (sin la tabla remitos) avisa y NO se registra: se reintenta en el próximo arranque [{rcf}]",
      rcf == 0 and "falta la tabla 'remitos'" in outf and q(sinrem, "select count(*) from _migraciones_aplicadas where id='079_pedido_98_reapertura_reconstruida'")[0][0] == 0)

# ---------- auto_migrar ----------
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
disp = dict(auto_migrar.migraciones_disponibles())
aplicadas = {row[0] for row in q(ORIG, "select id from _migraciones_aplicadas")}
pend = sorted(m for m in disp if m >= "070" and m not in aplicadas)
check("auto_migrar (el arranque de P) descubre la 079 y, sobre la base de P del 05/11 10:21, es la única migración pendiente de la serie 07x",
      pend == ["079_pedido_98_reapertura_reconstruida"] and disp["079_pedido_98_reapertura_reconstruida"].endswith(SCRIPT))
check("y va después de la 078 en el orden en que las corre", [m for m in sorted(disp, key=lambda m: os.path.basename(disp[m])) if m >= "078"] == ["078_facturas_no_se_cargan", "079_pedido_98_reapertura_reconstruida"])

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("t079_"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d_ for d_, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d_) for d_ in falla]
sys.exit(1 if falla else 0)
