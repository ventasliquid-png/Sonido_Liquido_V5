from enum import IntFlag

class RemitoFlags(IntFlag):
    EXISTENCE        = 1 << 0   # 1     — El documento existe lógicamente
    HAS_ACTIVITY     = 1 << 1   # 2     — 1=borrador editable, 0=emitido/cerrado
    # [Etapa 1, S870-OF continuación] Renombrado de ES_LIBRE (reserva muerta sin uso, R15 fuera
    # del giro comercial, Nike S835) a CIRCUITO_ROSA: color propio del PR, independiente del
    # pedido -- el pedido puede cambiar de color después de emitido el PR, y la guarda de
    # impresión lee el color con el que el PR nació. Dictamen Nike, CONSULTA_NIKE_circuito_PR
    # puntos 3/4/6. Mismo bit, mismo valor -- ninguna fila existente lo tiene prendido hoy.
    CIRCUITO_ROSA    = 1 << 4   # 16
    V15_STRUCT       = 1 << 10  # 1024  — Reserva estructural global — intocable
    VINCULAR_PARCIAL = 1 << 11  # 2048  — R16 generado por factura parcial ARCA
    PROHIBIDO        = 1 << 13  # 8192  — Colisión LAVIMAR — intocable
    # Bit 41 — RESERVADO, NO REUTILIZAR. Fue REMITO_DESFACTURADO (T4, S868),
    # asignado por Nike por simetría con PedidoFlags.CAMBIO_A_NEGRO. Retirado en
    # S869 (commit de revert): la cicatriz existía sólo porque falta el acumulador
    # cantidad_facturada del lado fiscal. Cuando ese acumulador exista, un remito
    # desfacturado se detecta solo — no necesita bit. Código recuperable en el
    # tag t4-original.

    # [S891, Nike Sello de Oro 22/10, tres dictámenes -- CONSULTA_NIKE_genoma_remito_2026-10-22.md] Clase y estado del
    # remito en el genoma. Los calcula UNA sola función (backend/remitos/genoma.py) a partir de los hechos del remito; nadie
    # los prende a mano. CIRCUITO_ROSA (bit 4) queda DEPRECADO: lo absorbe la clase INTERNO cuando el Rosa numere por la
    # serie RI (mientras tanto el código que lo lee sigue igual).
    # CLASE (excluyente): la numeración dice el color -- Blanco y no comercial SIEMPRE 0015, Rosa SIEMPRE RI.
    RESERVADO_AJUSTE_STOCK = 1 << 29  # reservado para el futuro documento de ajustes de stock (roturas, mermas, inventario)
    EGRESO           = 1 << 30  # remito comercial 0015
    EGRESO_AVIOS     = 1 << 31  # remito no comercial 0015 (avíos, reproceso, muestras)
    INTERNO          = 1 << 32  # remito interno, serie RI (Rosa)
    # ESTADO (excluyente). «Activo» no tiene bit: tiene clase y no está ANULADO ni PERDIDO.
    EMITIDO          = 1 << 33  # tiene número (0015 o RI)
    ANULADO          = 1 << 35  # simetría con PedidoFlags.ES_ANULADO
    PERDIDO          = 1 << 36
    # LOGÍSTICA (excluyente, solo con EMITIDO). Si nadie marca nada se asume RETIRADO en la fecha de emisión.
    EN_DEPOSITO      = 1 << 37  # emitido, esperando retiro (lo marca el operador)
    RETIRADO         = 1 << 38  # salió
    RECIBIDO         = 1 << 39  # entregado / volvió la copia firmada
    # CALIFICADORES (ortogonales, irreversibles: una vez prendidos no se apagan)
    DIFERENCIA_RECEPCION = 1 << 42  # el papel volvió distinto a lo emitido (recibido != remitido)
    FUE_ANULADO      = 1 << 43  # anulado alguna vez (queda aunque se deshaga la anulación)
    IMPRESO          = 1 << 44  # impreso alguna vez (un 0015 sin este bit = salió solo con la factura)
    SALIDA_DIFERIDA  = 1 << 45  # la salida física fue posterior a la emisión
    # [S892, Nike Sello de Oro 23/10] (Ojo: son bits de RemitoFlags; el 47 de PedidoFlags es ES_KIT, otra clase.)
    CIRCULACION_ROSA = 1 << 46  # un 0015 de un pedido Rosa (cuando lo despacha un transporte hace falta un remito de verdad): nace EGRESO + este bit; no se factura
    SALIDA_CONFIRMADA = 1 << 47  # una persona (o la guía del transporte, o la copia firmada) confirmó que salió; sin el bit, la salida es la asumida al emitir


