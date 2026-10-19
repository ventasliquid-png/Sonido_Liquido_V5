"""Contrato servidor <-> selector de estado de los informes (S876). Sobre una COPIA de la base migrada de P."""
import sys, os, shutil, sqlite3, gc
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_estado_informe_tmp.db"
shutil.copyfile(r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_migrada_20260930.db", TMP)
eng = create_engine(f"sqlite:///{TMP}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(TMP); v = con.execute(sql, a).fetchall(); con.close(); return v
# un pedido PENDIENTE sin ninguna entrega, con renglones (el de Informe F), y uno ya CUMPLIDO sin salida
pend = q("select p.id from pedidos p where p.estado='PENDIENTE' and p.id not in (select pedido_id from remitos) order by p.id limit 3")
pid = pend[0][0]
r = c.patch(f"/pedidos/{pid}", json={"estado": "PRESUPUESTO"}); check(f"PENDIENTE -> PRESUPUESTO con payload {{estado}} solo: 200 [{r.status_code}] y queda en la base", r.status_code == 200 and q("select estado from pedidos where id=?", pid)[0][0] == "PRESUPUESTO")
r = c.patch(f"/pedidos/{pid}", json={"estado": "INTERNO"}); check(f"-> INTERNO [{r.status_code}]", r.status_code == 200 and q("select estado from pedidos where id=?", pid)[0][0] == "INTERNO")
r = c.patch(f"/pedidos/{pid}", json={"estado": "PENDIENTE"}); check(f"-> PENDIENTE [{r.status_code}]", r.status_code == 200 and q("select estado from pedidos where id=?", pid)[0][0] == "PENDIENTE")
r = c.patch(f"/pedidos/{pid}", json={"estado": "CUMPLIDO"})
check(f"-> CUMPLIDO sin entregas: 409 CIERRE_CON_DISCREPANCIA [{r.status_code}], y NO cambia nada", r.status_code == 409 and r.json()["detail"].startswith("CIERRE_CON_DISCREPANCIA") and q("select estado from pedidos where id=?", pid)[0][0] == "PENDIENTE")
nota0 = q("select coalesce(nota,'') from pedidos where id=?", pid)[0][0]
r = c.patch(f"/pedidos/{pid}", json={"estado": "CUMPLIDO", "cierre_confirmado": True})
check(f"reenviado con cierre_confirmado: 200 [{r.status_code}], CUMPLIDO en la base", r.status_code == 200 and q("select estado from pedidos where id=?", pid)[0][0] == "CUMPLIDO")
nota1 = q("select coalesce(nota,'') from pedidos where id=?", pid)[0][0]
check("el cierre con discrepancia deja la nota documentando la diferencia (misma regla que el Tablero)", len(nota1) > len(nota0))
r = c.patch(f"/pedidos/{pid}", json={"estado": "ANULADO"}); check(f"CUMPLIDO -> ANULADO [{r.status_code}]", r.status_code == 200 and q("select estado from pedidos where id=?", pid)[0][0] == "ANULADO")
# el informe refleja el estado nuevo
j = c.get("/informes/pedidos-sin-remito", params={"incluir_anulados": True}).json()
fila = next((x for x in j["filas"] if x["pedido_id"] == pid), None)
check("el Informe F, recargado, muestra el estado nuevo del pedido (ANULADO) con su estado_base", fila is not None and fila["estado_base"] == "ANULADO" and fila["estado"] == "ANULADO")
# el selector manda solo {estado}: el schema (extra=forbid) lo acepta; un campo ajeno se rechaza fuerte
r = c.patch(f"/pedidos/{pend[1][0]}", json={"estado": "PRESUPUESTO", "campo_inventado": 1}); check(f"un campo que el schema no conoce es 422 explícito (la regla de 'fallar ruidoso') [{r.status_code}]", r.status_code == 422)
del c; gc.collect(); eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
