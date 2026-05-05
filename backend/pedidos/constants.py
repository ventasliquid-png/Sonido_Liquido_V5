from enum import IntFlag

class PedidoFlags(IntFlag):
    """
    Genoma 64-bit del Pedido (flags_estado).
    """
    NOTHING = 0
    EXISTENCE = 1
    
    # ... otros bits intermedios reservados para V5.9 ...

    # Bit 10: Obligar a salir del flujo fiscal (No informar a ARCA)
    NO_FISCAL_FORCE = 1024 # 2^10
