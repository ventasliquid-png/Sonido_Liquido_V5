# [IDENTIDAD] - backend\contactos\constants.py
# Versión: V5.6 GOLD
# ---------------------------------------------------------

# Genoma de Vinculo.flags_estado -- Dictamen Nike 20260908, enmendado 20260909 (v2).
# Bits 0-1 son la Ley Universal (EXISTENCE / IS_VIRGIN), reservados en TODA entidad
# del sistema -- nunca redefinir acá. Roles de contacto acotados a bits 2-6 (Bit 7
# IS_BANNED fue erradicado por duplicar la columna Vinculo.activo ya existente).


class VinculoFlags:
    EXISTENCE = 1 << 0   # Bit 0 -- Ley Universal, registro activo logicamente
    IS_VIRGIN = 1 << 1   # Bit 1 -- Ley Universal, 1=virgen (borrado fisico permitido)

    IS_PRIMARY = 1 << 2        # Bit 2 -- Contacto principal / visible por defecto
    IS_LOGISTIC = 1 << 3       # Bit 3 -- Contacto de entrega / flete / recepcion
    IS_ADMIN = 1 << 4          # Bit 4 -- Contacto administrativo / facturacion
    IS_DECISION_MAKER = 1 << 5  # Bit 5 -- Contacto comprador / autorizante
    IS_COLLECTIONS = 1 << 6   # Bit 6 -- Contacto de cobranzas

    # Bit 7 en adelante: libre.

    # Default canonico para un Vinculo recien creado (Nike, ratificacion v2):
    # nace existente y virgen, sin rol asignado todavia.
    DEFAULT = EXISTENCE | IS_VIRGIN  # = 3
