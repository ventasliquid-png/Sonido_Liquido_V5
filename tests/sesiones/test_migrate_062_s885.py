r"""migrate_062 (S885, Card #173): le da su domicilio fiscal a los clientes Blanco + Responsable Inscripto que no lo tenian (Gelato, Jomax, Medi Cient); Agustin Suarez Cipolletti NO se toca.
Sobre COPIAS de la base de P de las 15:51."""
import sys, os, shutil, sqlite3, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261009_1551.db"
GEL, GEL_D = "2fbeb6ebffc649ff81d1e324f410eed6", "30fb7723c09b4faf85c75c768b422ff3"
JOM, JOM_D = "ff6e98c3710f46f89ecf9045b26ea1aa", "764e8e0155914a5b8d2ade7dc0b04760"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_062_fiscales_blanco_ri.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
MEDI = q(ORIG, "select id from clientes where cuit='30657001569'")[0][0]
AGU = q(ORIG, "select id from clientes where cuit='33707925529'")[0][0]
def sin_fiscal_blanco_ri(db):
    return sorted(r[0] for r in q(db, """select c.razon_social from clientes c join condiciones_iva ci on ci.id=c.condicion_iva_id
        where c.activo=1 and ci.nombre='Responsable Inscripto' and (c.flags_estado & 15) in (13,15)
        and not exists (select 1 from domicilios_clientes dc join domicilios d on d.id=dc.domicilio_id where dc.cliente_id=c.id and d.es_fiscal=1 and d.activo=1)"""))
def resto(db, excluir_doms, excluir_clientes_dc):
    ph = ",".join("?" * len(excluir_doms))
    phc = ",".join("?" * len(excluir_clientes_dc))
    return (q(db, f"select * from domicilios where id not in ({ph}) order by id", *excluir_doms), q(db, f"select * from domicilios_clientes where cliente_id not in ({phc}) order by cliente_id, domicilio_id", *excluir_clientes_dc),
            q(db, "select id, estado, domicilio_entrega_id from pedidos order by id"), q(db, "select id, razon_social, flags_estado from clientes order by id"))

A = copia("test_062_a.db")
check(f"partida: los 4 Blanco + RI sin fiscal de P {sin_fiscal_blanco_ri(A)}", len(sin_fiscal_blanco_ri(A)) == 4)
antes = resto(A, [GEL_D, JOM_D], [GEL, JOM, MEDI]); n_dom0 = q(A, "select count(*) from domicilios")[0][0]
vg0, fk0 = q(A, "select count(*) from vinculos_geograficos")[0][0], len(q(A, "pragma foreign_key_check"))
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l.strip() for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "fiscal corregido: 3" in out and "AVISO" not in out and "ERROR" not in out)
check(f"quedan sin fiscal SOLO los que no se tocan: Agustin Suarez {sin_fiscal_blanco_ri(A)}", sin_fiscal_blanco_ri(A) == ["AGUSTÍN SUÁREZ CIPOLLETTI"])
g = q(A, "select es_fiscal, es_entrega, calle, numero, localidad, cp, provincia_id, observaciones from domicilios where id=?", GEL_D)[0]
check("Gelato: su fila de Ruta 36 y 630 pasa a FISCAL (sigue de entrega) y queda ordenada, con el texto original de ARCA en las observaciones",
      g[:7] == (1, 1, "Ruta Provincial 36 y 630", "S/N", "La Plata", "1900", "BA") and "RUTA PROVINCIAL 36 Y 630 0, LA PLATA SUDESTE CALLE 50 AMBAS VEREDAS" in g[7] and "migrate_062" in g[7])
j = q(A, "select es_fiscal, es_entrega, calle, numero, depto, cp, provincia_id from domicilios where id=?", JOM_D)[0]
check("Jomax: su unico domicilio pasa a FISCAL sin cambiar la direccion (Juan B. Justo 9246, Dpto A, 1408)", j[:2] == (1, 1) and j[3:] == ("9246", "A", "1408", "C") and q(A, "select calle from domicilios where id=?", JOM_D) == q(ORIG, "select calle from domicilios where id=?", JOM_D))
m = q(A, "select d.id, d.es_fiscal, d.es_entrega, d.calle, d.numero, d.piso, d.localidad, d.cp, d.provincia_id, d.activo, d.is_active, d.cliente_id from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=?", MEDI)
check(f"Medi Cient: se crea UN domicilio fiscal y de entrega: Caseros 1810 PB, Florida, 1602, Buenos Aires [{len(m)}]",
      len(m) == 1 and m[0][1:11] == (1, 1, "Caseros", "1810", "PB", "Florida", "1602", "BA", 1, 1) and m[0][11] == MEDI)
