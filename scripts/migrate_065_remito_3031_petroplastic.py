"""
migrate_065_remito_3031_petroplastic.py
=======================================
S890 (21/10/2026), paquete 1 de remitos, punto 5 (Carlos: «¿Existe un remito en el sistema? Si sí, hagamos que coincida en valores con el papel»).

El 20/10 el remito 0015-00003031 (Petroplastic, pedido #137, 400 bobinas) se armó como «Retira por mostrador» porque Cruz del Sur no estaba en el padrón de
transportes: quedó ENTREGADO, con el domicilio de la oficina (Roseti 1482), sin transporte, sin bultos ni valor declarado. Ese PDF nunca se imprimió: se rehizo con el
domicilio de entrega de Petroplastic (Ruta 234 Km 16, Junín de los Andes, Neuquén), 200 bultos y $ 2.980.000,00, y Carlos lo mandó a Celtrap (proveedor), que entregó
dos palets a Cruz del Sur e imprimió ese remito. Hay UN SOLO papel con ese número. La imagen de lo impreso es
«Intercambio/remito_0015_00003031 PETROPLASTIC Junin_copia.pdf» del Silo (md5 d7b93201ef228a486549f4377a6d69fd).

QUE HACE (solo si el 0015-00003031 es el de Petroplastic, pedido #137, CUIT 30663253529):
  remitos: metodo_entrega MOSTRADOR -> FLETE_TERCERO; transporte_id -> Cruz del Sur (CUIT 30556565798, la que Tomy dio de alta el 21/10);
           domicilio_entrega_id -> el del pedido (Pellegrini 989 fiscal / Ruta 234 Km 16 de entrega); estado ENTREGADO -> EN_CAMINO (salió el 20/10; la entrega
           al cliente no está registrada); bultos 200; valor_declarado 2980000. fecha_salida NO se toca (20/10 14:28: el día en que tomó número).
  remitos_notas: una nota [SISTEMA] con lo de antes, lo de después y dónde está la imagen.
  empresas_transporte: carga la web para pedir el retiro de Cruz del Sur (https://www.cruzdelsur.com/herramientas_retiro.php, la que dio Carlos) si está vacía
           y existe la columna (migrate_064).
GUARDAS: si el 0015-00003031 no existe o no es el de Petroplastic (en D la numeración es otra), no toca nada y se registra. Si Cruz del Sur todavía no está en el
padrón, no toca nada y NO se registra (se reintenta en el próximo arranque). Si el remito ya está alineado, no lo vuelve a tocar.
NO FRENA EL ARRANQUE: es un arreglo de datos; si falla, deshace todo, avisa con ERROR y no se registra (se reintenta).

MIGRATION_ID = "065_remito_3031_petroplastic"
NRO_SESION = 890
"""
import os
import sqlite3

MIGRATION_ID = "065_remito_3031_petroplastic"
NRO_SESION = 890
NUMERO = "0015-00003031"
CUIT_CLIENTE = "30663253529"
PEDIDO = 137
CUIT_CRUZ_DEL_SUR = "30556565798"
WEB_RETIRO_CRUZ = "https://www.cruzdelsur.com/herramientas_retiro.php"
BULTOS = 200
VALOR = 2980000.0
NOTA = ("[SISTEMA] Remito alineado con el papel (S890, migrate_065). El 20/10 se armó como «Retira por mostrador» porque Cruz del Sur no estaba en el padrón: "
        "quedó ENTREGADO, con el domicilio de la oficina (Roseti 1482), sin transporte, sin bultos ni valor declarado. Ese PDF nunca se imprimió: se rehízo con el "
        "domicilio de entrega de Petroplastic (Ruta 234 Km 16, Junín de los Andes), 200 bultos y $ 2.980.000,00, y Carlos lo mandó a Celtrap (proveedor), que entregó "
        "dos palets a Cruz del Sur e imprimió este remito: hay un solo papel con este número. Ahora: transporte de terceros (Cruz del Sur), domicilio del pedido, "
        "en camino desde el 20/10, 200 bultos, valor declarado $ 2.980.000,00. Imagen de lo impreso: Silo, Intercambio/remito_0015_00003031 PETROPLASTIC Junin_copia.pdf "
        "(md5 d7b93201ef228a486549f4377a6d69fd).")

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_065] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)


