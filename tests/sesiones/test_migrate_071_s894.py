r"""migrate_071 (S894, Carlos 28/10 «1 Ok»; Nike Sello de Oro): los nueve informales cargados como «Consumidor Final + 11111111119» que compran
solo en Rosa pasan a Rosa como Pao Tandil y Ana Robles: CUIT vacío (Adri Nails conserva el suyo), sin condición de IVA, nivel 9, sello (bit 4)
y medalla (bit 19). M&M Odontológicos queda Blanco; DAI y M&M Insumos no se tocan. Sobre una COPIA de la base de P del 28/10 13:13."""
import sys, os, sqlite3, subprocess
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261028_1313.db"
NUEVE = ("ASTRID MANICURA DEVOTO", "Adri Nails Adriana Vaquero", "DAI SALOMÉ", "DELICIA ALDERETES", "Federico Acuario",
         "LILIA MORALES", "LUCIANA FLORENTÍN", "MIRTA ROSSINI", "VLAJEC INSUMOS TATTOO")
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_071_rosa_sin_cuit.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def resto(db):
    marcas = ",".join("?" * len(NUEVE))
    return (q(db, f"select id, cuit, flags_estado, condicion_iva_id, observaciones from clientes where razon_social not in ({marcas}) order by id", *NUEVE),
            q(db, "select id, cliente_id, flags_estado, estado from pedidos order by id"), q(db, "select id, cliente_id from facturas order by id"))

check("partida: los nueve son Consumidor Final con 11111111119 (Adri Nails con su CUIT real) y compran en Rosa",
      all(r[0] in ("11111111119", "27182292368") for r in q(ORIG, f"select cuit from clientes where razon_social in ({','.join('?' * 9)})", *NUEVE)))
A = copia("test_071_a.db"); antes = resto(A)
rc, out = migrar(A)
check(f"corre sin error y pasa los nueve a Rosa [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "a Rosa 9, saltados 0, con error 0" in out)
filas = {n: (c, iva, f) for n, c, iva, f in q(A, f"select razon_social, cuit, condicion_iva_id, flags_estado from clientes where razon_social in ({','.join('?' * 9)})", *NUEVE)}
check("los nueve: CUIT vacío (Adri Nails conserva 27182292368), sin condición de IVA, nivel 9, sello Rosa y medalla",
      all(iva is None and (f & 15) == 9 and f & 16 and f & 524288 and (c is None if n != "Adri Nails Adriana Vaquero" else c == "27182292368")
          for n, (c, iva, f) in filas.items()))
check("cada uno lleva la línea [SISTEMA] con lo que tenía antes", all("[SISTEMA] 28/10/2026 (S894, migrate_071)" in (o or "") and "Antes: CUIT" in (o or "")
      for (o,) in q(A, f"select observaciones from clientes where razon_social in ({','.join('?' * 9)})", *NUEVE)))
check("nada más cambia: los demás clientes (M&M Odontológicos, DAI, M&M Insumos incluidos), los pedidos y las facturas", resto(A) == antes)
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '071%'"); con.commit(); con.close()
snap = q(A, "select id, cuit, flags_estado, condicion_iva_id from clientes order by id")
rc3, out3 = migrar(A)
check(f"sin el registro: los nueve ya no están como se auditó, los saltea y no toca nada [{rc3}]",
      rc3 == 0 and "a Rosa 0, saltados 9" in out3 and q(A, "select id, cuit, flags_estado, condicion_iva_id from clientes order by id") == snap)
os.remove(A)

# ---------- migrate_072: borrado físico de DAI y M&M Insumos (Carlos: «si se puede, eliminemos físicamente DAI solo y M&M Insumos solo») ----------
def migrar072(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_072_borrar_fichas_duplicadas.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def fk(db):
    con = sqlite3.connect(db); v = set(con.execute("pragma foreign_key_check").fetchall()); con.close(); return v
B = copia("test_072_b.db"); migrar(B)
fk_antes = fk(B)
rc, out = migrar072(B)
quedan = sorted(n for (n,) in q(B, "select razon_social from clientes where razon_social in ('DAI', 'DAI SALOMÉ', 'M&M INSUMOS', 'M&M ODONTOLÓGICOS LA PLATA')"))
check(f"072: borra DAI y M&M Insumos (vírgenes, sin pedidos) y deja a DAI Salomé y M&M Odontológicos [{rc}] {quedan}",
      rc == 0 and "borradas 2, saltadas 0, con error 0" in out and quedan == ["DAI SALOMÉ", "M&M ODONTOLÓGICOS LA PLATA"])
check("072: se va el domicilio propio de M&M Insumos (copia) con su vínculo y su enlace; el de M&M Odontológicos queda",
      q(B, "select count(*) from domicilios where id='c9a5b8a21a2a4e2d9a6efde881fcd628'")[0][0] == 0
      and q(B, "select count(*) from vinculos_geograficos where entidad_id='3d314dbe40f445adb6f4f55761ca34f3'")[0][0] == 0
      and q(B, "select count(*) from domicilios where id='b664085f1c0a4b3e92f97d93ba490b56'")[0][0] == 1)
check("072: no aparece ninguna referencia rota nueva (las que había vienen de la tabla vieja domicilios_legacy)", fk(B) <= fk_antes)
rc2, out2 = migrar072(B); check(f"072: segunda corrida, se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
os.remove(B)
C = copia("test_072_c.db")
x_con = sqlite3.connect(C); x_con.execute("update pedidos set cliente_id='64bffd58570446019580b1e68b573210' where id=(select min(id) from pedidos)"); x_con.commit(); x_con.close()
rc, out = migrar072(C)
check(f"072 guarda: si DAI tuviera un pedido, no se borra y avisa [{rc}]", rc == 0 and "AVISO -- DAI" in out
      and q(C, "select count(*) from clientes where id='64bffd58570446019580b1e68b573210'")[0][0] == 1)
os.remove(C)

# la regla de clientes (S894) no se los vuelve a cambiar
G = copia("test_071_g.db"); migrar(G)
from backend.main import app   # carga los modelos
from backend.clientes.models import Cliente
from backend.clientes.service import ClienteService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
eng = create_engine(f"sqlite:///{G}"); s = sessionmaker(bind=eng)()
estables = []
for n in NUEVE:
    c = s.query(Cliente).filter(Cliente.razon_social == n).one(); a = int(c.flags_estado); ClienteService._audit_sovereignty(c); estables.append(int(c.flags_estado) == a)
mm = s.query(Cliente).filter(Cliente.razon_social == "M&M ODONTOLÓGICOS LA PLATA").one(); ClienteService._audit_sovereignty(mm)
check("al recalcular con la regla de clientes los nueve quedan iguales (Rosa estable)", all(estables))
check(f"M&M Odontológicos (queda Blanco, Carlos) pierde la medalla vieja al recalcular ({mm.flags_estado})", not int(mm.flags_estado) & 524288)
s.rollback(); s.close(); eng.dispose()
os.remove(G)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
