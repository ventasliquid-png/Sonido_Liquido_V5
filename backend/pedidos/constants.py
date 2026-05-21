from enum import IntFlag

class PedidoFlags(IntFlag):
    """
    Genoma 64-bit del Pedido (flags_estado).
    """
    NOTHING   = 0
    EXISTENCE = 1          # Bit 0 — existencia lógica del documento

    # --- ESTADOS DEL PEDIDO (mutuamente excluyentes) ---
    # PENDIENTE es el estado base: EXISTENCE=1 sin ningún estado activo
    ES_PRESUPUESTO  = 1 << 2   # 4      — Cotización formal, no firme
    ES_BORRADOR     = 1 << 3   # 8      — En edición, no confirmado
    ES_INTERNO      = 1 << 4   # 16     — Circuito negro activo
    ES_CUMPLIDO     = 1 << 5   # 32     — Entregado y cerrado
    # Bit 6: PEDIDO_DUPLICATE_CONFIRMED (ver abajo)
    ES_ANULADO      = 1 << 7   # 128    — Baja lógica del documento
    ES_RESERVADO    = 1 << 8   # 256    — Precio congelado pre-aumento

    # Bit 6: Operador confirmó creación a pesar de advertencia de duplicado
    PEDIDO_DUPLICATE_CONFIRMED = 64  # 2^6

    # Bit 9: Al menos una factura vinculada tuvo corrección post-ingesta
    INGESTA_CON_CORRECCION = 512  # 2^9

    # --- EVENTOS IRREVERSIBLES ---
    TIENE_DEVOLUCION    = 1 << 10  # 1024   — Devuelto total o parcial

    # Bit 12 — canon sesión 798, reubicado desde Bit 10
    NO_FISCAL_FORCE = 4096  # 2^12

    # NOTA: Bit 11 libre. Bit 13 PROHIBIDO (colisión semántica LAVIMAR).
    ORIGEN_FACTURA      = 1 << 14  # 16384  — Nació desde ingesta ARCA
    ORIGEN_RETROACTIVO  = 1 << 15  # 32768  — Creado post-hecho
    CAMBIO_A_NEGRO      = 1 << 16  # 65536  — Nació blanco, operó en negro
    CAMBIO_A_BLANCO     = 1 << 17  # 131072 — Nació negro, operó en blanco
