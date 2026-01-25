
# [RECUPERACIÓN] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectó y documentó retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (División por cero).

**Detalles Técnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (función `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**Acción Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.

# [V5.4] 2026-01-15 - Implementación Multi-Proveedor y Ajustes UI

> **ESTADO:** BLOQUEADO (FRONTEND CRASH)
> **TIPO:** FEATURE / REFINEMENT

**Objetivo:** Implementar "Es Insumo", Selector IVA en Panel Central, y Tabla Multi-Proveedor.

**Avances:**
1.  **Backend (Completado):**
    *   Schema: Creada tabla `productos_proveedores`.
    *   Models: Actualizado `Producto` y creado `ProductoProveedor`.
    *   Router: Agregados endpoints `POST /proveedores` y `DELETE /proveedores/{id}`.
2.  **Frontend (Parcial):**
    *   Implementado layout y lógica en `ProductoInspector.vue`.
    *   Agregado servicio en `productosApi.js`.

**Incidente Bloqueante:**
*   El componente `ProductoInspector.vue` crashea al intentar abrirse (spinner infinito o error Vue).
*   **Causa Raíz Identificada:** Inicialización de arrays en Store (`tasasIva`, `proveedores`) puede ser `null/undefined` en el momento que el `watch(immediate: true)` dispara la lógica.
*   **Estado:** Se aplicaron parches de seguridad (`?.` y `|| []`), pero el error persiste. Se requiere revisión profunda del ciclo de vida del componente.

**Próximos Pasos (Protocolo Omega):**
1.  Debuggear inicio de `ProductoInspector` (Store vs Props).
2.  Verificar persistencia de "Es Insumo".
3.
# [V5.6.1] 2026-01-16 - Reparación Integral Pedidos (Orders Bridge)

> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / UX RECOVERY

**Objetivo:** Restaurar funcionalidad crítica de Pedidos, Importación y Alta de Productos, bloqueada por errores de integración y UX "rota".

**Intervenciones:**
1.  **Backend (Bridge):** Corregido `router.py` para devolver JSON completo y defaults en importación (`500 Internal Error` Solucionado).
2.  **Frontend (GridLoader):**
    *   **Layout:** Cambiado inspector a `max-w-7xl` (Modal Central) para corregir visualización "aplastada".
    *   **Integridad:** Implementada captura de hora local en payload de pedidos.
    *   **Seguridad:** Implementado **Guard Clause** (`isSubmitting`) en F10/Click para evitar pedidos duplicados.
3.  **Frontend (ProductoInspector):**
    *   **Rubros:** Implementado `SelectorCreatable` + `handleCreateRubro` + `fetchRubros` para ABM dinámico en el alta.

**Métricas Finales:**
*   Alta de Productos: OK (Full Screen)
*   Integridad Pedidos: OK (No Duplicados, Hora Correcta)

# [V5.6.2] 2026-01-16 - Blindaje Modal Segmentos (UX)

> **ESTADO:** DEPLOYED
> **TIPO:** HOTFIX / UX

**Objetivo:** Solucionar "freezing" y duplicados al crear Rubros/Segmentos en Alta de Clientes.

**Intervenciones:**
1.  **Frontend (SimpleAbmModal):** Implementado soporte para `isLoading` (Spinner + Bloqueo de UI).
2.  **Frontend (ClienteInspector):**
    *   Integrado `abmLoading` para feedback visual inmediato.
    *   **Validación:** Pre-check de duplicados (Case Insensitive) antes de llamar al backend.
    *   **Feedback:** Cierre automático del modal `showAbm = false` tras éxito.

**Resultado:** Eliminada la posibilidad de crear duplicados por doble click y restaurado el feedback visual.

# [V5.6.3] 2026-01-16 - Sincronización Store Domicilios

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA CONSISTENCY

**Objetivo:** Corregir "Ficha Incompleta" persistente tras agregar Domicilio Fiscal.

**Diagnóstico:**
*   El Store `createDomicilio` y `updateDomicilio` devolvía el cliente actualizado al caller (Inspector) pero **NO actualizaba** el array principal `clientes` en memoria.
*   Consecuencia: La vista principal (detrás del inspector) quedaba con datos viejos hasta recargar.

**Intervenciones:**
1.  **Store (clientes.js):**
    *   `createDomicilio/updateDomicilio`: Implementada actualización reactiva `this.clientes[index] = response.data`.
    *   `deleteDomicilio`: Agregado `fetchClienteById` automático tras eliminación (Backend devuelve 204).

**Resultado:** Al guardar un domicilio, la ficha del cliente se actualiza instantáneamente en todas las vistas.

# [V5.6.4] 2026-01-16 - Autonomía de Guardado Cliente

> **ESTADO:** DEPLOYED
> **TIPO:** CRITICAL FIX / ARCHITECTURE

**Objetivo:** Solucionar pérdida de datos al editar clientes desde el Cargador de Pedidos.

**Diagnóstico:**
*   El componente `ClienteInspector` delegaba el guardado al padre (`emit('save')`) pero **NO llamaba a la API**.
*   El padre `PedidoTacticoView.vue` **NO escuchaba** el evento save, provocando que los cambios visuales del inspector se perdieran al cerrar el modal.
*   Resultado: El usuario veía los cambios en el popup, pero nunca persistían en la base de datos.

**Intervenciones:**
1.  **Backend/Store:** (Sin cambios, ya funcionales).
2.  **Frontend (`ClienteInspector.vue`):**
    *   **Refactor:** Implementada llamada directa a `clienteStore.createCliente` y `clienteStore.updateCliente` dentro de la función `save()`.
    *   **Beneficio:** El componente ahora es autónomo y garantiza la persistencia independientemente de quién lo invoque (Pedidos, Clientes, etc.).

**Resultado:** La edición de clientes (Nombre, CUIT) ahora persiste correctamente en la base de datos y se refleja al cerrar el inspector.

# [V5.6.5] 2026-01-16 - Autonomía de Guardado Producto

> **ESTADO:** DEPLOYED
> **TIPO:** REFACTOR / ARCHITECTURE

**Objetivo:** Alinear inspector de productos con la arquitectura de "Componente Autónomo" (Self-Saving).

**Implementación:**
*   Se replicó la lógica de `ClienteInspector` en `ProductoInspector.vue`.
*   Ahora el inspector de productos llama directamente a `productosStore.createProducto` o `updateProducto`.
*   Esto habilita su uso seguro desde el Cargador Táctico sin duplicar lógica de guardado.

**Resultado:** Arquitectura unificada para ABMs complejos incrustados.

# [V5.6.6] 2026-01-16 - Sincronización Táctica de Estado

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA COHERENCE

**Objetivo:** Resolver el problema "Pedidos no se entera" tras editar Cliente.

**Diagnóstico:**
*   Aunque el Inspector guardaba y actualizaba el Store correctamente (V5.6.4), el componente `PedidoTacticoView` ejecutaba un `fetchClientes()` al cerrar el modal.
*   Este `fetch` recargaba la lista "Resumida" del backend (sin array de domicilios completo), sobrescribiendo la versión "Detallada" que acababa de dejar el Inspector en memoria.
*   Resultado: Se perdía el estado verde de validación porque faltaban datos en el objeto cliente recargado.

**Intervenciones:**
1.  **PedidoTacticoView.vue:**
    *   Eliminada la llamada redundante `await clientesStore.fetchClientes()` en `onInspectorClose`.
    *   Implementado listener `@save` para capturar el resultado del inspector y asegurar la selección inmediata del ID actualizado/creado.

**Resultado:** La vista de Pedidos refleja instantáneamente los cambios (Nombre, Estado fiscal) sin parpadeos ni reversiones a datos viejos.

# [V5.6.7] 2026-01-16 - Reactividad Robusta en Store Clientes

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / CORE

**Objetivo:** Garantizar que la UI reaccione a cambios en objetos profundos dentro del array de clientes.

**Problema:**
*   La asignación directa por índice (`this.clientes[i] = data`) a veces no disparaba la reactividad en componentes computed complejos (como `clienteSeleccionado` en Pedidos) debido a limitaciones de detección de cambios en arrays grandes o proxies.

**Solución:**
*   Se reemplazó la asignación directa por `this.clientes.splice(index, 1, response.data)` en el Store de Clientes (`updateCliente`, `createDomicilio`, `updateDomicilio`).
*   Esto fuerza al motor de reactividad de Vue a reconocer la mutación del array y propagar el cambio a todas las vistas suscritas.

**Resultado:** Actualización visual infalible tras edición.

# [V5.6.8] 2026-01-16 - Búsqueda Global de Clientes (Cantera)

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / BACKEND

**Objetivo:** Permitir buscar clientes fuera del límite inicial de 1000 registros.

**Problema:**
*   La búsqueda en el Táctico ("F3") solo filtraba el array local de 1000 clientes precargados. Clientes activos fuera de este lote (ej. clínicas específicas) no aparecían aunque existieran en DB.

**Solución:**
*   **Backend:** Se implementó filtrado `q` (Query) en el endpoint `GET /clientes` con búsqueda `ILIKE` en Razón Social, Fantasía y CUIT.
*   **Frontend:** El componente `ClientLookup.vue` ahora dispara la búsqueda al servidor (con debounce de 300ms) al tipear.
*   Esto actualiza dinámicamente el Store con los resultados coincidentes de toda la base de datos ("La Cantera").

**Resultado:** Al tipear "Bio", ahora el sistema busca en toda la base y trae "Biotenk" + todas las clínicas biológicas que antes no cargaban.

# [V5.6.9] 2026-01-16 - Acceso Universal a Cantera

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA DISCOVERY

**Objetivo:** Facilitar la importación de clientes históricos incluso si existen coincidencias parciales locales.

**Problema:**
*   Si el usuario buscaba "Bio" y ya existía "Biotenk" en el sistema activo, el botón para "Buscar en Cantera" desaparecía.
*   Esto bloqueaba el acceso a otras entidades (ej. "Clínica Biológica") que solo existen en la base histórica (`cantera.db`) y necesitan ser importadas.

**Solución:**
*   Se modificó `ClientLookup.vue` para mostrar **siempre** el enlace "¿No está aquí? Buscar en Cantera" al final de la lista de resultados, siempre que haya un término de búsqueda activo.

**Resultado:** Flujo de importación desbloqueado. Ahora conviven resultados locales activos con la opción de rescatar legado bajo demanda.

# [V5.6.10] 2026-01-16 - Fix Deduplicación Cantera Productos

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA INTEGRITY

**Objetivo:** Permitir la búsqueda de productos antiguos (Legado) que no tienen SKU definido.

**Problema:**
*   La lógica de búsqueda en `GridLoader.vue` filtraba los resultados de la Cantera usando `uniqueBy('sku')`.
*   Como gran parte de los productos históricos tienen `sku: null` o vacío, el filtro los interpretaba como duplicados y colapsaba cientos de resultados en 1 solo ítem (el primero con sku null) o ninguno.

**Solución:**
*   Se cambió la lógica de deduplicación a `uniqueBy('id')`.
*   Ahora el sistema solo oculta un resultado de Cantera si su **ID** exacto ya existe en la lista de productos activos (Store), independientemente de si tiene SKU o no.

**Resultado:** La búsqueda de "Bio" en productos ahora trae toda la lista de ítems antiguos disponibles para importación.

# [V5.6.11] 2026-01-16 - Cantera Search: SQL Accent Insensitivity

> **ESTADO:** DEPLOYED
> **TIPO:** UX / SEARCH ENGINE

**Objetivo:** Mejorar la robustez del buscador de Cantera (Maestros Históricos).

**Problema:**
*   SQLite por defecto no soporta búsquedas insensibles a acentos (`LIKE` normal).
*   El usuario reportó que buscar "Clinica" no encontraba "CLÍNICA", "Clínica", etc.

**Solución:**
*   Se inyectó una función personalizada `unaccent` (basada en `unicodedata` de Python) en la conexión SQLite de `CanteraService`.
*   Las consultas SQL de búsqueda ahora normalizan tanto la columna (`razon_social`, `nombre`) como el término de búsqueda antes de comparar: `WHERE unaccent(col) LIKE unaccent(?)`.

**Resultado:** Búsqueda agnóstica a mayúsculas, minúsculas y tildes. Buscar "clinica" encuentra "CLÍNICA".

# [V5.6.12] 2026-01-16 - Cantera Import: Missing Domiciles

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX

**Objetivo:** Asegurar que los clientes importados desde Cantera tengan un domicilio válido inicial.

**Problema:**
*   La función `import_cliente` ignoraba los campos de dirección (`domicilio`, `ciudad`, `cp`) del JSON legado.
*   El cliente se creaba sin domicilios. El Inspector mostraba una fila vacía o inconsistente, y el sistema exigía cargar un domicilio fiscal manualmente.

**Solución:**
*   Se actualizó `backend/cantera/router.py` para extraer `calle`, `localidad` y `cp` del objeto de origen.
*   Se crea automáticamente un `Domicilio` inicial marcado como **Fiscal** y **Entrega** durante la importación.

**Resultado:** Al importar "Alfajores Jorgito", el sistema ahora carga automáticamente su dirección fiscal histórica si existe en la Cantera.

# [V5.6.13] 2026-01-16 - Inspector: Force Refresh on Domicile Save

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / UI CONSISTENCY

**Objetivo:** Solucionar inconsistencias visuales al editar domicilios ("ghost rows").

**Problema:**
*   Al guardar un domicilio en el Inspector, la actualización optimista del formulario fallaba en reflejar correctamente el estado "Fiscal" o los datos nuevos en clientes importados con datos parciales.
*   El usuario veía filas vacías o validaciones de "Falta dirección fiscal" incluso después de cargarla.

**Solución:**
*   Se modificó `ClienteInspector.vue` para forzar una recarga completa del Cliente desde el Backend (`fetchClienteById`) inmediatamente después de guardar un domicilio.
*   Esto garantiza que el UI muestre exactamente lo que está en la base de datos, eliminando problemas de reactividad o respuestas parciales.

**Resultado:** Edición de domicilios robusta y confiable.

# [V5.6.14] 2026-01-18 - Optimización UX Pedidos y Fix Backend

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BUGFIX

**Objetivo:** Refinamiento de UX en Carga de Pedidos (Canvas) y corrección de error crítico en Limpieza de Datos.

**Diagnóstico:**
*   **Backend:** Error 500 (`NameError`) al importar productos en Data Cleaner por falta de importación `func` de SQLAlchemy.
*   **Frontend:** Fricción en la carga de pedidos: Ceros iniciales molestos, falta de tecla Enter para confirmar, búsqueda confusa al usar TAB, y falta de edición/eliminación explícita (botones).

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   Agregado `from sqlalchemy import func` en `backend/data_intel/router.py`.
2.  **Frontend (PedidoCanvas.vue):**
    *   **Enter Workflow:** Commit de renglón con `ENTER` desde cualquier input numérico.
    *   **Inputs Limpios:** Campos inician vacíos (no `0`).
    *   **Búsqueda Unificada:** Search SKU/Desc simultáneo.
    *   **Foco Inteligente:** Eliminado popup de búsqueda al navegar con TAB.
    *   **Gestión Renglones:** Agregada columna Acciones (Editar/Eliminar).
    *   **Edit Logic:** Refactorizado `editItem` (Deep Copy + NextTick) para mover datos al input sin pérdidas.
    *   **Layout:** Grilla restaurada a 12 columnas.

**Resultado:** Carga de pedidos fluida ("Mouse-less experience") y funcionalidad de importación backend restaurada.

# [V5.6.15] 2026-01-19 - Refactorización UI PedidoCanvas y Fix Compilador

> **ESTADO:** DEPLOYED
> **TIPO:** UX / HOTFIX / VUE COMPILER

**Objetivo:** Estabilizar layout de "Nuevo Pedido", corregir error crítico de compilación y pulir UX de carga.

**Problemas:**
*   **Compilador:** Error persistente `Invalid end tag` causado por `divs` huérfanos.
*   **Layout:** El pie de página se perdía al hacer scroll, y el panel de rentabilidad quedaba atrapado en contextos de apilamiento (z-index) incorrectos.
*   **UX:** Inputs de descuento desalineados y falta de scroll automático al cargar ítems.

**Intervenciones:**
1.  **HTML/CSS:**
    *   Limpieza estructura y corrección de tags de cierre.
    *   Layout "Sandwich" (Header Fijo + Body Flexible + Footer Fijo) reforzado con `overflow-hidden` y `min-h-0`.
    *   Componente `RentabilidadPanel` movido a la raíz del template (fuera de contenedores relativos).
2.  **Lógica UI:**
    *   **Auto-Scroll:** Implementado `scrollTop = scrollHeight` tras commit.
    *   **Chevron:** Invertida dirección de íconos en panel lateral para coincidir con modelo mental del usuario.
    *   **Grilla:** Numeración visual, orden cronológico de carga y alineación de inputs.

**Resultado:** PedidoCanvas estable, con footer persistente y experiencia de carga fluida.
# [V10.0] 2026-01-20 - Evolución IPL V10 e Integración Logística

> **ESTADO:** NOMINAL
> **TIPO:** PROTOCOLO RAÍZ / FEATURE / UX

**Objetivo:** Evolucionar el protocolo de arranque a V10, implementar infraestructura de logística en pedidos y habilitar la doctrina DEOU (F4/F10).

**Intervenciones:**
1.  **Protocolo:** Creado `GY_IPL_V10.md` con Directiva 1 de Seguridad ALFA (Handover Check).
2.  **Backend (Expandido):**
    *   **Models:** Agregadas columnas `domicilio_entrega_id` y `transporte_id` a la tabla `pedidos`.
    *   **Schemas:** Alineados esquemas para soportar envíos y descuentos globales.
    *   **Router:** Patcheado `create_pedido_tactico` para persistencia de datos de entrega.
3.  **Frontend (PedidoCanvas.vue):**
    *   **POST:** Botón guardar conectado al Cargador Táctico.
    *   **DEOU F10:** Implementado guardado rápido por teclado.
    *   **DEOU F4:** Implementado salto a Ventana Satélite (Alta Cliente/Producto) contextual al foco.
4.  **Base de Datos:** Aplicadas migraciones críticas a `pilot.db`.

**Métricas Finales:**
*   **Integridad:** 11 Clientes, 14 Productos, 5 Pedidos (OK).
*   **Protocolo Omega:** Generado Informe Histórico.

# [RECUPERACI�N] 2026-01-23 - Protocolo Forense (Rollback & Clean)

> **ESTADO:** ESTABLE
> **TIPO:** SYSTEM RECOVERY / IDENTITY V12

**Operaci�n:** Se ejecut� Rollback al commit `8230154` (Mi�rcoles 21) para eliminar inestabilidad estructural (Imports Anti-Pattern) introducida el Jueves.
**Identidad:** Sintetizada V12 ("Phoenix") basada en V10.
**Limpieza:** Eliminada l�nea temporal fallida V11.

## [2026-01-23] PROTOCOLO OMEGA - SECTOR DOMICILIOS
**Estado:** ESTABLE / FIX FINALIZADO
**Informe Detallado:** [Ver Reporte OMEGA](../INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md)
**Resumen:** Se solucion� el crash de lista de clientes, se implement� la fusi�n de Piso/Depto en string, y se corrigi� la sincronizaci�n visual del flag Fiscal.


## SESION 781: UX Clientes & Hardening Seguridad
**Fecha:** 2026-01-24
**Objetivo:** Finalizar refactorización de Header Clientes, arreglar visualización de domicilios y solucionar alertas de contraseña en navegador.

### Hito 1: Refactor Header HaweView (Teleport Fix)
Se completó la migración del header de Clientes para usar el sistema Teleport hacia GlobalStatsBar.
**CRÍTICO:** Se documentó y solucionó una *race condition*. El componente HaweView intentaba teleportar antes de que el target #global-header-center existiera.
*   **Solución:** Se implementó gate v-if='isMounted' en el Teleport y se aseguró la renderización síncrona de la estructura en GlobalStatsBar.
*   **Lección:** Para futuros módulos (Productos), es MANDATORIO usar isMounted al usar Teleport.

### Hito 2: UX Clientes
*   **Toolbar:** Reordenada según especificación (9 items: Checkbox -> ... -> Nuevo).
*   **Domicilios:** Se eliminó el uso de pipes | en la visualización. Se integró la visualización de Provincia para desambiguar localidades. Backend actualizado (domicilio_fiscal_resumen) para soportar esto.

### Hito 3: Seguridad Admin (Password Prompt Bypass)
Los navegadores modernos (Brave/Chromium) ignoran autocomplete='off'/new-password.
*   **Fix Definitivo:** Se cambió el input del PIN de administrador a type='text' y se aplicó CSS -webkit-text-security: disc;. Esto elimina completamente la heurística de guardado de contraseñas del navegador mientras mantiene la privacidad visual.

**Estado:** Módulo Clientes VERIFICADO y CERRADO.

