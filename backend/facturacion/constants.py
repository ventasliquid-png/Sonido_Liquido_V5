# backend/facturacion/constants.py
# Genoma flags_estado — facturas (sellado Nike Arq 5.5, sesión 799-CA)

class FacturaFlags:
    # Bits 0-14: Canon base
    EXISTENCE       = 1 << 0   # 1
    IS_VIRGIN       = 1 << 1   # 2 — virgen(1)/tocado(0)
    HAS_REMITO      = 1 << 2   # 4
    ACTIVE          = 1 << 3   # 8 — no anulada
    
    # [V5.9 GOLD] Nuevos Bits Sellados
    CORRECCION_OCR      = 1 << 9   # 512
    V15_STRUCT          = 1 << 10  # 1024 (Reservado)
    DISCREPANCIA_FISCAL = 1 << 11  # 2048
    
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

    # [Etapa 7d, dictamen Nike 29/09 "¿Cómo se modela NC/ND..."] Los cuatro bits 17-20 los
    # mantiene FacturacionService (no solo se derivan): se recalculan desde facturas_ajustes en cada
    # alta/reversión. ES_NC/ES_ND marcan a la fila misma (tipo NOTA_CREDITO_*/NOTA_DEBITO_*);
    # TIENE_NC/TIENE_ND marcan a la factura ajustada. OJO: existe un TIENE_NC distinto en
    # backend/ingesta/constants.py (Bit 2, flags de FacturasProcesadas) -- otro namespace, no
    # colisiona, pero no son la misma bandera.


def es_nota_credito(tipo_comprobante) -> bool:
    """NOTA_CREDITO_A/B/C/M y las FCE (NOTA_CREDITO_FCE_A...) -- los tipos canónicos del parser (7a)."""
    return (tipo_comprobante or "").startswith("NOTA_CREDITO")


def es_nota_debito(tipo_comprobante) -> bool:
    return (tipo_comprobante or "").startswith("NOTA_DEBITO")


def es_nota_ajuste(tipo_comprobante) -> bool:
    return es_nota_credito(tipo_comprobante) or es_nota_debito(tipo_comprobante)
