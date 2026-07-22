# Ficha Técnica: BITS_CLIENTES.md

## Rango de Estado Nominal (0-4)
- **Bit 0 (1)**: EXISTENCE (El registro existe físicamente).
- **Bit 1 (2)**: VIRGINITY (1 = Registro Virgen / 0 = Registro Operado/Modificado).
- **Bit 2 (4)**: GOLD (Validado por ARCA/AFIP).
- **Bit 3 (8)**: V14_STRUCT (Estructura de datos alineada con Doctrina V14).
- **Bit 4 (16)**: SABUESO (Auditado por el motor de búsqueda inteligente).

## Bits de Gestión Específica
- **Bit 19 (524288)**: POWER_PINK (Medalla de soberanía informal para clientes Rosa con lista y segmento completos).
- **Bit 20 (1048576)**: PENDIENTE_REVISION (Requiere revisión manual — falta segmento o lista de precios).

## Bits de Canal de Origen
- **Bit 30**: CH_TNUBE (Canal Tiendanube).
- **Bit 31**: CH_MLIBRE (Canal MercadoLibre).
- **Bit 32**: CH_WHATSAPP (Canal Manual/WhatsApp).
