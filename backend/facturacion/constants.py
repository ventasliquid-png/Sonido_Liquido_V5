# backend/facturacion/constants.py
# Genoma flags_estado — facturas (sellado Nike Arq 5.5, sesión 799-CA)

class FacturaFlags:
    # Bits 0-14: Canon base
    EXISTENCE       = 1 << 0   # 1
    HAS_ACTIVITY    = 1 << 1   # 2 — virgen(1)/tocado(0)
    HAS_REMITO      = 1 << 2   # 4
    ACTIVE          = 1 << 3   # 8 — no anulada
    # Bit 10 = V15_STRUCT (reservado global)

    # Bits 15-21: Lógica de negocio V6
    PASADO_A_PEDIDO = 1 << 15  # 32768
    EN_CUARENTENA   = 1 << 16  # 65536
    TIENE_NC        = 1 << 17  # 131072
    TIENE_ND        = 1 << 18  # 262144
    ES_NC           = 1 << 19  # 524288
    ES_ND           = 1 << 20  # 1048576
    AUDITADA        = 1 << 21  # 2097152

    # Bits 22-29: Reservado Módulo Contabilidad (retenciones)
    # Bits 30+: Ultra-reservado
