"""Test end-to-end de la Etapa 6 (devolucion como cantidad negativa), contra una copia
descartable. Nunca toca pilot_v5x.db real. Usa el pedido_item #48 real (pedido #28,
cantidad=2.0, ya entregado 2.0/2.0 -- CUMPLIDO) como caso de devolucion parcial y despues
de exceso."""
import shutil, sys, os
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5")
os.chdir(r"C:\dev\Sonido_Liquido_V5")

SCRATCH_DB = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_etapa6_test.db"
copiar_p("pilot_v5x.db", SCRATCH_DB)

checks = []
def check(desc, cond):
    checks.append((desc, bool(cond)))
    print(("[OK]  " if cond else "[FAIL]"), desc)

import backend.main as main_module
from backend.main import app
from backend.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

engine = create_engine(f"sqlite:///{SCRATCH_DB}")
TestSession = sessionmaker(bind=engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

PEDIDO_ID = 28
PEDIDO_ITEM_ID = 48
# El pedido 28 no tiene transporte_id propio -- se lo pasamos explicito en cada payload
# (ArmarRemitoPayload lo permite como override), igual que haria la pantalla real si el
# pedido no lo trae precargado.
DOMICILIO_ID = "0358b5a6d2ec461caec2c3978930499a"
TRANSPORTE_ID = "44264d5c43a147d3997fd558d38b3db6"

# ============ Estado inicial: cantidad_entregada = 2.0 (CUMPLIDO) ============
resp_pedido = client.get(f"/pedidos/{PEDIDO_ID}")
check("GET pedido 28 -> 200", resp_pedido.status_code == 200)
item_inicial = next(i for i in resp_pedido.json()["items"] if i["id"] == PEDIDO_ITEM_ID)
check(f"Item 48 arranca CUMPLIDO (entregada={item_inicial['cantidad_entregada']} == cantidad={item_inicial['cantidad']})",
      item_inicial["cantidad_entregada"] == item_inicial["cantidad"] == 2.0)

# ============ Guarda: no se puede devolver MAS de lo entregado (2.5 > 2.0) ============
resp_exceso = client.post("/remitos/armar", json={
    "pedido_id": PEDIDO_ID, "domicilio_entrega_id": DOMICILIO_ID, "transporte_id": TRANSPORTE_ID,
    "items": [{"pedido_item_id": PEDIDO_ITEM_ID, "cantidad": -2.5}],
})
check("Devolver 2.5 sobre 2.0 entregado -> 409 DEVOLUCION_EXCEDE_ENTREGADO",
      resp_exceso.status_code == 409 and "DEVOLUCION_EXCEDE_ENTREGADO" in resp_exceso.json()["detail"])

# Verificar que el rollback fue real: el pedido sigue igual (no quedo un remito fantasma)
resp_pedido2 = client.get(f"/pedidos/{PEDIDO_ID}")
item_post_fail = next(i for i in resp_pedido2.json()["items"] if i["id"] == PEDIDO_ITEM_ID)
check("Tras el 409, cantidad_entregada sigue en 2.0 (rollback real)", item_post_fail["cantidad_entregada"] == 2.0)

# ============ Devolucion parcial valida: -1.0 ============
resp_dev = client.post("/remitos/armar", json={
    "pedido_id": PEDIDO_ID, "domicilio_entrega_id": DOMICILIO_ID, "transporte_id": TRANSPORTE_ID,
    "items": [{"pedido_item_id": PEDIDO_ITEM_ID, "cantidad": -1.0}],
})
check("Devolver 1.0 sobre 2.0 entregado -> 200", resp_dev.status_code == 200)
remito_devolucion = resp_dev.json()
check("El remito de devolucion nace BORRADOR", remito_devolucion["estado"] == "BORRADOR")
check("El remito de devolucion nace sin numero_legal (se numera al imprimir)", remito_devolucion["numero_legal"] is None)
item_dev = remito_devolucion["items"][0]
check(f"El RemitoItem de la devolucion tiene cantidad -1.0 (obtenido {item_dev['cantidad']})", item_dev["cantidad"] == -1.0)

# ============ El renglon se "descompleta": vuelve a tener pendiente ============
resp_pedido3 = client.get(f"/pedidos/{PEDIDO_ID}")
item_post_dev = next(i for i in resp_pedido3.json()["items"] if i["id"] == PEDIDO_ITEM_ID)
check(f"cantidad_entregada baja a 1.0 (obtenido {item_post_dev['cantidad_entregada']})", item_post_dev["cantidad_entregada"] == 1.0)
saldo = item_post_dev["cantidad"] - item_post_dev["cantidad_entregada"]
check(f"El renglon vuelve a tener 1.0 pendiente (saldo={saldo})", saldo == 1.0)

# ============ Ahora SI se puede armar un PR nuevo por ese pendiente (renglon ampliable de nuevo) ============
resp_reamado = client.post("/remitos/armar", json={
    "pedido_id": PEDIDO_ID, "domicilio_entrega_id": DOMICILIO_ID, "transporte_id": TRANSPORTE_ID,
    "items": [{"pedido_item_id": PEDIDO_ITEM_ID, "cantidad": 1.0}],
})
check("Tras la devolucion, se puede volver a armar un PR por el pendiente liberado -> 200", resp_reamado.status_code == 200)

resp_pedido4 = client.get(f"/pedidos/{PEDIDO_ID}")
item_final = next(i for i in resp_pedido4.json()["items"] if i["id"] == PEDIDO_ITEM_ID)
check(f"cantidad_entregada vuelve a 2.0 (obtenido {item_final['cantidad_entregada']})", item_final["cantidad_entregada"] == 2.0)

# ============ Segunda devolucion sobre el mismo renglon, ahora exacta al limite (2.0) ============
resp_dev2 = client.post("/remitos/armar", json={
    "pedido_id": PEDIDO_ID, "domicilio_entrega_id": DOMICILIO_ID, "transporte_id": TRANSPORTE_ID,
    "items": [{"pedido_item_id": PEDIDO_ITEM_ID, "cantidad": -2.0}],
})
check("Devolver exactamente 2.0 sobre 2.0 entregado (limite) -> 200", resp_dev2.status_code == 200)
resp_pedido5 = client.get(f"/pedidos/{PEDIDO_ID}")
item_post_dev2 = next(i for i in resp_pedido5.json()["items"] if i["id"] == PEDIDO_ITEM_ID)
check(f"cantidad_entregada vuelve a 0.0 tras devolver todo (obtenido {item_post_dev2['cantidad_entregada']})", item_post_dev2["cantidad_entregada"] == 0.0)

# ============ RENGLON_AJENO_AL_PEDIDO sigue funcionando con cantidad negativa (guarda compartida) ============
resp_ajeno = client.post("/remitos/armar", json={
    "pedido_id": PEDIDO_ID, "domicilio_entrega_id": DOMICILIO_ID, "transporte_id": TRANSPORTE_ID,
    "items": [{"pedido_item_id": 999999, "cantidad": -1.0}],
})
check("Devolucion con pedido_item_id ajeno -> 409 RENGLON_AJENO_AL_PEDIDO",
      resp_ajeno.status_code == 409 and "RENGLON_AJENO_AL_PEDIDO" in resp_ajeno.json()["detail"])

# ============ Informe A (get_entregas) incluye la fila negativa sin romperse, sin falsa SOBRE_ENTREGA ============
resp_informe = client.get("/informes/remitos", params={"cliente_id": None})
check("Informe A (remitos) -> 200 con filas negativas en la base", resp_informe.status_code == 200)
filas_negativas = [f for f in resp_informe.json()["filas"] if f.get("pedido_item_id") == PEDIDO_ITEM_ID and (f.get("cantidad_remitida") or 0) < 0]
check(f"Informe A muestra al menos una fila con cantidad_remitida negativa para el item 48 (encontradas: {len(filas_negativas)})", len(filas_negativas) >= 1)

resp_entregas = client.get("/remitos/entregas")
anomalias_sobre_entrega = [a for a in resp_entregas.json()["anomalias"] if a["tipo"] == "SOBRE_ENTREGA" and a.get("pedido_item_id") == PEDIDO_ITEM_ID]
check("GET /remitos/entregas -> 200, sin falsa SOBRE_ENTREGA en el item 48 (neto 0, nunca excedio 2.0)",
      resp_entregas.status_code == 200 and len(anomalias_sobre_entrega) == 0)

# ============ PDF del remito de devolucion no rompe con cantidad negativa ============
remito_dev_id = remito_devolucion["id"]
resp_pdf = client.get(f"/remitos/{remito_dev_id}/pdf")
check(f"GET /remitos/{{id}}/pdf del remito de devolucion -> 200 (no crashea con cantidad negativa)", resp_pdf.status_code == 200)
check("El PDF generado tiene contenido real (no vacio)", len(resp_pdf.content) > 500)

print()
total = len(checks)
ok = sum(1 for _, c in checks if c)
print(f"RESULTADO: {ok}/{total} checks OK")
if ok != total:
    sys.exit(1)
