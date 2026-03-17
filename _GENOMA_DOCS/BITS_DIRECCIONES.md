# Ficha Técnica: BITS_DIRECCIONES.md

## Estándar de Slots
- **Slot 0**: Fiscal (Dirección Legal/Impositiva).
- **Slot 1**: Entrega (Dirección Logística Predeterminada).
- **Slot 2+**: Histórico (Direcciones utilizadas anteriormente o sucursales secundarias).

## Capacidad
- **Registros**: Soporte para hasta 256 registros por cliente preservando la integridad histórica.
- **Byte Histórico**: Los IDs de direcciones previas se almacenan en el campo `historial_direcciones` para auditoría forense.
