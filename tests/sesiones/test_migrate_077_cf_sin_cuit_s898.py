r"""S898, H21 (Carlos 03/11: «H21, solo máscara»). Regla de oro de Nike del 28/10: el CUIT comodín del Consumidor Final (11111111119) vive solo en el comprobante, nunca en la ficha. La ficha nueva de
la S897 lo guardaba; desde la S898 es solo una máscara de la pantalla y la ficha de un Consumidor Final guarda el CUIT vacío. migrate_077 deja con el CUIT vacío a los clientes que lo tenían guardado
(en P: M&M Odontológicos La Plata y Elizabeth Paola Roca) sin tocar nada más. Sobre una COPIA de la base de P del 02/11 16:40 (estado previo a la migración); el arranque de P la aplica con auto_migrar."""
import sys, os, sqlite3, subprocess, hashlib
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261102_1640.db"
MM, ROCA, MOSTRADOR = "3bb357cb3dec47dfad9de11da889aae7", "126ed0545e3543b2879a6be69a4e3832", "9bdd804555df48909f95f3a453df3f2f"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(db, sql, *a):
    con = sqlite3.connect(db); con.execute(sql, a); con.commit(); con.close()
def correr(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_077_cf_sin_cuit_comodin.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def huella(db, sql, *a):
    return hashlib.md5(repr(q(db, sql, *a)).encode("utf-8")).hexdigest()
CLI_SIN_CUIT = "select id, razon_social, cuit, condicion_iva_id, flags_estado, activo from clientes where id not in (?, ?) order by id"
FILA = "select razon_social, cuit, condicion_iva_id, flags_estado, activo from clientes where id=?"

# ---------- partida ----------
a = copia("t077_a.db")
CF = q(a, "select id from condiciones_iva where upper(nombre) like '%CONSUMIDOR FINAL%'")[0][0]
check("partida: M&M Odontológicos y Roca son Consumidor Final con el 11111111119 guardado; el Mostrador tiene el 00000000000",
      q(a, FILA, MM)[0][1:3] == ("11111111119", CF) and q(a, FILA, ROCA)[0][1:3] == ("11111111119", CF) and q(a, FILA, MOSTRADOR)[0][1] == "00000000000")
antes_mm, antes_roca = q(a, FILA, MM)[0], q(a, FILA, ROCA)[0]
h_otros, h_ped, h_rem, h_fac = (huella(a, CLI_SIN_CUIT, MM, ROCA), huella(a, "select * from pedidos order by id"), huella(a, "select * from remitos order by id"),
                                huella(a, "select * from facturas order by id"))
# una ficha con el 11111111119 pero con OTRA condición de IVA: no se toca
otro = q(a, "select id from clientes where id not in (?, ?, ?) and condicion_iva_id is not null and condicion_iva_id != ? limit 1", MM, ROCA, MOSTRADOR, CF)[0][0]
x(a, "update clientes set cuit='11111111119' where id=?", otro)
h_otros = huella(a, CLI_SIN_CUIT, MM, ROCA)

# ---------- migrate_077 ----------
rc, out = correr(a)
check(f"la migración corre y sale 0 [{rc}]; informa las dos fichas y se registra", rc == 0 and out.count("OK --") == 2 and "M&M ODONTOL" in out.upper() and "ROCA" in out.upper()
      and q(a, "select count(*) from _migraciones_aplicadas where id='077_cf_sin_cuit_comodin'")[0][0] == 1)
check("las dos fichas quedan con el CUIT vacío (NULL, como los demás clientes sin CUIT) y siguen Consumidor Final, con los mismos bits y activas",
      q(a, FILA, MM)[0] == (antes_mm[0], None, antes_mm[2], antes_mm[3], antes_mm[4]) and q(a, FILA, ROCA)[0] == (antes_roca[0], None, antes_roca[2], antes_roca[3], antes_roca[4]))
check("el Mostrador conserva el 00000000000 y un cliente con el 11111111119 pero otra condición de IVA no se toca; ningún otro cliente cambió",
      q(a, FILA, MOSTRADOR)[0][1] == "00000000000" and q(a, "select cuit from clientes where id=?", otro)[0][0] == "11111111119" and huella(a, CLI_SIN_CUIT, MM, ROCA) == h_otros)
check("los pedidos (#15, #19, #102 de M&M y #149 de Roca), los remitos y las facturas quedan idénticos",
      huella(a, "select * from pedidos order by id") == h_ped and huella(a, "select * from remitos order by id") == h_rem and huella(a, "select * from facturas order by id") == h_fac)
rc2, out2 = correr(a)
check(f"idempotente: la segunda corrida se saltea por el registro [{rc2}]", rc2 == 0 and "SKIP" in out2 and q(a, FILA, MM)[0][1] is None)
x(a, "delete from _migraciones_aplicadas where id='077_cf_sin_cuit_comodin'")
x(a, "update clientes set cuit='11111111119' where id=?", MM)
rc3, out3 = correr(a)
check("y sin el registro, con una ficha que volvió a tener el comodín, la deja vacía de nuevo (una sola ficha) y no toca nada más",
      rc3 == 0 and out3.count("OK --") == 1 and q(a, FILA, MM)[0][1] is None and q(a, "select cuit from clientes where id=?", otro)[0][0] == "11111111119")

# ---------- el arranque de P la descubre ----------
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
disp = dict(auto_migrar.migraciones_disponibles())
check("auto_migrar (el arranque de P) descubre la 077 con su nombre de archivo", disp.get("077_cf_sin_cuit_comodin", "").endswith("migrate_077_cf_sin_cuit_comodin.py"))
for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("t077_"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
