# Archivo: backend/clientes/constants.py

class ClientFlags:
    """
    [DOCTRINA V14] ENIGMA BLUEPRINT
    Bitmask Constants for 'flags_estado' (32-bit Integer).
    """
    
    # Bit 0 (1): EXISTENCE
    # El registro existe físicamente en la DB. (Equivale a 'activo' legacy si es 1)
    EXISTENCE = 0x001
    IS_ACTIVE = 0x001 # Alias legacy para service.py
    
    # Bit 1 (2): VIRGINITY
    # 1: Virgen (Sin movimientos) / 0: Activo (Tiene remitos/facturas).
    VIRGINITY = 0x002
    IS_VIRGIN = 0x002 # Alias legacy
    
    # Bit 2 (4): GOLD_ARCA
    # El dato fue homologado por el satélite RAR (ARCA).
    GOLD_ARCA = 0x004
    FISCAL_REQUIRED = 0x004 # Alias funcional para service.py
    
    # Bit 3 (8): V14_STRUCT
    # El registro cumple con la arquitectura de 32 bits Genoma V14.
    V14_STRUCT = 0x008
    
    # Bit 4 (16): OPERATOR_OK
    # Sello Rosa: Validado manualmente por el operador.
    OPERATOR_OK = 0x010
    
    # Bit 5 (32): MULTI_CUIT
    # Sello Azul: CUIT compartido (UBA, Sedes, etc.).
    MULTI_CUIT = 0x020

    # --- FLAGS COMPLEMENTARIOS ---
    # (Reservados para futuras expansiones del Genoma)
    CREDIT_HOLD = 0x040
    INTERNAL_USE = 0x080
