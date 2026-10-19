"""backup_semanal.py (S876): corre una vez por semana, consistente con WAL, nunca frena el arranque. Todo en carpetas temporales."""
import sys, os, shutil, sqlite3, tempfile, time, glob, subprocess
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5\scripts")
import backup_semanal as b
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
T = tempfile.mkdtemp(prefix="bk_sem_")
db = os.path.join(T, "data", "V5_LS_MASTER.db"); os.makedirs(os.path.dirname(db))
dest = os.path.join(T, "silo", "BACKUPS_DB", "PRODUCCION_P")
os.makedirs(os.path.dirname(dest))          # el Silo "está montado": existe BACKUPS_DB, la subcarpeta se crea sola
# base en modo WAL con escrituras SIN checkpoint, conexión abierta (como el servidor andando)
con = sqlite3.connect(db); con.execute("pragma journal_mode=wal"); con.execute("pragma wal_autocheckpoint=0")
con.execute("create table pedidos(id integer primary key, n text)")
con.executemany("insert into pedidos(n) values (?)", [(f"p{i}",) for i in range(500)]); con.commit()
check("la base de prueba está en WAL y con -wal sin checkpoint", os.path.exists(db + "-wal") and os.path.getsize(db + "-wal") > 0)
def correr(*extra):
    return b.main(["--db", db, "--destino", dest, *extra])
def copias(): return sorted(glob.glob(os.path.join(dest, "PRODUCCION_P*.db")))

rc = correr(); c1 = copias()
check("sin ningún respaldo previo: sale con 0 y crea uno", rc == 0 and len(c1) == 1)
copia = sqlite3.connect(c1[0]); filas = copia.execute("select count(*) from pedidos").fetchone()[0]; integ = copia.execute("pragma integrity_check").fetchone()[0]; copia.close()
check("la copia trae TODO lo escrito aunque estuviera solo en el WAL (500 filas) e integridad ok", filas == 500 and integ == "ok")
check("no queda ningún .parcial suelto", not glob.glob(os.path.join(dest, "*.parcial")))
check("queda constancia de la última corrida (estado_semanal.json)", os.path.exists(os.path.join(dest, "estado_semanal.json")))
check("el servidor 'sigue andando': la base de origen no se tocó (500 filas, se puede seguir escribiendo)", con.execute("select count(*) from pedidos").fetchone()[0] == 500 and con.execute("insert into pedidos(n) values ('x')") is not None)
con.commit()

time.sleep(1.1)
rc = correr(); check("segunda corrida enseguida: sale con 0 y NO crea otra (hay uno reciente)", rc == 0 and len(copias()) == 1)

viejo = c1[0]; hace8 = time.time() - 8 * 86400; os.utime(viejo, (hace8, hace8))
time.sleep(1.1)
rc = correr(); check("con el último respaldo de 8 días: crea uno nuevo", rc == 0 and len(copias()) == 2)

time.sleep(1.1)
rc = correr("--forzar"); check("--forzar guarda aunque haya uno reciente", rc == 0 and len(copias()) == 3)

# una copia de OF (nombre PRODUCCION_P_al_...) también cuenta como respaldo reciente
shutil.copyfile(copias()[-1], os.path.join(dest, "PRODUCCION_P_al_20260929_1132.db"))
for f in copias(): os.utime(f, (hace8, hace8))
os.utime(os.path.join(dest, "PRODUCCION_P_al_20260929_1132.db"), None)
n0 = len(copias()); rc = correr()
check("una copia hecha desde OF (otro nombre) y reciente alcanza: no crea otra", rc == 0 and len(copias()) == n0)

# Silo no montado -> carpeta local, sin frenar
rc = b.main(["--db", db, "--destino", os.path.join(T, "NO_EXISTE", "x", "PRODUCCION_P"), "--forzar"])
check("Silo no montado: sale con 0 y deja la copia en data/backups_locales", rc == 0 and len(glob.glob(os.path.join(T, "data", "backups_locales", "PRODUCCION_P*.db"))) == 1)

# base inexistente / base corrupta: nunca frena
rc = b.main(["--db", os.path.join(T, "no_hay.db"), "--destino", dest]); check("base inexistente: sale con 0", rc == 0)
malo = os.path.join(T, "corrupta.db"); open(malo, "wb").write(b"esto no es sqlite" * 100)
rc = b.main(["--db", malo, "--destino", dest, "--forzar"]); check("base corrupta: sale con 0 (el error se informa, no se propaga)", rc == 0)
check("la corrupta no dejó basura (.parcial ni copia nueva)", not glob.glob(os.path.join(dest, "*.parcial")))

# como lo llama el lanzador: proceso aparte, código de salida 0
p = subprocess.run([sys.executable, r"C:\dev\Sonido_Liquido_V5\scripts\backup_semanal.py", "--db", db, "--destino", dest], capture_output=True, text=True, encoding="utf-8")
check(f"como proceso (lo que hace el .bat): código {p.returncode} y una línea de estado", p.returncode == 0 and "[BACKUP SEMANAL]" in p.stdout)

con.close(); shutil.rmtree(T, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
