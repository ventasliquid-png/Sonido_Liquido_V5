class FacturaFlags:
    EXISTENCE       = 1    # Bit 0 — existe en el sistema
    TIENE_REMITO    = 2    # Bit 1 — al menos un remito asociado
    CONTABILIZADA   = 4    # Bit 2 — entró a contabilidad
    EN_CUARENTENA   = 8    # Bit 3 — requiere revisión supervisor
    TIENE_NC        = 16   # Bit 4 — Nota de Crédito vinculada
    TIENE_ND        = 32   # Bit 5 — Nota de Débito vinculada
    TIENE_RECIBO    = 64   # Bit 6 — cancelada con recibo
    AUDITADA        = 128  # Bit 7 — revisada por supervisor
    ENTREGA_PARCIAL = 256  # Bit 8 — más de un remito, entrega incompleta
