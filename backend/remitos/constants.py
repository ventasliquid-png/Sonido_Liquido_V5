from enum import IntFlag

class RemitoFlags(IntFlag):
    EXISTENCE        = 1 << 0   # 1     — El documento existe lógicamente
    HAS_ACTIVITY     = 1 << 1   # 2     — 1=borrador editable, 0=emitido/cerrado
    ES_LIBRE         = 1 << 4   # 16    — R15 fuera del giro comercial (Nike S835)
    V15_STRUCT       = 1 << 10  # 1024  — Reserva estructural global — intocable
    VINCULAR_PARCIAL = 1 << 11  # 2048  — R16 generado por factura parcial ARCA
    PROHIBIDO        = 1 << 13  # 8192  — Colisión LAVIMAR — intocable
