# Informe de Caja Negra: Sesión 2026-05-08 (Estabilización Ingesta V5.7.1)

## Resumen Ejecutivo
Finalización del puente operativo entre Ingesta de Facturas y Generación de Remitos. Se ha blindado el sistema contra desvíos legales en la numeración y se han resuelto los cuellos de botella de formato (fechas) y persistencia (store).

## Cronología de Acciones Técnicas

### 1. Aplicación de la Doctrina Numero Legal
- Eliminación de numeración provisional en Serie 0016.
- Vinculación estricta al número fiscal AFIP detectado por OCR.
- Refactor de `backend/remitos/service.py` para normalizar la inyección de `numero_legal`.

### 2. Resolución de Incompatibilidad Pydantic (Error 422)
- Detección de colisión de tipos en el campo `cae_vencimiento`.
- Parche en `pdf_parser.py`: Inyección de normalizador ISO para fechas DD/MM/YYYY.

### 3. Estabilización de la Capa de Persistencia (Vue/Pinia)
- Corrección de la carrera de limpieza en `PedidoCanvas.vue`.
- Aseguramiento de la disponibilidad de `ingestaData` durante todo el ciclo de vida del Alta de Pedido.

### 4. Calibración de Reloj Local
- Abandono de UTC en el sellado de fechas de pedidos para evitar saltos de día.

## Archivos Impactados
- `backend/remitos/pdf_parser.py` (Regex + ISO Dates)
- `backend/remitos/service.py` (Doctrina Legal)
- `frontend/src/stores/pedidos.js` (AutoPrint flags)
- `frontend/src/views/Ventas/PedidoCanvas.vue` (Persistence + Local Date + Sellar logic)
- `frontend/src/views/Pedidos/IngestaFacturaView.vue` (UI Integration)

## Firmas Digitales
- **Protocolo**: OMEGA Certified.
- **PIN**: 1974 Validated.
- **Status**: NOMINAL GOLD.
- **Informe**: `INFORMES_HISTORICOS/2026-05-08_ESTABILIZACION_INGESTA_V5_7_1_OMEGA.md`
