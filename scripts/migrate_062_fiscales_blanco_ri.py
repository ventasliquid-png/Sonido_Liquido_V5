"""
migrate_062_fiscales_blanco_ri.py
=================================
S885 (13/10/2026), Card #173. Regla de Carlos (09/10): un cliente BLANCO (flags_estado & 15 en 13 o 15) y Responsable Inscripto NO puede quedar sin domicilio fiscal.
El barrido de la copia de P del 09/10 (15:51) encontro 4 que no la cumplen; el domicilio fiscal de cada uno se consulto al Padron A13 de ARCA por el Puente (solo lectura):

  - GELATO SA (30-69934960-3): ARCA = «RUTA PROVINCIAL 36 Y 630 0, LA PLATA SUDESTE CALLE 50 AMBAS VEREDAS, BUENOS AIRES (1900)», IDENTICO al texto de su fila 30fb7723...
    (solo entrega, con el texto crudo de ARCA pegado en `calle`) -> se marca FISCAL y se ordena la fila (calle, numero, localidad, cp); el texto original queda en `observaciones`.
  - JOMAX INSUMOS HOSPITALARIOS (30-71649149-4): ARCA = «JUSTO JUAN B AV. 9246 Dpto:A, CIUDAD AUTONOMA BUENOS AIRES (1408)» = su unico domicilio 764e8e01... (solo entrega) -> se marca FISCAL.
  - MEDI CIENT S.R.L. (30-65700156-9): ARCA = «CASEROS 1810 PB, FLORIDA, BUENOS AIRES (1602)» (Carlos lo confirmo en cuitonline); en P no tiene NINGUN domicilio -> se crea ese como fiscal y entrega.
  - AGUSTIN SUAREZ CIPOLLETTI (33-70792552-9): NO SE TOCA. El CUIT cargado devuelve «VIA LONDRA S.A.» (Medrano 17, Ituzaingo): CUIT o razon social mal cargado; decide Carlos.

QUE NO HACE: no cambia ningun otro domicilio, cliente, pedido ni remito; no borra nada.
GUARDAS (por cliente; si algo no cierra se informa y ese cliente queda como estaba): el cliente existe, esta activo y TODAVIA no tiene domicilio fiscal activo; la fila a marcar existe, es solo de ese cliente, esta activa y
tiene el contenido esperado (Gelato: el texto crudo de ARCA; Jomax: Juan B. Justo 9246); Medi Cient: sin ningun domicilio y sin la marca de esta migracion. Idempotente (la marca en `observaciones`, el estado y el registro).
SEGURIDAD: SAVEPOINT por cliente, despues del backup de auto_migrar, sale siempre 0.

MIGRATION_ID = "062_fiscales_blanco_ri"
NRO_SESION = 885
"""
import os
import sqlite3
import uuid

MIGRATION_ID = "062_fiscales_blanco_ri"
NRO_SESION = 885
MARCA = "migrate_062"

