# INFORME HISTÓRICO: Restauración Logística (Remitos V5.1)
**Fecha**: 2026-03-20
**Agente**: Gy (Antigravity)
**Estado**: NOMINAL GOLD (Parcial)

## 1. Resumen de la Misión
Se abordó la restauración de la funcionalidad de edición de remitos emitidos (especialmente los provenientes de ingesta de facturas PDF) que se encontraba desactivada/perdida en el listado de "Logística: Remitos Emitidos".

## 2. Ediciones Técnicas (Sprint Actual)
- [x] **Backend**: Implementación de `PATCH /remitos/{id}` en el router y método `update_remito` en el servicio para modificar cabeceras.
- [x] **Store**: Acción `updateRemito` añadida a Pinia.
- [x] **UI**: Evento `@dblclick` en `RemitoListView.vue` para abrir el modal de edición.
- [x] **Modal**: Permite editar Número Legal, CAE, Vencimiento, Transporte y Dirección de Entrega.

## 3. DEUDAS TÉCNICAS (PENDIENTE PRÓXIMA SESIÓN)
> [!IMPORTANT]
> El usuario ha solicitado expandir la capacidad del editor de remitos. Las siguientes tareas quedan "en el hangar" para ser resueltas por Gy en el próximo despertar:
>
> 1. **Edición de Bultos y Valor Declarado**: Añadir estos campos al modal de edición (actualmente solo existen en la creación manual).
> 2. **Edición del Cuerpo (Items)**: Habilitar la edición de las cantidades y descripciones de los productos dentro de un remito ya emitido (BORRADOR).
> 3. **Gestión de Direcciones Incompletas**: Solucionar el problema de faltantes en la dirección cuando el remito proviene de la extracción de PDF (PDF Ingestion).
> 4. **Habilitación de Campos**: Asegurar que los campos de Cliente y Dirección sean editables/seleccionables en el modal incluso para remitos de ingesta.

## 4. Auditoría de Cierre
- Sistema en estado Nominal (Estabilidad API 200 OK).
- Sergio Jofre sincronizado (Bit 19 activo).
- Auditoría OMEGA iniciada.
