r"""S890, paquete 1 de remitos: migrate_064 (empresas_transporte.web_retiro) y migrate_065 (el remito 0015-00003031 de Petroplastic igual al papel), sobre COPIAS
CRUDAS de la base de P (sin _esquema_p: la migración tiene que agregar la columna sola). Casos: el camino normal, la idempotencia, la 065 antes que la 064, Cruz del Sur
todavía sin cargar (no se registra: se reintenta), y una base donde el 3031 es de otro cliente (la numeración de D es otra: no toca nada)."""
import sys, os, shutil, sqlite3, glob, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
M064 = os.path.join(RAIZ, "scripts", "migrate_064_empresas_transporte_web_retiro.py")
M065 = os.path.join(RAIZ, "scripts", "migrate_065_remito_3031_petroplastic.py")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261021_1206.db"   # [S891] fija: la prueba parte de P ANTES de la 064/065 (el 3031 de mostrador, sin webs de retiro); desde el 21/10 noche P ya las tiene
TMP = os.path.join(RAIZ, "scratch", "test_migrate_064_065"); os.makedirs(TMP, exist_ok=True)
def copia(nombre):
    p = os.path.join(TMP, nombre); shutil.copyfile(ORIG, p); return p
def correr(script, db):
    env = dict(os.environ, DATABASE_URL=f"sqlite:///{db}", PYTHONIOENCODING="utf-8")
    r = subprocess.run([PY, "-X", "utf8", script], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout + r.stderr
def q(db, sql, *a):
    con = sqlite3.connect(db); r = con.execute(sql, a).fetchall(); con.close(); return r
def registrada(db, mid): return bool(q(db, "select 1 from _migraciones_aplicadas where id=?", mid))
CRUZ = "30556565798"

# ---- camino normal: 064 y después 065
db = copia("normal.db")
check("setup: la copia de P tiene a Cruz del Sur (CUIT 30556565798, cargada por Tomy el 21/10) y el 3031 MOSTRADOR/ENTREGADO sin transporte",
      any("".join(ch for ch in str(c or "") if ch.isdigit()) == CRUZ for (c,) in q(db, "select cuit from empresas_transporte"))
      and q(db, "select metodo_entrega, estado, transporte_id from remitos where numero_legal='0015-00003031'") == [("MOSTRADOR", "ENTREGADO", None)])
rc, out = correr(M064, db)
cols = {r[1]: r[2] for r in q(db, "pragma table_info(empresas_transporte)")}
check(f"064: agrega empresas_transporte.web_retiro (VARCHAR(255), NULL) y se registra [rc {rc}]", rc == 0 and cols.get("web_retiro") == "VARCHAR(255)" and registrada(db, "064_empresas_transporte_web_retiro"))
check("064: no carga ninguna web (todas en NULL)", q(db, "select count(*) from empresas_transporte where web_retiro is not null")[0][0] == 0)
rc, out = correr(M064, db)
check(f"064 otra vez: SKIP [rc {rc}]", rc == 0 and "SKIP" in out)
antes_notas = q(db, "select count(*) from remitos_notas")[0][0]
rc, out = correr(M065, db)
r = q(db, """select r.metodo_entrega, r.estado, t.cuit, r.domicilio_entrega_id = p.domicilio_entrega_id, r.bultos, r.valor_declarado, substr(r.fecha_salida,1,16)
             from remitos r join pedidos p on p.id=r.pedido_id left join empresas_transporte t on t.id=r.transporte_id where r.numero_legal='0015-00003031'""")[0]
check(f"065: el 3031 queda transporte de terceros con Cruz del Sur, domicilio del pedido, EN_CAMINO, 200 bultos, $ 2.980.000 [rc {rc}] -> {r}",
      rc == 0 and r[0] == "FLETE_TERCERO" and r[1] == "EN_CAMINO" and "".join(ch for ch in r[2] if ch.isdigit()) == CRUZ and r[3] == 1 and r[4] == 200 and r[5] == 2980000.0)
check(f"065: la fecha de salida no se toca (20/10 14:28, el día en que tomó número): {r[6]}", r[6] == "2026-10-20 14:28")
nota = q(db, "select texto, autor_id from remitos_notas r where remito_id=(select id from remitos where numero_legal='0015-00003031') order by id desc limit 1")[0]
check("065: deja UNA nota [SISTEMA] con lo de antes, lo de después y dónde está la imagen", q(db, "select count(*) from remitos_notas")[0][0] == antes_notas + 1
      and nota[0].startswith("[SISTEMA] Remito alineado con el papel (S890, migrate_065)") and "Junin_copia.pdf" in nota[0] and "Celtrap" in nota[0] and nota[1] is None)
check("065: carga la web de retiro de Cruz del Sur", q(db, "select web_retiro from empresas_transporte where replace(replace(cuit,'-',''),' ','')=?", CRUZ) == [("https://www.cruzdelsur.com/herramientas_retiro.php",)])
check("065: se registra", registrada(db, "065_remito_3031_petroplastic"))
check("065: no toca ningún otro remito (los demás siguen igual que en la copia original)",
      q(db, "select count(*) from remitos where numero_legal<>'0015-00003031'") == q(ORIG, "select count(*) from remitos where numero_legal<>'0015-00003031'")
      and q(db, "select sum(coalesce(bultos,0)), count(transporte_id) from remitos where numero_legal<>'0015-00003031'") == q(ORIG, "select sum(coalesce(bultos,0)), count(transporte_id) from remitos where numero_legal<>'0015-00003031'"))
rc, out = correr(M065, db)
check(f"065 otra vez: SKIP, sin otra nota [rc {rc}]", rc == 0 and "SKIP" in out and q(db, "select count(*) from remitos_notas")[0][0] == antes_notas + 1)

# ---- la 065 antes que la 064 (sin la columna): alinea el remito y saltea la web
db = copia("sin064.db")
rc, out = correr(M065, db)
check(f"065 sin la columna web_retiro: alinea el 3031 igual y no rompe [rc {rc}]", rc == 0 and q(db, "select metodo_entrega from remitos where numero_legal='0015-00003031'") == [("FLETE_TERCERO",)]
      and "web_retiro" not in {r[1] for r in q(db, "pragma table_info(empresas_transporte)")})

# ---- Cruz del Sur todavía sin cargar: no toca nada y NO se registra
db = copia("sincruz.db")
con = sqlite3.connect(db); con.execute("delete from empresas_transporte where replace(replace(cuit,'-',''),' ','')=?", (CRUZ,)); con.commit(); con.close()
rc, out = correr(M065, db)
check(f"sin Cruz del Sur en el padrón: no toca el 3031 y NO se registra (se reintenta en el próximo arranque) [rc {rc}]", rc == 0 and "AVISO" in out
      and q(db, "select metodo_entrega from remitos where numero_legal='0015-00003031'") == [("MOSTRADOR",)] and not registrada(db, "065_remito_3031_petroplastic"))

# ---- base donde el 3031 es de otro cliente (en D la numeración es otra)
db = copia("otro.db")
con = sqlite3.connect(db); con.execute("update remitos set pedido_id=(select id from pedidos where id<>137 order by id limit 1) where numero_legal='0015-00003031'"); con.commit(); con.close()
rc, out = correr(M065, db)
check(f"si el 3031 no es el de Petroplastic (pedido #137): no toca nada y se registra [rc {rc}]", rc == 0 and "Nada que hacer" in out
      and q(db, "select metodo_entrega from remitos where numero_legal='0015-00003031'") == [("MOSTRADOR",)] and registrada(db, "065_remito_3031_petroplastic"))

# ---- auto_migrar las descubre, en orden (la 064 antes que la 065)
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
ids_ = [m for m, _ in auto_migrar.migraciones_disponibles()]
# [S891] ya no son las ultimas (despues viene la 066): lo que importa es que se descubren y la 064 corre antes que la 065
check(f"auto_migrar descubre la 064 y la 065, en ese orden", "064_empresas_transporte_web_retiro" in ids_ and "065_remito_3031_petroplastic" in ids_
      and ids_.index("064_empresas_transporte_web_retiro") < ids_.index("065_remito_3031_petroplastic"))

shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
