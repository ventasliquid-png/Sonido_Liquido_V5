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
