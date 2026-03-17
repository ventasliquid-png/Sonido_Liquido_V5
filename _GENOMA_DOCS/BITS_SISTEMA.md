# Ficha Técnica: BITS_SISTEMA.md (Protocolo ALFA)

## Diagnóstico de Inicio (Sellado OMEGA-DOC)
- **Bit 1**: PARADA (Estado de detención operativa).
- **Bit 2**: ERROR_MENOR (Fallo no crítico / Warning).
- **Bit 3**: SYNC (Sincronización Cloud/Local activa).
- **Bit 4**: TRINCHERA (Operación en Modo Chernobyl / Casa).

## Protocolo de Interpretación
Este bitstatus debe ser reportado al inicio de cada sesión mediante el comando de diagnóstico ALFA.