GELATO_CLIENTE = "2fbeb6ebffc649ff81d1e324f410eed6"
GELATO_DOM = "30fb7723c09b4faf85c75c768b422ff3"
GELATO_TEXTO_ARCA = "RUTA PROVINCIAL 36 Y 630 0, LA PLATA SUDESTE CALLE 50 AMBAS VEREDAS, BUENOS AIRES (1900)"
JOMAX_CLIENTE = "ff6e98c3710f46f89ecf9045b26ea1aa"
JOMAX_DOM = "764e8e0155914a5b8d2ade7dc0b04760"
MEDI_CUIT = "30657001569"

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_062] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("clientes", "domicilios", "domicilios_clientes", "provincias"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_062] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)
HAY_VG = bool(cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='vinculos_geograficos'").fetchone())


def nota(texto):
    return f"[SISTEMA] {texto} ({MARCA}, S{NRO_SESION}, Card #173)."


def agregar_nota(dom_id, texto):
    cur.execute("UPDATE domicilios SET observaciones = CASE WHEN observaciones IS NULL OR trim(observaciones) = '' THEN ? ELSE observaciones || ' ' || ? END WHERE id = ?",
                (nota(texto), nota(texto), dom_id))


def tiene_fiscal_activo(cliente_id):
    return cur.execute("""SELECT 1 FROM domicilios d JOIN domicilios_clientes dc ON dc.domicilio_id = d.id
                          WHERE dc.cliente_id = ? AND d.es_fiscal = 1 AND COALESCE(d.activo, 1) = 1""", (cliente_id,)).fetchone() is not None


def cliente_activo(cliente_id=None, cuit=None):
    if cliente_id:
        r = cur.execute("SELECT id, activo FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    else:
        r = cur.execute("SELECT id, activo FROM clientes WHERE cuit = ?", (cuit,)).fetchone()
    return (r[0] if r and r[1] else None)


def marcar_vinculo_fiscal(cliente_id, dom_id):
    """Deja el vinculo geografico del cliente con ese domicilio con el bit 1 (fiscal); si no existe lo crea."""
    if not HAY_VG:
        return
    r = cur.execute("SELECT id, flags_relacion FROM vinculos_geograficos WHERE entidad_tipo = 'CLIENTE' AND entidad_id = ? AND domicilio_id = ?", (cliente_id, dom_id)).fetchone()
    if r:
        cur.execute("UPDATE vinculos_geograficos SET flags_relacion = ?, activo = 1 WHERE id = ?", ((r[1] or 0) | 1, r[0]))
    else:
        cur.execute("INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at) VALUES (?, 'CLIENTE', ?, ?, NULL, 1, 1, datetime('now'), datetime('now'))",
                    (uuid.uuid4().hex, cliente_id, dom_id))


def solo_de(dom_id, cliente_id):
    return [r[0] for r in cur.execute("SELECT cliente_id FROM domicilios_clientes WHERE domicilio_id = ?", (dom_id,))] == [cliente_id]


print(f"[migrate_062] Iniciando {MIGRATION_ID}...")
hechos, saltados, errores = [], [], []


def gelato():
    cli = cliente_activo(cliente_id=GELATO_CLIENTE)
    d = cur.execute("SELECT calle, es_fiscal, activo, observaciones FROM domicilios WHERE id = ?", (GELATO_DOM,)).fetchone()
    if cli is None:
        return "el cliente no existe o esta inactivo"
    if d is None:
        return "no esta la fila de Gelato"
    if MARCA in str(d[3] or ""):
        return "ya tiene la marca de la migracion"
    if tiene_fiscal_activo(cli):
        return "el cliente ya tiene un domicilio fiscal activo"
    if d[1] or not d[2]:
        return "la fila ya es fiscal o esta inactiva"
    if (d[0] or "").strip() != GELATO_TEXTO_ARCA:
        return "la fila ya no tiene el texto de ARCA (alguien la edito)"
    if not solo_de(GELATO_DOM, cli):
        return "la fila no es solo de Gelato"
    cur.execute("UPDATE domicilios SET es_fiscal = 1, calle = 'Ruta Provincial 36 y 630', numero = 'S/N', localidad = 'La Plata', cp = '1900' WHERE id = ?", (GELATO_DOM,))
    agregar_nota(GELATO_DOM, f"Se marca como domicilio FISCAL de Gelato (el que informa ARCA) y se ordena la direccion. Texto original de ARCA: {GELATO_TEXTO_ARCA}")
    marcar_vinculo_fiscal(cli, GELATO_DOM)
    return None


def jomax():
    cli = cliente_activo(cliente_id=JOMAX_CLIENTE)
    d = cur.execute("SELECT calle, numero, es_fiscal, activo, observaciones FROM domicilios WHERE id = ?", (JOMAX_DOM,)).fetchone()
    if cli is None:
        return "el cliente no existe o esta inactivo"
    if d is None:
        return "no esta la fila de Jomax"
    if MARCA in str(d[4] or ""):
        return "ya tiene la marca de la migracion"
    if tiene_fiscal_activo(cli):
        return "el cliente ya tiene un domicilio fiscal activo"
    if d[2] or not d[3]:
        return "la fila ya es fiscal o esta inactiva"
    if "JUSTO" not in (d[0] or "").upper() or (d[1] or "").strip() != "9246":
        return "la fila ya no es Juan B. Justo 9246"
    if not solo_de(JOMAX_DOM, cli):
        return "la fila no es solo de Jomax"
    cur.execute("UPDATE domicilios SET es_fiscal = 1 WHERE id = ?", (JOMAX_DOM,))
    agregar_nota(JOMAX_DOM, "Se marca como domicilio FISCAL de Jomax: ARCA informa JUSTO JUAN B AV. 9246 Dpto:A, CIUDAD AUTONOMA BUENOS AIRES (1408)")
    marcar_vinculo_fiscal(cli, JOMAX_DOM)
    return None


def medi_cient():
    cli = cliente_activo(cuit=MEDI_CUIT)
    if cli is None:
        return "el cliente no existe o esta inactivo"
    if cur.execute("SELECT 1 FROM domicilios_clientes WHERE cliente_id = ?", (cli,)).fetchone():
        return "el cliente ya tiene domicilios (no se crea otro)"
    if cur.execute("SELECT 1 FROM domicilios WHERE cliente_id = ?", (cli,)).fetchone():
        return "ya hay un domicilio de este cliente (de un vinculo que ya no esta): no se crea otro"
    if not cur.execute("SELECT 1 FROM provincias WHERE id = 'BA'").fetchone():
        return "no esta la provincia 'BA'"
    dom_id = uuid.uuid4().hex
    columnas = {r[1] for r in cur.execute("PRAGMA table_info(domicilios)")}
    valores = {"id": dom_id, "cliente_id": cli, "calle": "Caseros", "numero": "1810", "piso": "PB", "cp": "1602", "localidad": "Florida", "provincia_id": "BA",
               "es_fiscal": 1, "es_entrega": 1, "es_predeterminado": 0, "activo": 1, "is_active": 1, "bit_identidad": 1, "flags_estado": 0, "flags_infra": 0, "is_maps_manual": 0,
               "maps_link": "https://www.google.com/maps/search/?api=1&query=Caseros+1810+Florida+Buenos+Aires",
               "observaciones": nota("Medi Cient no tenia ningun domicilio; se crea el fiscal que informa ARCA (Padron A13): CASEROS 1810 PB, FLORIDA, BUENOS AIRES (1602)")}
    valores = {k: v for k, v in valores.items() if k in columnas}
    cur.execute(f"INSERT INTO domicilios ({', '.join(valores)}) VALUES ({', '.join('?' * len(valores))})", tuple(valores.values()))
    cur.execute("INSERT INTO domicilios_clientes (cliente_id, domicilio_id, flags, alias, es_predeterminado, created_at) VALUES (?, ?, 2097152, NULL, 0, datetime('now'))", (cli, dom_id))
    marcar_vinculo_fiscal(cli, dom_id)
    return None


for nombre, fn in (("GELATO SA", gelato), ("JOMAX INSUMOS HOSPITALARIOS", jomax), ("MEDI CIENT S.R.L.", medi_cient)):
    try:
        cur.execute("SAVEPOINT cli")
        motivo = fn()
        if motivo:
            saltados.append((nombre, motivo))
        else:
            hechos.append(nombre)
        cur.execute("RELEASE cli")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO cli"); cur.execute("RELEASE cli")
        errores.append((nombre, f"{type(e).__name__}: {e}"))

if errores:
    print("[migrate_062] ERROR -- algun cliente fallo (ese cliente quedo como estaba); no se registra y se reintenta en el proximo arranque")
    for n, m in errores:
        print(f"[migrate_062]   {n}: {m}")
else:
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(f"[migrate_062] OK -- clientes con domicilio fiscal corregido: {len(hechos)}; sin tocar: {len(saltados)}; {MIGRATION_ID} registrada.")
    for n in hechos:
        print(f"[migrate_062]   {n}: domicilio fiscal listo")
    for n, m in saltados:
        print(f"[migrate_062] AVISO -- {n}: {m} (queda como estaba)")
conn.close()
