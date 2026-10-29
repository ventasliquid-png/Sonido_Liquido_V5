r"""migrate_074 (S895, Carlos 29/10; consulta a Nike): el RI salió con el formato «RI-000001» y Carlos fijó el talonario «RI01» + 8 dígitos. Antes de que el formato nuevo llegara a P,
Tomy probó el Cumplido de dos pedidos (RI-000001 y RI-000002). La migración los pasa a RI01-00000001 y RI01-00000002 con una nota [SISTEMA], solo si no se imprimieron, no tienen factura
y el número nuevo está libre. Sobre una COPIA de la base de P del 28/10 16:51; los RI de prueba se arman clonando un remito real."""
import sys, os, sqlite3, subprocess, uuid
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261028_1651.db"
IMPRESO = 1 << 44
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_074_ri_renumerar_talonario.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def clonar_ri(db, numero, flags_extra=0):
    """Clona un remito real como un RI viejo: ENTREGADO, sin papel, con el número dado. Devuelve su id."""
    con = sqlite3.connect(db)
    cols = [r[1] for r in con.execute("pragma table_info(remitos)")]
    fila = dict(zip(cols, con.execute("select * from remitos where numero_legal like '0015-%' order by numero_legal limit 1").fetchone()))
    rid = uuid.uuid4().hex
    fila.update(id=rid, numero_legal=numero, estado="ENTREGADO", flags_estado=((int(fila["flags_estado"] or 0) & ~IMPRESO) | flags_extra))
    con.execute(f"insert into remitos ({','.join(cols)}) values ({','.join('?' * len(cols))})", [fila[c] for c in cols]); con.commit(); con.close()
    return rid
def resto(db):
    return (q(db, "select id, numero_legal, estado, flags_estado from remitos where numero_legal not like 'RI%' order by id"), q(db, "select count(*) from remitos_notas where texto not like '%Renumerado%'"),
            q(db, "select id, estado, flags_estado from pedidos order by id"))

A = copia("test_074_a.db")
r1, r2 = clonar_ri(A, "RI-000001"), clonar_ri(A, "RI-000002")
antes = resto(A)
rc, out = migrar(A)
nums = sorted(n for (n,) in q(A, "select numero_legal from remitos where numero_legal like 'RI%'"))
check(f"pasa los dos RI viejos al talonario nuevo conservando el orden [{rc}] {nums}", rc == 0 and nums == ["RI01-00000001", "RI01-00000002"] and "renumerados 2, saltados 0, con error 0" in out)
check("cada uno lleva su nota [SISTEMA] con el número anterior", all(any(f"Renumerado de {v} a {n}" in t for (t,) in q(A, "select texto from remitos_notas where remito_id=?", rid))
      for rid, v, n in ((r1, "RI-000001", "RI01-00000001"), (r2, "RI-000002", "RI01-00000002"))))
check("nada más cambia: estado, marcas y clase de los RI, los demás remitos, sus notas y los pedidos", resto(A) == antes
      and all(q(A, "select estado from remitos where id=?", rid)[0][0] == "ENTREGADO" for rid in (r1, r2)))
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
os.remove(A)

# guardas: impreso, con factura, o número nuevo ya existente
B = copia("test_074_b.db")
impreso = clonar_ri(B, "RI-000001", IMPRESO)
facturado = clonar_ri(B, "RI-000002")
fid = q(B, "select id from facturas limit 1")[0][0]
con = sqlite3.connect(B); con.execute("insert into facturas_remitos (factura_id, remito_id, fecha_vinculo, flags_estado) values (?, ?, datetime('now'), 1)", (fid, facturado)); con.commit(); con.close()
choque = clonar_ri(B, "RI-000003"); clonar_ri(B, "RI01-00000003")
libre = clonar_ri(B, "RI-000004")
rc, out = migrar(B)
nums = dict(q(B, "select id, numero_legal from remitos where numero_legal like 'RI%'"))
check(f"guardas: el impreso, el facturado y el que chocaría con un número existente quedan como estaban y se avisa; el libre se renumera [{rc}]",
      rc == 0 and nums[impreso] == "RI-000001" and nums[facturado] == "RI-000002" and nums[choque] == "RI-000003" and nums[libre] == "RI01-00000004" and out.count("AVISO") == 3)
os.remove(B)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
