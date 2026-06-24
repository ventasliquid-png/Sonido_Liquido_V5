from enum import IntFlag

class PedidoFlags(IntFlag):
    """
    Genoma 64-bit del Pedido V6 — canonizado por Nike Arq 5.5
    Banda baja reservada para bits universales y Motor Bipolar.
    Banda 32+ para ciclo de vida y auditoría forense del pedido.
    """
    NOTHING      = 0
    EXISTENCE    = 1 << 0   # Bit 0 — existencia lógica
    HAS_ACTIVITY = 1 << 1   # Bit 1 — Ley Universal: marca de actividad/virginidad. Bit 1 no está libre en ninguna entidad del sistema.

    # Bits bajos preexistentes — INTOCABLES
    PEDIDO_DUPLICATE_CONFIRMED = 1 << 6   # Bit 6
    INGESTA_CON_CORRECCION     = 1 << 9   # Bit 9
    NO_FISCAL_FORCE            = 1 << 12  # Bit 12 — Motor Bipolar soberano
    # Bit 13 PROHIBIDO — colisión LAVIMAR
    # Bit 20 — Pedido tiene ítems con entrega parcial pendiente.
    # Se enciende automáticamente al crear remito que no cubre el total de algún ítem.
    # Se apaga cuando todos los ítems están cubiertos al 100%. Canonizado Nike S833.
    HAS_PARTIAL_DELIVERY = 1 << 20
    # Bit 21 — Entrega física completa. Se enciende cuando TODOS los ítems tienen
    # cantidad_entregada >= cantidad. Se apaga si se anula un remito y vuelve a haber pendiente.
    # Canonizado Nike S833.
    FULL_DELIVERED = 1 << 21
    # Bit 40 PROHIBIDO — DISCRIMINA_IVA del cliente

    # BANDA 32+ — Estados mutuamente excluyentes
    # Patrón obligatorio en toda transición:
    # flags = (flags & ~STATE_MASK) | ES_NUEVO_ESTADO
    ES_PRESUPUESTO  = 1 << 32  # Cotización formal, sin color aún
    ES_FIRME        = 1 << 33  # Pedido confirmado (blanco o negro)
    ES_CUMPLIDO     = 1 << 34  # Entregado y cerrado
    ES_ANULADO      = 1 << 35  # Baja lógica del documento

    # BANDA 32+ — Flags ortogonales acumulables
    RESERVA_STOCK      = 1 << 36  # Stock comprometido desde presupuesto
    TUVO_CIRCUITO      = 1 << 37  # Forense: tuvo vida operativa real
    ORIGEN_FACTURA     = 1 << 38  # Nació desde ingesta ARCA
    ORIGEN_RETROACTIVO = 1 << 39  # Creado post-hecho
    # Bit 40 PROHIBIDO
    CAMBIO_A_NEGRO     = 1 << 41  # Cicatriz: nació blanco, operó negro
    CAMBIO_A_BLANCO    = 1 << 42  # Cicatriz: nació negro, operó blanco
    PEDIDO_GHOST       = 1 << 43  # Bit 43 — operado sin rastro (auditoría)

# Máscara de estados excluyentes
STATE_MASK = (
    PedidoFlags.ES_PRESUPUESTO |
    PedidoFlags.ES_FIRME       |
    PedidoFlags.ES_CUMPLIDO    |
    PedidoFlags.ES_ANULADO
)