check("Medi Cient: el vinculo con el cliente tiene el espejo (Bit 21) como todos los demas", q(A, "select flags from domicilios_clientes where cliente_id=?", MEDI) == [(2097152,)])
check("vinculos geograficos: NO se crea ninguno nuevo (apuntan a «domicilios_legacy», que no existe, y cada uno suma una violacion al foreign_key_check) y los existentes no cambian",
      q(A, "select count(*) from vinculos_geograficos")[0][0] == vg0 and len(q(A, "pragma foreign_key_check")) == fk0
      and q(A, "select flags_relacion from vinculos_geograficos where entidad_tipo='CLIENTE' and entidad_id=? and domicilio_id=?", JOM, JOM_D) == q(ORIG, "select flags_relacion from vinculos_geograficos where entidad_tipo='CLIENTE' and entidad_id=? and domicilio_id=?", JOM, JOM_D))
check("Agustin Suarez: ni su domicilio ni su ficha cambian", q(A, "select * from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=?", AGU) == q(ORIG, "select * from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=?", AGU))
check("se agrega exactamente UN domicilio (el de Medi Cient) y nada mas cambia: los demas domicilios, vinculos, pedidos y clientes",
      q(A, "select count(*) from domicilios")[0][0] == n_dom0 + 1 and resto(A, [GEL_D, JOM_D, m[0][0]], [GEL, JOM, MEDI]) == antes)
check("la base queda integra", q(A, "pragma integrity_check") == [("ok",)])
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '062%'"); con.commit(); con.close()
snap = (q(A, "select * from domicilios order by id"), q(A, "select * from domicilios_clientes order by cliente_id, domicilio_id")); rc3, out3 = migrar(A)
check(f"sin el registro: las guardas evitan repetir (no duplica el de Medi Cient ni vuelve a tocar nada) [{rc3}]", rc3 == 0 and out3.count("AVISO") == 3
      and (q(A, "select * from domicilios order by id"), q(A, "select * from domicilios_clientes order by cliente_id, domicilio_id")) == snap)
os.remove(A)

# ---------- guardas: ese cliente no se toca, los otros si ----------
casos = [("Gelato ya tiene OTRO fiscal activo", lambda c: c.execute("update domicilios set es_fiscal=1 where id=(select domicilio_id from domicilios_clientes where cliente_id=? and domicilio_id != ? limit 1)", (GEL, GEL_D)), "GELATO"),
         ("alguien edito la fila de Gelato (ya no tiene el texto de ARCA)", lambda c: c.execute("update domicilios set calle='Ruta 36 km 630' where id=?", (GEL_D,)), "GELATO"),
         ("la fila de Gelato la comparte otro cliente", lambda c: c.execute("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 0, 0)", (JOM, GEL_D)), "GELATO"),
         ("Jomax ya no es de Juan B. Justo 9246", lambda c: c.execute("update domicilios set numero='9300' where id=?", (JOM_D,)), "JOMAX"),
         ("Jomax esta inactivo", lambda c: c.execute("update clientes set activo=0 where id=?", (JOM,)), "JOMAX"),
         ("Medi Cient ya tiene un domicilio (lo cargo Tomy)", lambda c: c.execute("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 0, 0)", (MEDI, JOM_D)), "MEDI")]
for i, (desc, preparar, quien) in enumerate(casos):
    B = copia(f"test_062_b{i}.db")
    con = sqlite3.connect(B); preparar(con); con.commit(); con.close()
    n_antes = q(B, "select count(*) from domicilios")[0][0]
    rc, out = migrar(B)
    aviso = [l for l in out.splitlines() if "AVISO" in l and quien in l.upper().replace("INSUMOS HOSPITALARIOS", "").replace("S.R.L.", "").replace("MEDI CIENT", "MEDI")]
    check(f"guarda: {desc} -> ese cliente se avisa y NO se toca [{rc}]", rc == 0 and len(aviso) >= 1)
    if quien == "MEDI":
        check("guarda: ...y no se crea un domicilio de mas", q(B, "select count(*) from domicilios")[0][0] == n_antes)
    os.remove(B)

for f in os.listdir(os.path.join(RAIZ, "scratch")):
    if f.startswith("test_062_"):
        try: os.remove(os.path.join(RAIZ, "scratch", f))
        except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