def registrar(msg):
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(f"[migrate_065] {msg} {MIGRATION_ID} registrada.")


print(f"[migrate_065] Iniciando {MIGRATION_ID}...")
try:
    fila = cur.execute("""SELECT r.id, r.metodo_entrega, r.transporte_id, r.estado, p.id, p.domicilio_entrega_id, c.cuit
                          FROM remitos r JOIN pedidos p ON p.id = r.pedido_id JOIN clientes c ON c.id = p.cliente_id
                          WHERE r.numero_legal = ?""", (NUMERO,)).fetchone()
    if not fila or fila[4] != PEDIDO or "".join(ch for ch in str(fila[6] or "") if ch.isdigit()) != CUIT_CLIENTE:
        registrar(f"Nada que hacer: el {NUMERO} no existe en esta base o no es el de Petroplastic (pedido #{PEDIDO}).")
        conn.close()
        raise SystemExit(0)
    remito_id, metodo, transporte_id, estado, _, dom_pedido, _ = fila
    cruz = [r for r in cur.execute("SELECT id, cuit, nombre FROM empresas_transporte")
            if "".join(ch for ch in str(r[1] or "") if ch.isdigit()) == CUIT_CRUZ_DEL_SUR]
    if not cruz:
        print(f"[migrate_065] AVISO -- Cruz del Sur (CUIT {CUIT_CRUZ_DEL_SUR}) no está en el padrón de transportes: no se toca nada y NO se registra "
              "(se reintenta en el próximo arranque).")
        conn.close()
        raise SystemExit(0)
    cruz_id, _, cruz_nombre = cruz[0]
    if not dom_pedido:
        raise RuntimeError(f"el pedido #{PEDIDO} no tiene domicilio de entrega")
    cur.execute("BEGIN")
    if metodo == "FLETE_TERCERO" and transporte_id == cruz_id:
        print(f"[migrate_065] El {NUMERO} ya está alineado (transporte de terceros, {cruz_nombre}): no se vuelve a tocar.")
    else:
        cur.execute("""UPDATE remitos SET metodo_entrega='FLETE_TERCERO', transporte_id=?, domicilio_entrega_id=?, estado='EN_CAMINO', bultos=?, valor_declarado=?
                       WHERE id=?""", (cruz_id, dom_pedido, BULTOS, VALOR, remito_id))
        cur.execute("INSERT INTO remitos_notas (remito_id, texto, fecha) VALUES (?, ?, datetime('now', 'localtime'))", (remito_id, NOTA))
        print(f"[migrate_065] {NUMERO}: {metodo}/{estado} -> FLETE_TERCERO/EN_CAMINO con {cruz_nombre}, domicilio del pedido, {BULTOS} bultos, "
              f"valor declarado {VALOR:,.2f}; nota [SISTEMA] agregada.")
    if "web_retiro" in {r[1] for r in cur.execute("PRAGMA table_info(empresas_transporte)")}:
        n = cur.execute("UPDATE empresas_transporte SET web_retiro=? WHERE id=? AND COALESCE(TRIM(web_retiro), '')=''", (WEB_RETIRO_CRUZ, cruz_id)).rowcount
        print(f"[migrate_065] Web de retiro de {cruz_nombre}: {'cargada' if n else 'ya tenía una, no se toca'}.")
    registrar("OK --")
    cur.execute("COMMIT")
except SystemExit:
    raise
except Exception as e:  # noqa: BLE001
    try:
        cur.execute("ROLLBACK")
    except Exception:  # noqa: BLE001
        pass
    print(f"[migrate_065] ERROR -- {type(e).__name__}: {e}. Se deshizo todo y NO se registra (se reintenta en el próximo arranque). No frena el arranque.")
    conn.close()
    raise SystemExit(0)
conn.close()
