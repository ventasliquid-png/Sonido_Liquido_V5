# Implementación: Refinamiento de Lógica de Activación y Persistencia de Listado

## Problemas Detectados
1.  **Pérdida de Contexto de Listado:** Al salir de la ficha (inspector) o cancelar una acción, el listado vuelve a "Solo Activos" en lugar de recordar que el usuario estaba viendo "Todos" o "Inactivos".
2.  **Reactuación Masiva Insegura (Utilidades Maestras):** La reactivación desde `MasterTools` (UM) salta las validaciones y activa clientes incompletos.
3.  **Lógica de Lote Incompleto:** Si reactivamos un lote y algunos están incompletos, no podemos abrir 50 fichas a la vez.

## Estrategia de Solución

### 1. Persistencia de Listado (`HaweView.vue`)
*   **Estado en Store/LocalStorage:** Guardar el `filterStatus` en `localStorage` (igual que se hace con `sortBy`) para que persista entre recargas o navegaciones.
*   **Corrección de Flujo:** Asegurar que `cancel` o `closeInspector` no reseteen el filtro.

### 2. Reactivación Masiva Segura (`MasterTools.vue` / `DataCleaner.vue`)
*   **Lógica "Cuarentena":** La reactivación masiva desde UM moverá los clientes a la lista principal pero **manteniendo su estado `activo=False`** si no cumplen validación, o simplemente los deja visibles en el maestro (si "reactivar desde UM" significa "traer de Cantera" o "Recuperar de Papelera"). 
    *   *Aclaración:* Si se refiere a "Data Cleaner" (Recuperar eliminados soft), estos ya vuelven como `activo=False` generalmente.
    *   Si se refiere a una acción de "Forzar Activación Masiva", esta debe ser **reemplazada** por "Validar y Activar" o simplemente prohibir la activación masiva de incompletos.
*   **Propuesta del Usuario Aceptada:** "Pasarlos al maestro de clientes pero en estado inactivo".
    *   Esto significa que la acción "Recuperar" o "Importar" debe setear `activo=False` por defecto, obligando al usuario a activarlos uno a uno (y validarlos) en el listado operativo.

## Plan de Ejecución

### Paso 1: Persistencia de Filtro
*   Modificar `HaweView.vue`:
    *   Inicializar `filterStatus` leyendo de `localStorage`.
    *   `watch(filterStatus)` para guardar en `localStorage`.

### Paso 2: Seguridad en Master Tools / Cantera
*   Revisar `CanteraExplorer.vue` o `MasterTools.vue` (donde ocurra esta "reactivación").
*   Asegurar que la importación o recuperación setee explícitamente `activo=False` para que caigan en la bandeja de entrada inactiva para su revisión posterior.

## Archivos Afectados
*   `frontend/src/views/HaweView.vue` (Persistencia Filtro)
*   `frontend/src/views/Maestros/CanteraExplorer.vue` (Importación Segura) - *Si aplica* (o el componente que el usuario llama "Utilidades Maestras").
