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
