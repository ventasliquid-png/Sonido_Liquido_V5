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

    # Bit 10: Obligar a salir del flujo fiscal (No informar a ARCA)
    NO_FISCAL_FORCE = 1024 # 2^10
