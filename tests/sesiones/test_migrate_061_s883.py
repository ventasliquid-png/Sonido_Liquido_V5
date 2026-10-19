r"""migrate_061 (S883, Card #158): deja inactivos los domicilios repetidos de Centro Pet (Vieytes 1549) e INAPYR (Diagonal 74 N° 80). Sobre COPIAS de la base de P de las 15:51."""
import sys, os, shutil, sqlite3, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261009_1551.db"
CP, CP_Q, CP_S = "069bd7c5be294d88a1df92c856239a7f", "dcc423810a45424e8a29202e85b97349", "e1a12cf398264bf7aeb1c5a7ed3f7458"
IN, IN_Q, IN_S = "65ae103173c04371bdf7f4cd5567598e", "0358b5a6d2ec461caec2c3978930499a", "3d561b71aa15479e914dddfd8fe950d8"
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def migrar(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_061_domicilios_repetidos.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def dom(db, i): return q(db, "select activo, is_active, observaciones from domicilios where id=?", i)[0]
def resto(db, excluir):
    ph = ",".join("?" * len(excluir))
    return (q(db, f"select * from domicilios where id not in ({ph}) order by id", *excluir), q(db, "select * from domicilios_clientes order by cliente_id, domicilio_id"),
            q(db, "select id, estado, domicilio_entrega_id from pedidos order by id"), q(db, "select id, estado, domicilio_entrega_id from remitos order by id"))

A = copia("test_061_a.db"); antes = resto(A, [CP_S, IN_S])
check("partida: los dos pares existen, los cuatro domicilios estan activos y cada par tiene la misma direccion",
      all(dom(A, i)[0] == 1 for i in (CP_Q, CP_S, IN_Q, IN_S)))
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "sobrantes dejados inactivos: 2" in out and "AVISO" not in out and "ERROR" not in out)
check("los dos SOBRANTES quedan inactivos, con la nota [SISTEMA] que dice cual queda", all(dom(A, s)[:2] == (0, 0) and "[SISTEMA]" in dom(A, s)[2] and q_[:8] in dom(A, s)[2] for s, q_ in ((CP_S, CP_Q), (IN_S, IN_Q))))
check("los dos que QUEDAN siguen activos y sin tocar", all(dom(A, i)[:2] == (1, 1) and "[SISTEMA]" not in str(dom(A, i)[2]) for i in (CP_Q, IN_Q)))
check("no se borra nada: los cuatro domicilios y sus vinculos con el cliente siguen", q(A, "select count(*) from domicilios where id in (?,?,?,?)", CP_Q, CP_S, IN_Q, IN_S)[0][0] == 4 and q(A, "select count(*) from domicilios_clientes where domicilio_id in (?,?,?,?)", CP_Q, CP_S, IN_Q, IN_S)[0][0] == 4)
check("nada mas cambia: los demas domicilios, los vinculos cliente-domicilio, los pedidos y los remitos", resto(A, [CP_S, IN_S]) == antes)
rc2, out2 = migrar(A); check(f"segunda corrida: se saltea [{rc2}]", rc2 == 0 and "SKIP" in out2)
con = sqlite3.connect(A); con.execute("delete from _migraciones_aplicadas where id like '061%'"); con.commit(); con.close()
snap = (dom(A, CP_S), dom(A, IN_S)); rc3, out3 = migrar(A)
check(f"sin el registro: la marca de la nota evita repetir y no cambia nada [{rc3}]", rc3 == 0 and out3.count("ya tiene la marca") == 2 and (dom(A, CP_S), dom(A, IN_S)) == snap)
os.remove(A)

# ---------- guardas: ese par no se toca, el otro si ----------
casos = [("un pedido usa el sobrante de Centro Pet como entrega", lambda c: c.execute("update pedidos set domicilio_entrega_id=? where id=111", (CP_S,)), CP_S, IN_S),
         ("un remito usa el sobrante de INAPYR como entrega", lambda c: c.execute("update remitos set domicilio_entrega_id=? where id=(select min(id) from remitos)", (IN_S,)), IN_S, CP_S),
         ("el sobrante de Centro Pet esta vinculado tambien a otro cliente", lambda c: c.execute("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 0, 0)", (IN, CP_S)), CP_S, IN_S),
         ("las direcciones del par de INAPYR ya no coinciden", lambda c: c.execute("update domicilios set numero='99' where id=?", (IN_S,)), IN_S, CP_S),
         ("el sobrante de Centro Pet es el fiscal", lambda c: c.execute("update domicilios set es_fiscal=1 where id=?", (CP_S,)), CP_S, IN_S),
         ("el sobrante de INAPYR es el predeterminado del cliente", lambda c: c.execute("update domicilios_clientes set es_predeterminado=1 where domicilio_id=?", (IN_S,)), IN_S, CP_S),
         ("el domicilio que queda de Centro Pet esta inactivo", lambda c: c.execute("update domicilios set activo=0 where id=?", (CP_Q,)), CP_S, IN_S)]
for desc, prep, intacto, procesado in casos:
    G = copia("test_061_g.db"); con = sqlite3.connect(G); prep(con); con.commit(); con.close()
    s0 = dom(G, intacto); rc, out = migrar(G)
    check(f"guarda: {desc} -> ese par queda como estaba y se avisa, el otro par se procesa [{rc}]", rc == 0 and "AVISO" in out and dom(G, intacto) == s0 and dom(G, procesado)[:2] == (0, 0))
    os.remove(G)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
