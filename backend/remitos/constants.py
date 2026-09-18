from enum import IntFlag

class RemitoFlags(IntFlag):
    EXISTENCE        = 1 << 0   # 1     — El documento existe lógicamente
    HAS_ACTIVITY     = 1 << 1   # 2     — 1=borrador editable, 0=emitido/cerrado
    ES_LIBRE         = 1 << 4   # 16    — R15 fuera del giro comercial (Nike S835)
    V15_STRUCT       = 1 << 10  # 1024  — Reserva estructural global — intocable
    VINCULAR_PARCIAL = 1 << 11  # 2048  — R16 generado por factura parcial ARCA
    PROHIBIDO        = 1 << 13  # 8192  — Colisión LAVIMAR — intocable

    # [T4, S868 — dictamen de Nike, 18/09] Cicatriz forense irreversible: distingue "nació no
    # facturable" de "estuvo facturado y se desfacturó" (NC financiera / anulación comercial —
    # "hacéme NC y te lo pago en negro"). Se enciende una sola vez y no se apaga nunca. El vínculo
    # a la factura anulada NO se borra (trazabilidad); el remito vuelve solo a estado pendiente.
    # Bit 41 por simetría exacta con PedidoFlags.CAMBIO_A_NEGRO (también Bit 41) — asignado por
    # Nike, no por lectura propia de este archivo (precedente Card #106/S863: eso salió mal).
    REMITO_DESFACTURADO = 1 << 41  # 2199023255552
