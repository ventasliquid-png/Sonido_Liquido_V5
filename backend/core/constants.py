# --- [V5-X] SYSTEM FLAGS & BITMASKS (UNIVERSAL 4 BYTES) ---
# Centralized definition for 32-bit Integer Flags

# --- CLIENTES (0x01) ---
CLIENTE_IS_ACTIVE = 1 << 0       # 0x01: Cliente activo en sistema
CLIENTE_FISCAL_REQUIRED = 1 << 2 # 0x04: Requiere validación fiscal estricta (Gold/Silver)
CLIENTE_REQUIRES_AUDIT = 1 << 3  # 0x08: Marcado para auditoría manual
CLIENTE_ACCOUNT_BLOCKED = 1 << 4 # 0x10: Cuenta bloqueada por administración
CLIENTE_PAYMENT_PENDING = 1 << 5 # 0x20: Tiene pagos pendientes críticos
CLIENTE_HAS_OPEN_CLAIMS = 1 << 6 # 0x40: Tiene reclamos abiertos
# RESERVED: 1<<7 to 1<<31

# --- PRODUCTOS (0x02) ---
PRODUCTO_IS_ACTIVE = 1 << 0      # 0x01: Producto vendible
PRODUCTO_STOCK_CONTROL = 1 << 1  # 0x02: Control de stock estricto
PRODUCTO_IS_VISIBLE = 1 << 2     # 0x04: Visible en listas públicas/web
PRODUCTO_CRITICAL_ITEM = 1 << 3  # 0x08: Artículo crítico (Alerta de stock bajo)
PRODUCTO_IS_KIT = 1 << 4         # 0x10: Es un combo/kit
PRODUCTO_ALLOW_NEGATIVE = 1 << 5 # 0x20: Permite stock negativo temporal
PRODUCTO_REQUIRES_BATCH = 1 << 6 # 0x40: Requiere lote/vencimiento
# RESERVED: 1<<7 to 1<<31

# --- PEDIDOS (0x03) ---
PEDIDO_IS_URGENT = 1 << 0        # 0x01: Pedido urgente
PEDIDO_PAYMENT_VALIDATED = 1 << 1# 0x02: Pago verificado
PEDIDO_TRACEABILITY = 1 << 2     # 0x04: Trazabilidad requerida
PEDIDO_DISPATCH_RELEASED = 1 << 3# 0x08: Liberado para despacho (Logística)
PEDIDO_REQUIRES_INVOICE = 1 << 4 # 0x10: Requiere factura fiscal obligatoria
PEDIDO_IS_PICKUP = 1 << 5        # 0x20: Retiro en local (No envío)
PEDIDO_HAS_NOTES = 1 << 6        # 0x40: Tiene notas internas importantes
# RESERVED: 1<<7 to 1<<31

# --- CONTACTOS / VINCULOS (0x04) ---
CONTACTO_IS_ACTIVE = 1 << 0      # 0x01: Contacto activo
CONTACTO_IS_PRIMARY = 1 << 1     # 0x02: Contacto principal de la cuenta
CONTACTO_IDENTITY_OK = 1 << 2    # 0x04: Identidad validada
CONTACTO_WHATSAPP_OK = 1 << 3    # 0x08: Recibe WhatsApp
CONTACTO_EMAIL_OK = 1 << 4       # 0x10: Recibe Email
# RESERVED: 1<<5 to 1<<31

# --- TRANSPORTES (0x05) ---
TRANSPORTE_IS_ACTIVE = 1 << 0    # 0x01: Transporte activo
TRANSPORTE_REQ_WEB = 1 << 1      # 0x02: Requiere carga en web externa
TRANSPORTE_HAS_TRACKING = 1 << 2 # 0x04: Tiene tracking online
TRANSPORTE_HOME_PICKUP = 1 << 3  # 0x08: Realiza retiro a domicilio
TRANSPORTE_REQ_LABEL = 1 << 4    # 0x10: Requiere etiqueta impresa específica

# --- DOMICILIOS: IDENTIDAD (0x06) ---
DOM_ACTIVO = 1 << 0              # 0x01
DOM_HISTORIAL = 1 << 1           # 0x02 - Registro con historia (Protección de borrado)
DOM_FISCAL = 1 << 2              # 0x04 - Domicilio Legal
DOM_PROVEEDOR = 1 << 3           # 0x08
DOM_TRANSPORTE = 1 << 4          # 0x10 - Terminal/Depósito de fletes
DOM_PARTICULAR = 1 << 5          # 0x20
DOM_HUB = 1 << 6                 # 0x40 - Multi-vínculo (>1)
DOM_PROPIO = 1 << 7              # 0x80 - Punto de Sonido Líquido S.R.L.
DOM_RESTRICCIONES = 1 << 8       # 0x100 - Notas de acceso (zorrita, horarios)
DOM_MAPS_VERIFIED = 1 << 9       # 0x200 - Validado manualmente
DOM_RECEPTORIA = 1 << 10         # 0x400 - Punto de retiro de terceros
DOM_ZONA_DIFICIL = 1 << 11       # 0x800 - Alerta de logística/seguridad
DOM_SOBERANIA_GOLD = 1 << 12     # 0x1000 - Registro auditado y normalizado (Bit 13)

# --- DOMICILIOS: INFRAESTRUCTURA (0x07) ---
DOM_INFRA_RAMPA = 1 << 0         # 0x01
DOM_INFRA_DOCK = 1 << 1          # 0x02
DOM_INFRA_ASCENSOR = 1 << 2      # 0x04
