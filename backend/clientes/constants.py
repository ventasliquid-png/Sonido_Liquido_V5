# Archivo: backend/clientes/constants.py

class ClientFlags:
    """
    [DOCTRINA V14] ENIGMA BLUEPRINT
    Bitmask Constants for 'flags_estado' (64-bit Integer - Genoma 64).
    """
    
    # Bit 0 (1): EXISTENCE
    # El registro existe físicamente en la DB. (Equivale a 'activo' legacy si es 1)
    EXISTENCE = 1 << 0
    IS_ACTIVE = 1 << 0 # Alias legacy para service.py
    
    # Bit 2 (4): GOLD_ARCA
    # El dato fue homologado por el satélite RAR (ARCA).
    GOLD_ARCA = 1 << 2
    FISCAL_REQUIRED = 1 << 2 # Alias funcional para service.py
    
    # Bit 3 (8): V14_STRUCT
    # El registro cumple con la arquitectura de 64 bits Genoma V14.
    V14_STRUCT = 1 << 3
    
    # Bit 4 (16): OPERATOR_OK
    # Sello Rosa: Validado manualmente por el operador.
    OPERATOR_OK = 1 << 4
    
    # --- [CANON VANGUARD] ESTRUCTURA JERÁRQUICA 64-BIT ---
    
    # Bit 13 (8192): HISTORIA
    # Sello de Vida: El cliente ya tiene movimientos reales (Facturas/Remitos).
    HISTORIA = 1 << 13
    
    # Bit 15 (32768): VIRGINITY
    # 1: Virgen (Sin movimientos) / 0: Ya desvirgado.
    VIRGINITY = 1 << 15
    IS_VIRGIN = 1 << 15 # Alias funcional
    
    # Bit 16 (65536): MULTI_DESTINO
    # Se activa si el cliente tiene múltiples direcciones de entrega.
    MULTI_DESTINO = 1 << 16
    
    # Bit 20 (1048576): PENDIENTE_REVISION
    # El cliente nació "amarillo" (faltan datos operativos como Segmento o Lista).
    PENDIENTE_REVISION = 1 << 20

    # --- [CANALES DE MARKETING] (Acquisition DNA 30-34) ---
    CH_TIENDANUBE = 1 << 30
    CH_MLIBRE = 1 << 31
    CH_GOOGLE = 1 << 32
    CH_RRSS = 1 << 33  # Instagram / Facebook Unified
    CH_TIKTOK = 1 << 34
