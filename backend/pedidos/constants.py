from enum import IntFlag

class PedidoFlags(IntFlag):
    """
    Genoma 64-bit del Pedido (flags_estado).
    """
    NOTHING = 0
    EXISTENCE = 1
    
    # ... otros bits intermedios reservados para V5.9 ...

    # Bit 6: Operador confirmó creación a pesar de advertencia de duplicado
    PEDIDO_DUPLICATE_CONFIRMED = 64  # 2^6

    # Bit 9: Al menos una factura vinculada tuvo corrección post-ingesta
    INGESTA_CON_CORRECCION = 512 # 2^9

    # Bit 12 — canon sesión 798, reubicado desde Bit 10
    NO_FISCAL_FORCE = 4096 # 2^12