MASCARA_CLASE = int(RemitoFlags.EGRESO | RemitoFlags.EGRESO_AVIOS | RemitoFlags.INTERNO)
MASCARA_ESTADO = int(RemitoFlags.EMITIDO | RemitoFlags.ANULADO | RemitoFlags.PERDIDO)
MASCARA_LOGISTICA = int(RemitoFlags.EN_DEPOSITO | RemitoFlags.RETIRADO | RemitoFlags.RECIBIDO)


# [S876, PROMPT 2026-09-30_NS_implementar_remito_renglon_S875, Nike "Sello de Oro" en tres
# rondas] Cómo SALIÓ físicamente la mercadería de ESTE remito. Es el hecho fáctico de esa entrega
# puntual, congelado al crear el Remito (igual que RemitoFlags.CIRCUITO_ROSA): nunca se relee en
# vivo de Domicilio ni de Pedido. No es la configuración habitual de una dirección: esa es
# Domicilio.metodo_entrega / origen_logistico (V5.2 GOLD, clientes/models.py), otra capa, que no
# se toca ni se fusiona con esta. NULL = remito anterior a esta capa (no se inventa retroactivo).
class MetodoEntrega:
    MOSTRADOR         = "MOSTRADOR"          # retiro en planta: sin traslado, sin transporte
    FLETE_TERCERO     = "FLETE_TERCERO"      # el transportista termina la entrega
    TRANSPORTE_PROPIO = "TRANSPORTE_PROPIO"
    MOTO_CADETERIA    = "MOTO_CADETERIA"
    REMITO_EXTERNO    = "REMITO_EXTERNO"     # viaja con el remito/etiqueta de un tercero (correo, MercadoLibre)

METODOS_ENTREGA = (
    MetodoEntrega.MOSTRADOR,
    MetodoEntrega.FLETE_TERCERO,
    MetodoEntrega.TRANSPORTE_PROPIO,
    MetodoEntrega.MOTO_CADETERIA,
    MetodoEntrega.REMITO_EXTERNO,
)

# Con estos métodos no interviene una empresa de transporte de terceros: Remito.transporte_id
# puede quedar NULL (migrate_047). Con FLETE_TERCERO (o sin método, el camino de siempre) sigue
# siendo obligatorio.
METODOS_SIN_TRANSPORTE = (
    MetodoEntrega.MOSTRADOR,
    MetodoEntrega.TRANSPORTE_PROPIO,
    MetodoEntrega.MOTO_CADETERIA,
    MetodoEntrega.REMITO_EXTERNO,
)


# [S876] Por qué un RENGLÓN salió sin ser una venta firme. Vive en RemitoItem, no en Remito ni en
# Pedido: un mismo remito puede llevar renglones de venta firme y uno en consignación a la vez.
# NULL = facturable normal. Un renglón con motivo nace con cantidad_facturada NULL ("no aplica
# todavía", dictamen Nike 23/09: NULL != 0) y se resuelve FACTURAR (motivo vuelve a NULL y el
# renglón entra al camino normal) o con una devolución (PR de cantidad negativa, Etapa 6).
class MotivoNoFacturable:
    CONSIGNACION       = "CONSIGNACION"
    MUESTRA_SIN_CARGO  = "MUESTRA_SIN_CARGO"
    GARANTIA_REEMPLAZO = "GARANTIA_REEMPLAZO"

MOTIVOS_NO_FACTURABLE = (
    MotivoNoFacturable.CONSIGNACION,
    MotivoNoFacturable.MUESTRA_SIN_CARGO,
    MotivoNoFacturable.GARANTIA_REEMPLAZO,
)

# Riesgo "Consignación Eterna" (mercadería a prueba que se olvida sin resolver): pedido de Nike,
# alerta a los 30 días de antigüedad para todo renglón con motivo abierto -- Informes.
DIAS_ALERTA_NO_FACTURABLE = 30

