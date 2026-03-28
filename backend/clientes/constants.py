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
    
    # Bit 4 (16): DOC_A_PERMITTED (Paz Binaria / Fiscal V14)
    DOC_A_PERMITTED = 16
    
    # Bit 5 (32): IS_GHOST (Operaciones Ocultas / Sin Rastro)
    IS_GHOST = 32
    
    # Bit 6 (64): OC_REQUIRED (Poka-Yoke V5.9)
    # Note: Grep showed this bit used in router.py for OC check.
    OC_REQUIRED = 64

    
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
    (Legacy field mappings, kept for compatibility)
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

class DomicilioIdentity:
    """
    [V5.2.3.1 GOLD] SOBERANÍA GEOGRÁFICA (bit_identidad)
    64-bit mask for hardware-level identity classification.
    """
    ACTIVO = 1 << 0              # 1
    HISTORIAL = 1 << 1           # 2 - Registro con historia (Protección de borrado)
    FISCAL = 1 << 2              # 4 - Domicilio legal
    PROVEEDOR = 1 << 3           # 8
    TRANSPORTE = 1 << 4          # 16 - Terminal/Depósito de fletes
    PARTICULAR = 1 << 5          # 32
    HUB = 1 << 6                 # 64 - Auto-Set: Se activa si vínculos > 1
    PROPIO = 1 << 7              # 128 - Punto de Sonido Líquido S.R.L.
    RESTRICCIONES = 1 << 8       # 256 - Notas de acceso (zorrita, horarios)
    MAPS_VERIFIED = 1 << 9       # 512 - Validado manualmente
    RECEPTORIA = 1 << 10         # 1024 - Punto de retiro de terceros
    ZONA_DIFICIL = 1 << 11       # 2048 - Alerta de logística/seguridad
    SOBERANIA_GOLD = 1 << 12     # 4096 - Registro auditado y normalizado (Bit 13)

class DomicilioRelationFlags:
    """
    [V5.2.3.1 GOLD] N:M Bridge Flags (domicilios_clientes.flags)
    Classification of use for a specific relationship.
    """
    FISCAL = 1 << 0              # 1 - Este vínculo es de carácter fiscal
    ENTREGA = 2                  # Bit 1 (Value 2): Este vínculo es para entrega logística
    PREDETERMINADO = 1 << 2      # 4 - Es la opción por defecto para este cliente
    MIRROR = 1 << 21             # 2097152 - Espejo sincronizado (Bit 21)

class SystemFlags:
    """
    [DOCTRINA V14] GENOMA DE SISTEMA (Byte 0)
    """
    TERMICA = 1    # Bloqueo total (Rojo)
    ADVERTENCIA = 2 # Discrepancia (Amarillo)
    AISLAMIENTO = 4 # Sin conexión ARCA (Naranja)

