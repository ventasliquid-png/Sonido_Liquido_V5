# Informe de Actividad - Sesión de Tarde/Noche 15/12/2025

## Resumen Ejecutivo
Se realizó una re-ingeniería completa del flujo de vida de los Pedidos en el "Inspector", pasando de un modelo rígido de preguntas al cierre a un modelo fluido tipo "Borrador de Gmail". Además, se desacopló estructuralmente el "Estado del Trabajo" (Borrador/Pendiente) del "Tipo Impositivo" (Fiscal/X), permitiendo mayor flexibilidad operativa.

## Detalle de Actividades

### 1. Arquitectura de Datos (Backend & DB)
- **Modificación de Esquema**: Se agregó la columna `tipo_comprobante` a la tabla `pedidos`.
    - *Antes*: El estado `INTERNO` se usaba confusamente para pedidos en negro.
    - *Ahora*: El estado define el avance (`PENDIENTE`, `PRESUPUESTO`) y el tipo define la fiscalidad (`FISCAL`, `X`).
- **Migración SQLite**: Se creó y ejecutó exitosamente el script `scripts/add_tipo_to_pedidos.py` para actualizar la base de datos local sin perder datos.
- **Endpoints**: Se actualizaron los endpoints `POST /tactico`, `PATCH /pedidos/{id}` y `POST /clone` para soportar y persistir el nuevo campo.
- **Items**: Se implementó `PATCH /pedidos/items/{id}` para permitir la edición en vivo de cantidades y precios.

### 2. Frontend & UX (Inspector de Pedidos)
- **Evolución del Flujo**:
    1.  *Intento 1*: Prompt al salir (¿Guardar cambios?). (Descartado por intrusivo).
    2.  *Intento 2*: Botonera explícita al pie (Oficializar / Cotizar). (Descartado por redundante).
    3.  *Solución Final*: **Control Unificado en Selector**.
        - El selector de estado gobierna todo.
        - Ir a `PENDIENTE` dispara la pregunta de confirmación de tipo (Fiscal vs X).
        - Ir a `BORRADOR` o `PRESUPUESTO` es instantáneo.
- **UX "Gmail Style"**:
    - Se eliminaron todas las preguntas al cerrar con Escape o F10.
    - El guardado es automático y silencioso. El estado `BORRADOR` es el default seguro.
- **Mejoras Visuales**:
    - Se retiraron las flechas (spinners) de los inputs numéricos.
    - Se habilitó la edición directa de Precio Unitario.
    - Se corrigió la legibilidad del buscador de productos (SmartSelect) en fondo oscuro.

### 3. Frontend (Tablero Táctico)
- **Filtros**: Se renombraron las pestañas para reflejar la nueva realidad:
    - `Clonados` -> `Borradores`.
    - `Internos` -> `Presupuestos` (y X).
- **Columnas**: Se ajustaron los badges de estado para coincidir con la nueva nomenclatura.

### 4. Correcciones Técnicas (Bug Fixes)
- **Error CORS/500**: Solucionado al corregir el script de migración que causaba el crash del backend.
- **Sintaxis Vue**: Se reparó un bloque de código duplicado en `PedidoInspector.vue` que impedía la compilación.
- **Reactividad**: Se solucionó el lag al agregar items forzando la actualización de props desde el store.

## Estado Actual del Sistema
- **Pedidos**: Operativos con flujo Borrador -> Pendiente/Presupuesto.
- **Base de Datos**: Actualizada con campo `tipo_comprobante`.
- **Pendientes**:
    - Revisar lógica de precios al cambiar de Fiscal a X (actualmente mantiene el precio, ¿debería recalcular?).
    - Verificar que los filtros de lista cuenten correctamente los nuevos estados combinados.

## Próximos Pasos Sugeridos
1.  Actualizar Manual Operativo con el nuevo flujo de "Activación de Pedidos".
2.  Prueba de campo de la carga de pedidos "X" vs "Fiscales" para asegurar que los totales reflejen la realidad deseada.