# [S893, Carlos 26/10] Por qué lo que quedó de un renglón es menos de lo que figuraba en el remito. Con una de estas causas el servidor arma una CORRECCIÓN
# (un renglón de cantidad negativa, el mecanismo de la devolución de la Etapa 6, atado al renglón de origen): el pedido vuelve a deber la diferencia y, si estaba
# CUMPLIDO, se reabre. La causa queda guardada para Stock: VOLVIO suma al stock; NO_SALIO, SE_PERDIO y SE_RECHAZO no.
class CausaCorreccion:
    NO_SALIO   = "NO_SALIO"     # el remito dice más de lo que realmente salió
    SE_PERDIO  = "SE_PERDIO"    # salió y se perdió en el camino
    SE_RECHAZO = "SE_RECHAZO"   # llegó y el cliente no lo aceptó
    VOLVIO     = "VOLVIO"       # llegó y después volvió (devolución del cliente)

CAUSAS_CORRECCION = (
    CausaCorreccion.NO_SALIO,
    CausaCorreccion.SE_PERDIO,
    CausaCorreccion.SE_RECHAZO,
    CausaCorreccion.VOLVIO,
)

# Con estas causas lo que QUEDÓ es lo que llegó (cantidad_recibida del renglón de origen = lo que quedó). Con VOLVIO llegó todo y después volvió una parte.
CAUSAS_QUE_CAMBIAN_LO_QUE_LLEGO = (CausaCorreccion.NO_SALIO, CausaCorreccion.SE_PERDIO, CausaCorreccion.SE_RECHAZO)

ETIQUETA_CAUSA = {
    CausaCorreccion.NO_SALIO: "No salió todo",
    CausaCorreccion.SE_PERDIO: "Se perdió",
    CausaCorreccion.SE_RECHAZO: "Se rechazó",
    CausaCorreccion.VOLVIO: "Volvió",
}

# [S893, Carlos 26/10; Nike Sello de Oro 26/10: bit 48 de PedidoFlags] QUIÉN CARGA CON LA PÉRDIDA. Lo decide el PEDIDO: FLETE_A_CARGO_NUESTRO prendido = el flete es nuestro (vehículo o moto nuestros,
# o un transporte que pagamos nosotros): la pérdida en el camino es nuestra, se factura lo que llegó y el pedido vuelve a deber. Apagado (el normal, y el de todos los pedidos viejos) el flete es del
# cliente (retira, su transporte, su moto, su plataforma): lo entregado a su transporte ya es suyo, lo que se pierde es un reclamo suyo, se factura lo que salió y el pedido NO vuelve a deber.
# Además, un remito que salió con TRANSPORTE_PROPIO (nuestro vehículo) es nuestro aunque el bit no esté prendido. «Moto / cadetería» ya no dice nada por sí sola: la moto que manda el cliente es suya.
# Solo afecta a SE_PERDIO: NO_SALIO, SE_RECHAZO y VOLVIO mueven siempre.
METODOS_RIESGO_PROPIO = (
    MetodoEntrega.TRANSPORTE_PROPIO,
)


def riesgo_de_la_entrega(metodo_entrega, pedido_flags=0) -> str:
    """'PROPIO' si la pérdida en el camino es nuestra (el pedido tiene prendido FLETE_A_CARGO_NUESTRO, bit 48, o el remito salió con nuestro vehículo); 'COMPRADOR' en cualquier otro caso."""
    if int(pedido_flags or 0) & (1 << 48):   # PedidoFlags.FLETE_A_CARGO_NUESTRO (no se importa para no cruzar módulos en el arranque)
        return "PROPIO"
    return "PROPIO" if (metodo_entrega or "").strip().upper() in METODOS_RIESGO_PROPIO else "COMPRADOR"


# [S895, Carlos 29/10] Talonarios. El 0015 es el talonario fiscal de hoy; el RI (remito interno, circuito no formal) es OTRO talonario: «RI01» + 8 dígitos, como
# «0015-00003034» (punto de venta + número). Con dos dígitos hay 99 talonarios de RI (un depósito de salida más, otro talonario «RI02»); las letras lo distinguen de un
# punto de venta fiscal a simple vista y en una fotocopia. El genoma lee la clase del prefijo; «RI-» (sin talonario) se sigue entendiendo por compatibilidad.
import re as _re
TALONARIO_RI = "RI01"
_RE_NUMERO_RI = _re.compile(r"^RI(\d{2})?-")


def es_numero_ri(numero) -> bool:
    """True si el número es de la serie RI (remito interno): «RI01-00000001», o el viejo «RI-00000001»."""
    return bool(numero) and bool(_RE_NUMERO_RI.match(str(numero)))

