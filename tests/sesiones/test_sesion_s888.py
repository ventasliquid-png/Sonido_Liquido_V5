r"""S888, Card #183 (decisión de Carlos 19/10: «arrancá con la #183 con 7 días»): la sesión no debería obligar a nadie a cerrarla para poder hacer un cambio.
Caso real: en P, con la sesión vencida (token de 25 h), la pantalla dejaba seguir (el guard del router solo miraba que EXISTIERA un token) y fallaban en silencio las acciones
que firman con el usuario (no comercial, liberar despacho, conciliar facturas...); el botón «Cerrar Sesión» de la barra lateral emitía un evento que nadie escuchaba.
(1) Servidor: la sesión dura 7 días; el token trae iat; POST /auth/refresh renueva un token VÁLIDO de un usuario activo y rechaza uno vencido, inválido o ausente.
(2) Pantalla (estática): renovación silenciosa al usarla (como mucho una vez por hora), 401 global -> login una sola vez y vuelta a la misma pantalla, guard que rechaza un token
vencido, aviso en el login, cartel «¿Querés seguir?» y botón «Cerrar Sesión» que funciona. El comportamiento se verificó además en el navegador de D (5 escenarios).
Sobre una COPIA de la base de desarrollo de D (usuario de prueba admin/admin123, el mismo que usan las pruebas de la Etapa 7)."""
import sys, os, shutil, sqlite3, re, io
from datetime import datetime, timedelta, timezone
from _esquema_p import copiar_p   # [S888] la copia de D tambien necesita la columna nueva del modelo
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
os.makedirs(os.path.join(RAIZ, "scratch"), exist_ok=True)
T = os.path.join(RAIZ, "scratch", "test_sesion_tmp.db"); copiar_p(os.path.join(RAIZ, "pilot_v5x.db"), T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
app.dependency_overrides[get_db] = ov          # solo la base: la autenticacion es la real
c = TestClient(app, raise_server_exceptions=False)
def decodificar(t): return jwt.decode(t, SECRET_KEY, algorithms=[ALGORITHM])
def token(minutos, sub="admin", clave=SECRET_KEY):
    return jwt.encode({"sub": sub, "exp": datetime.now(timezone.utc) + timedelta(minutes=minutos)}, clave, algorithm=ALGORITHM)
def detalle(r): return (r.json() or {}).get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else r.text
SIETE_DIAS = 7 * 24 * 3600

# ---------------- (1) servidor
check(f"la sesión dura 7 días (ACCESS_TOKEN_EXPIRE_MINUTES = {ACCESS_TOKEN_EXPIRE_MINUTES})", ACCESS_TOKEN_EXPIRE_MINUTES == 10080)
r = c.post("/auth/token", data={"username": "admin", "password": "admin123"})
t = r.json().get("access_token") if r.status_code == 200 else None
d = decodificar(t) if t else {}
ahora = datetime.now(timezone.utc).timestamp()
check(f"el login da un token de 7 días con iat (cuándo se emitió) [{r.status_code}] vence en {round((d.get('exp', 0) - ahora) / 86400, 3)} días",
      t and abs(d["exp"] - ahora - SIETE_DIAS) < 120 and abs(d.get("iat", 0) - ahora) < 120 and d.get("sub") == "admin")
r = c.post("/auth/token", data={"username": "admin", "password": "otra"})
check(f"contraseña incorrecta: 401 como siempre (el login no cambia) [{r.status_code}]", r.status_code == 401 and "incorrectos" in detalle(r))
r = c.post("/auth/refresh", headers={"Authorization": f"Bearer {token(30)}"})
n = r.json().get("access_token") if r.status_code == 200 else None
dn = decodificar(n) if n else {}
check(f"POST /auth/refresh con un token VÁLIDO devuelve uno nuevo del mismo usuario, de 7 días completos y con iat [{r.status_code}]",
      n and dn.get("sub") == "admin" and abs(dn["exp"] - datetime.now(timezone.utc).timestamp() - SIETE_DIAS) < 120 and "iat" in dn)
r2 = c.patch("/pedidos/999999/no-comercial", json={"is_no_comercial": True}, headers={"Authorization": f"Bearer {n}"}) if n else None
check(f"el token renovado sirve para una acción que exige sesión (pasa la autenticación: 404 de pedido inexistente, no 401) [{r2.status_code if r2 else None}]", r2 is not None and r2.status_code == 404)
for nombre, cab, quiere in (("vencido hace 1 minuto", {"Authorization": f"Bearer {token(-1)}"}, "Token inválido o expirado"),
                            ("con firma ajena", {"Authorization": f"Bearer {token(30, clave='otra-clave')}"}, "Token inválido o expirado"),
                            ("basura", {"Authorization": "Bearer invalid.token.value"}, "Token inválido o expirado"),
                            ("ausente", {}, "Not authenticated")):
    r = c.post("/auth/refresh", headers=cab)
    check(f"/auth/refresh con un token {nombre}: 401 «{quiere}» (un token muerto no se renueva: hay que entrar de nuevo) [{r.status_code}]", r.status_code == 401 and detalle(r) == quiere)
con = sqlite3.connect(T); con.execute("update usuarios set is_active = 0 where username = 'admin'"); con.commit(); con.close()
r = c.post("/auth/refresh", headers={"Authorization": f"Bearer {token(30)}"})
check(f"un usuario desactivado no renueva (403 «Usuario inactivo») [{r.status_code}]", r.status_code == 403)
con = sqlite3.connect(T); con.execute("update usuarios set is_active = 1 where username = 'admin'"); con.commit(); con.close()

# ---------------- (2) pantalla (estática)
ses, api_, rou, log_, side, app_, aviso = (leer(f"frontend/src/{p}") for p in ("services/sesion.js", "services/api.js", "router/index.js", "views/Login.vue",
                                                                              "components/layout/AppSidebar.vue", "App.vue", "components/ui/AvisoSesion.vue"))
check("services/sesion.js: renueva si el token tiene más de 1 hora (o no trae iat) y no venció; cartel en los últimos 5 minutos",
      "RENOVAR_CADA_MS = 60 * 60 * 1000" in ses and "AVISO_ANTES_MS = 5 * 60 * 1000" in ses and "if (typeof datos.iat !== 'number') return true;" in ses and "ahora - datos.iat * 1000 >= RENOVAR_CADA_MS" in ses)
check("la renovación es de a una (si ya hay una en curso, no se pide otra) y no vuelve a disparar la renovación (__sinRenovar)",
      "if (renovando) return renovando;" in ses and "api.post('/auth/refresh', null, { __sinRenovar: true })" in ses)
check("irAlLogin va al login UNA sola vez, limpia la sesión y recuerda la pantalla para volver; el destino solo puede ser una ruta interna",
      "if (yendoAlLogin) return;" in ses and "window.location.assign(`/login?motivo=${encodeURIComponent(motivo)}&volver=${encodeURIComponent(volver)}`)" in ses
      and "v.startsWith('/') && !v.startsWith('//') && !v.startsWith('/login')" in ses)
check("api.js: renovación silenciosa antes de cada pedido al servidor (salvo los de /auth/) y 401 global -> login (salvo el del propio login)",
      "renovarSiHaceFalta(api)" in api_ and "!String(config.url || '').startsWith('/auth/')" in api_
      and re.search(r"error\.response\.status === 401 && !url\.includes\('/auth/token'\)\) \{\s*irAlLogin\('vencida'\);", api_))
check("router: un token VENCIDO ya no deja entrar: lleva al login con el aviso y la pantalla para volver",
      "import { tokenVencido } from '../services/sesion';" in rou and re.search(r"tokenVencido\(token\)\) \{[\s\S]{0,400}next\(\{ path: '/login', query: \{ motivo: 'vencida', volver: to\.fullPath \} \}\);", rou))
check("login: explica que la sesión venció y, al entrar, vuelve a la pantalla donde estaba", "Tu sesión venció. Entrá de nuevo y seguís donde estabas." in log_ and "router.push(destinoSeguro(route.query.volver));" in log_ and 'data-aviso="sesion"' in log_)
check("barra lateral: «Cerrar Sesión» hace algo (pregunta y cierra) en vez de solo emitir un evento que nadie escucha",
      '@click="salir"' in side and "const salir = () => { emit('logout'); cerrarSesion(router) }" in side and "@click=\"$emit('logout')\"" not in side and "window.confirm('¿Cerrar la sesión?')" in ses)
check("el cartel «¿Querés seguir?» está montado una vez en App.vue, con «Sí, seguir» (renueva) y «No, cerrar sesión», y se cierra solo si nadie contesta",
      "<AvisoSesion />" in app_ and 'data-accion="seguir"' in aviso and 'data-accion="cerrar"' in aviso and "if (ms <= 0) { visible.value = false; irAlLogin('vencida'); return; }" in aviso and "renovarAhora(api)" in aviso)

app.dependency_overrides.clear()
try: eng.dispose(); os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
