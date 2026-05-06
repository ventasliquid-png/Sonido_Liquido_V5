# backend/productos/constants.py
# [DOCTRINA V15] GENOMA SOBERANO DE PRODUCTOS — 64-bit
# Desacoplado de ClientFlags para soberanía de dominio.

class ProductoFlags:
    """
    Bitmask de 64 bits para el campo flags_estado de Producto.
    Cada bit tiene semántica propia del dominio de productos.
    """
    # --- Nibble Bajo (Identity DNA) ---
    # Bit 0 (1): EXISTENCIA / ACTIVO
    EXISTENCE = 1
    IS_ACTIVE = 1

    # Bit 1 (2): 0=virgen/borrable, 1=tocado/bloqueado
    HAS_ACTIVITY = 2

    # Bit 2 (4): GOLD_CATALOGADO (Producto auditado y normalizado)
    GOLD_CATALOGED = 4

    # Bit 3 (8): EXPATRIADO (Producto refugiado en General por baja de rubro)
    EXPATRIADO = 8

    # Bit 10 (1024): ESTRUCTURA V15 (Creado bajo protocolo V15)
    V15_STRUCT = 1024

    # --- Nibble Alto (Operaciones) ---
    # Bit 4 (16): TIENE_COSTO (Costo de reposición cargado)
    HAS_COST = 16

    # Bit 5 (32): TIENE_PROVEEDOR (Proveedor habitual asignado)
    HAS_SUPPLIER = 32

    # Bit 6 (64): KIT (Es un producto compuesto)
    IS_KIT = 64

    # Bit 7 (128): STOCK_CONTROLADO (Participa en control de stock)
    STOCK_MANAGED = 128

    # --- Byte 1 (Fiscal / Logística) ---
    # Bit 8 (256): IVA_ASIGNADO
    IVA_ASSIGNED = 256

    # Bit 9 (512): PRESENTACION_DEFINIDA
    PACKAGING_DEFINED = 512

    # --- Byte 2+ (Auditoría) ---
    # Bit 20 (1048576): PENDIENTE_REVISION
    PENDIENTE_REVISION = 1 << 20

