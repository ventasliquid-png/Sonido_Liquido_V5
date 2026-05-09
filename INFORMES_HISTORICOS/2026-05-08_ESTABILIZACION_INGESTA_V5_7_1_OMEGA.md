# Informe Histórico: Estabilización Ingesta V5.7.1 (Protocolo OMEGA)
Fecha: 2026-05-08
Operador: Antigravity (Advanced Agentic Coding)

## Resumen Ejecutivo
Se ha completado la estabilización del workflow de ingesta de facturas y generación de remitos puente. La sesión se centró en la aplicación estricta de la **Doctrina Numero Legal** y la resolución de bloqueos técnicos en el sellado fiscal y la persistencia de datos.

## Desafíos Técnicos y Resoluciones

### 1. El Misterio del Error 422 (Formatos de Fecha)
- **Problema**: El endpoint `/facturacion/{id}/sellar` fallaba con `422 Unprocessable Entity`.
- **Diagnóstico**: Pydantic esperaba una fecha en formato ISO (`YYYY-MM-DD`), pero el parser de PDF extraía el formato argentino (`DD/MM/YYYY`).
- **Resolución**: Se implementó la función helper `_iso_date()` en `pdf_parser.py` para normalizar todas las fechas extraídas antes de enviarlas al backend.

### 2. Persistencia del Store (Fuga de ingestaData)
- **Problema**: Al intentar sellar la factura desde `PedidoCanvas.vue`, el objeto `ingestaData` era `null`.
- **Causa**: Un mecanismo de limpieza preventiva en el `onMounted` borraba los datos apenas se cargaban los ítems.
- **Resolución**: Se postergó la ejecución de `clearIngestaData()` hasta que el proceso de guardado (incluyendo el sellado y la generación del remito puente) sea exitoso.

### 3. Doctrina Numero Legal (Hard Enforcement)
- **Implementación**: Se eliminaron los fallbacks al ID de pedido en `backend/remitos/service.py`. 
- **Lógica**: Los remitos de la serie `0016` (automáticos) ahora requieren obligatoriamente un `numero_comprobante` de factura sellado. Si el OCR falla o el sellado no ocurre, el sistema bloquea la creación del remito para preservar la integridad legal.

### 4. Sincronización Horaria (ART vs ISO)
- **Problema**: Los pedidos guardados de noche aparecían con fecha del día siguiente en el listado.
- **Resolución**: Sustitución de `toISOString()` (que usa UTC) por una función `getLocalDate()` manual en el frontend, asegurando que la fecha grabada sea la del huso horario de Argentina.

## Verificación de Éxito
- **Test Gelato SA**: Pedido #33 generado con éxito.
- **Factura AFIP**: 00001-00002531 sellada correctamente.
- **Remito Puente**: `0016-00002531` generado y vinculado.
- **Auto-Print**: El PDF se abre automáticamente tras el guardado.

**Estado Final: NOMINAL GOLD.**
PIN 1974 Validado.
