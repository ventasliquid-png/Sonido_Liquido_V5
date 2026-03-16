# Archivo: backend/clientes/constants.py

class ClientFlags:
    """
    [DOCTRINA V14] GENOMA MASTER - PIN 1974
    Suma de Potencias de 2 - Nibble Bajo (Identity DNA)
    """
    # Bit 0 (1): ACTIVO / EXISTENCIA
    EXISTENCE = 1
    IS_ACTIVE = 1 
    
    # Bit 1 (2): VIRGINIDAD (1 = Virgen / 0 = Operado)
    VIRGINITY = 2
    IS_VIRGIN = 2
    
    # Bit 2 (4): GOLD_ARCA (Validado por Satélite)
    GOLD_ARCA = 4
    FISCAL_REQUIRED = 4
    
    # Bit 3 (8): ESTRUCTURA V14 (Protocolo Apolo)
    V14_STRUCT = 8
    
    # Bit 4 (16): SABUESO_ALERT (Alerta de líos/deudas)
    SABUESO_ALERT = 16
    
    # --- [NIVELES COMBINADOS] ---
    LEVEL_NEW = 15    # 1+2+4+8 (Virgen Validado V14)
    LEVEL_HISTORY = 13 # 1+4+8 (Operado Validado V14)
    # Pao de Tandil: 9 (Histórico) / 11 (Nuevo)
    
    # --- [AUDITORÍA Y UX] ---
    # Bit 20 (1048576): PENDIENTE_REVISION (Color Amarillo)
    PENDIENTE_REVISION = 1 << 20
    
    # --- [MARKETING DNA] (Acquisition 30-34) ---
    CH_TIENDANUBE = 1 << 30
    CH_MLIBRE = 1 << 31

class DomicilioFlags:
    """
    [DOCTRINA V14] GENOMA MASTER - INDEPENDENCIA GEOGRÁFICA
    """
    ACTIVO = 1
    CONFLICTO = 2
    ORO_FISCAL = 4
    ORO_CURADO = 8
    LOGISTICA = 16
    
    # Estados de Operación
    VERDE_ARCA = 21   # 16+4+1
    VERDE_MANUAL = 25 # 16+8+1
    ORO_TOTAL = 29    # 16+8+4+1
    AMARILLO = 23    # 16+4+2+1 (Conflicto)

class SystemFlags:
    """
    [DOCTRINA V14] GENOMA DE SISTEMA (Byte 0)
    """
    TERMICA = 1    # Bloqueo total (Rojo)
    ADVERTENCIA = 2 # Discrepancia (Amarillo)
    AISLAMIENTO = 4 # Sin conexión ARCA (Naranja)

