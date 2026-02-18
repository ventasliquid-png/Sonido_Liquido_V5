# Archivo: backend/clientes/constants.py

class ClientFlags:
    """
    Bitmask Constants for 'flags_estado' (32-bit Integer).
    Strategically mapped for V5-X Hybrid Architecture.
    """
    
    # 0x01: Baja Lógica (Soft Delete). 
    # Si está en 0, el cliente está "Borrado". Si está en 1, está "Activo".
    # (Reemplaza al booleano 'activo' legacy)
    IS_ACTIVE = 0x001 
    
    # 0x02: Virginidad (Integridad Referencial).
    # 1 = Nunca ha operado (Sin pedidos, sin deuda). Seguro para Hard Delete.
    # 0 = Ya tiene historia. Solo permite Soft Delete.
    IS_VIRGIN = 0x002
    
    # 0x04: Switch Bronze/Gold (Fiscal Requirement).
    # 0 = Bronze (Informal/Mostrador). No exige CUIT ni Domicilio Fiscal.
    # 1 = Gold/Silver. Exige CUIT válido y Domicilio Fiscal.
    FISCAL_REQUIRED = 0x004
    
    # 0x08: Validación Externa (ARCA/AFIP).
    # 1 = Datos validados contra padrón oficial (Golden Record).
    # 0 = Datos declarativos o inventados.
    ARCA_VALIDATED = 0x008
    
    # 0x10: Habilitación Fiscal (Tipo de Factura).
    # 1 = Puede emitir Factura A (RI).
    # 0 = Solo B o X (Monotributo/Consumidor Final/Informal).
    DOC_A_PERMITTED = 0x010
    
    # 0x20: Estado Fantasma (Pre-Alta).
    # 1 = Carga rápida de Tomás. Invisible para el resto del sistema.
    # 0 = Cliente confirmado y visible.
    IS_GHOST = 0x020
    
    # 0x40: Bloqueo Financiero.
    CREDIT_HOLD = 0x040
    
    # 0x80: Uso Interno (Sucursal, Gastos).
    INTERNAL_USE = 0x080
