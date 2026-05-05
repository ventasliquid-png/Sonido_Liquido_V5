class RemitoFlags:
    EXISTENCE    = 1    # Bit 0 — existe en el sistema
    TIENE_FAC    = 2    # Bit 1 — tiene factura asociada
    ES_PARCIAL   = 4    # Bit 2 — es uno de varios remitos de una factura
    ES_CIERRE    = 8    # Bit 3 — completa la entrega de la factura
    EN_CUARENTENA = 16  # Bit 4 — requiere revisión supervisor
