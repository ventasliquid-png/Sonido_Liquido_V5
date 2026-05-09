# backend/ingesta/constants.py
# Genoma flags_estado — Ingesta (sellado Nike Arq 5.5, sesión 800-CA)

class IngestaFlags:
    # --- GENOMA RAW (ingesta_facturas_raw.flags_estado) ---
    RAW_EXISTENCE       = 1 << 0   # 1
    RAW_EN_CUARENTENA   = 1 << 2   # 4

    # --- GENOMA PRC (ingesta_facturas_procesadas.flags_estado) ---
    EXISTENCE           = 1 << 0   # 1
    HAS_ACTIVITY        = 1 << 1   # 2
    TIENE_NC            = 1 << 2   # 4
    TIENE_ND            = 1 << 3   # 8
    AUDITADA            = 1 << 4   # 16
    VINCULADA_PEDIDO    = 1 << 5   # 32
    RAW_CON_PROBLEMAS   = 1 << 6   # 64
    SIN_STOCK           = 1 << 7   # 128
    SIN_AUTORIZACION_CC = 1 << 8   # 256
    CORRECCION_OCR      = 1 << 9   # 512
    PROHIBIDO_V15       = 1 << 10  # 1024
    DISCREPANCIA_FISCAL = 1 << 11  # 2048
    PROHIBIDO_LAVIMAR   = 1 << 13  # 8192
