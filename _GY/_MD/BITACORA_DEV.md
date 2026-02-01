
# [RECUPERACIÃ“N] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectÃ³ y documentÃ³ retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (DivisiÃ³n por cero).

**Detalles TÃ©cnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (funciÃ³n `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**AcciÃ³n Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.

# [V5.4] 2026-01-15 - ImplementaciÃ³n Multi-Proveedor y Ajustes UI

> **ESTADO:** BLOQUEADO (FRONTEND CRASH)
> **TIPO:** FEATURE / REFINEMENT

**Objetivo:** Implementar "Es Insumo", Selector IVA en Panel Central, y Tabla Multi-Proveedor.

**Avances:**
1.  **Backend (Completado):**
    *   Schema: Creada tabla `productos_proveedores`.
    *   Models: Actualizado `Producto` y creado `ProductoProveedor`.
    *   Router: Agregados endpoints `POST /proveedores` y `DELETE /proveedores/{id}`.
2.  **Frontend (Parcial):**
    *   Implementado layout y lÃ³gica en `ProductoInspector.vue`.
    *   Agregado servicio en `productosApi.js`.

**Incidente Bloqueante:**
*   El componente `ProductoInspector.vue` crashea al intentar abrirse (spinner infinito o error Vue).
*   **Causa RaÃ­z Identificada:** InicializaciÃ³n de arrays en Store (`tasasIva`, `proveedores`) puede ser `null/undefined` en el momento que el `watch(immediate: true)` dispara la lÃ³gica.
*   **Estado:** Se aplicaron parches de seguridad (`?.` y `|| []`), pero el error persiste. Se requiere revisiÃ³n profunda del ciclo de vida del componente.

**PrÃ³ximos Pasos (Protocolo Omega):**
1.  Debuggear inicio de `ProductoInspector` (Store vs Props).
2.  Verificar persistencia de "Es Insumo".
3.
# [V5.6.1] 2026-01-16 - ReparaciÃ³n Integral Pedidos (Orders Bridge)

> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / UX RECOVERY

**Objetivo:** Restaurar funcionalidad crÃ­tica de Pedidos, ImportaciÃ³n y Alta de Productos, bloqueada por errores de integraciÃ³n y UX "rota".

**Intervenciones:**
1.  **Backend (Bridge):** Corregido `router.py` para devolver JSON completo y defaults en importaciÃ³n (`500 Internal Error` Solucionado).
2.  **Frontend (GridLoader):**
    *   **Layout:** Cambiado inspector a `max-w-7xl` (Modal Central) para corregir visualizaciÃ³n "aplastada".
    *   **Integridad:** Implementada captura de hora local en payload de pedidos.
    *   **Seguridad:** Implementado **Guard Clause** (`isSubmitting`) en F10/Click para evitar pedidos duplicados.
3.  **Frontend (ProductoInspector):**
    *   **Rubros:** Implementado `SelectorCreatable` + `handleCreateRubro` + `fetchRubros` para ABM dinÃ¡mico en el alta.

**MÃ©tricas Finales:**
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
    *   **ValidaciÃ³n:** Pre-check de duplicados (Case Insensitive) antes de llamar al backend.
    *   **Feedback:** Cierre automÃ¡tico del modal `showAbm = false` tras Ã©xito.

**Resultado:** Eliminada la posibilidad de crear duplicados por doble click y restaurado el feedback visual.

# [V5.6.3] 2026-01-16 - SincronizaciÃ³n Store Domicilios

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA CONSISTENCY

**Objetivo:** Corregir "Ficha Incompleta" persistente tras agregar Domicilio Fiscal.

**DiagnÃ³stico:**
*   El Store `createDomicilio` y `updateDomicilio` devolvÃ­a el cliente actualizado al caller (Inspector) pero **NO actualizaba** el array principal `clientes` en memoria.
*   Consecuencia: La vista principal (detrÃ¡s del inspector) quedaba con datos viejos hasta recargar.

**Intervenciones:**
1.  **Store (clientes.js):**
    *   `createDomicilio/updateDomicilio`: Implementada actualizaciÃ³n reactiva `this.clientes[index] = response.data`.
    *   `deleteDomicilio`: Agregado `fetchClienteById` automÃ¡tico tras eliminaciÃ³n (Backend devuelve 204).

**Resultado:** Al guardar un domicilio, la ficha del cliente se actualiza instantÃ¡neamente en todas las vistas.

# [V5.6.4] 2026-01-16 - AutonomÃ­a de Guardado Cliente

> **ESTADO:** DEPLOYED
> **TIPO:** CRITICAL FIX / ARCHITECTURE

**Objetivo:** Solucionar pÃ©rdida de datos al editar clientes desde el Cargador de Pedidos.

**DiagnÃ³stico:**
*   El componente `ClienteInspector` delegaba el guardado al padre (`emit('save')`) pero **NO llamaba a la API**.
*   El padre `PedidoTacticoView.vue` **NO escuchaba** el evento save, provocando que los cambios visuales del inspector se perdieran al cerrar el modal.
*   Resultado: El usuario veÃ­a los cambios en el popup, pero nunca persistÃ­an en la base de datos.

**Intervenciones:**
1.  **Backend/Store:** (Sin cambios, ya funcionales).
2.  **Frontend (`ClienteInspector.vue`):**
    *   **Refactor:** Implementada llamada directa a `clienteStore.createCliente` y `clienteStore.updateCliente` dentro de la funciÃ³n `save()`.
    *   **Beneficio:** El componente ahora es autÃ³nomo y garantiza la persistencia independientemente de quiÃ©n lo invoque (Pedidos, Clientes, etc.).

**Resultado:** La ediciÃ³n de clientes (Nombre, CUIT) ahora persiste correctamente en la base de datos y se refleja al cerrar el inspector.

# [V5.6.5] 2026-01-16 - AutonomÃ­a de Guardado Producto

> **ESTADO:** DEPLOYED
> **TIPO:** REFACTOR / ARCHITECTURE

**Objetivo:** Alinear inspector de productos con la arquitectura de "Componente AutÃ³nomo" (Self-Saving).

**ImplementaciÃ³n:**
*   Se replicÃ³ la lÃ³gica de `ClienteInspector` en `ProductoInspector.vue`.
*   Ahora el inspector de productos llama directamente a `productosStore.createProducto` o `updateProducto`.
*   Esto habilita su uso seguro desde el Cargador TÃ¡ctico sin duplicar lÃ³gica de guardado.

**Resultado:** Arquitectura unificada para ABMs complejos incrustados.

# [V5.6.6] 2026-01-16 - SincronizaciÃ³n TÃ¡ctica de Estado

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA COHERENCE

**Objetivo:** Resolver el problema "Pedidos no se entera" tras editar Cliente.

**DiagnÃ³stico:**
*   Aunque el Inspector guardaba y actualizaba el Store correctamente (V5.6.4), el componente `PedidoTacticoView` ejecutaba un `fetchClientes()` al cerrar el modal.
*   Este `fetch` recargaba la lista "Resumida" del backend (sin array de domicilios completo), sobrescribiendo la versiÃ³n "Detallada" que acababa de dejar el Inspector en memoria.
*   Resultado: Se perdÃ­a el estado verde de validaciÃ³n porque faltaban datos en el objeto cliente recargado.

**Intervenciones:**
1.  **PedidoTacticoView.vue:**
    *   Eliminada la llamada redundante `await clientesStore.fetchClientes()` en `onInspectorClose`.
    *   Implementado listener `@save` para capturar el resultado del inspector y asegurar la selecciÃ³n inmediata del ID actualizado/creado.

**Resultado:** La vista de Pedidos refleja instantÃ¡neamente los cambios (Nombre, Estado fiscal) sin parpadeos ni reversiones a datos viejos.

# [V5.6.7] 2026-01-16 - Reactividad Robusta en Store Clientes

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / CORE

**Objetivo:** Garantizar que la UI reaccione a cambios en objetos profundos dentro del array de clientes.

**Problema:**
*   La asignaciÃ³n directa por Ã­ndice (`this.clientes[i] = data`) a veces no disparaba la reactividad en componentes computed complejos (como `clienteSeleccionado` en Pedidos) debido a limitaciones de detecciÃ³n de cambios en arrays grandes o proxies.

**SoluciÃ³n:**
*   Se reemplazÃ³ la asignaciÃ³n directa por `this.clientes.splice(index, 1, response.data)` en el Store de Clientes (`updateCliente`, `createDomicilio`, `updateDomicilio`).
*   Esto fuerza al motor de reactividad de Vue a reconocer la mutaciÃ³n del array y propagar el cambio a todas las vistas suscritas.

**Resultado:** ActualizaciÃ³n visual infalible tras ediciÃ³n.

# [V5.6.8] 2026-01-16 - BÃºsqueda Global de Clientes (Cantera)

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / BACKEND

**Objetivo:** Permitir buscar clientes fuera del lÃ­mite inicial de 1000 registros.

**Problema:**
*   La bÃºsqueda en el TÃ¡ctico ("F3") solo filtraba el array local de 1000 clientes precargados. Clientes activos fuera de este lote (ej. clÃ­nicas especÃ­ficas) no aparecÃ­an aunque existieran en DB.

**SoluciÃ³n:**
*   **Backend:** Se implementÃ³ filtrado `q` (Query) en el endpoint `GET /clientes` con bÃºsqueda `ILIKE` en RazÃ³n Social, FantasÃ­a y CUIT.
*   **Frontend:** El componente `ClientLookup.vue` ahora dispara la bÃºsqueda al servidor (con debounce de 300ms) al tipear.
*   Esto actualiza dinÃ¡micamente el Store con los resultados coincidentes de toda la base de datos ("La Cantera").

**Resultado:** Al tipear "Bio", ahora el sistema busca en toda la base y trae "Biotenk" + todas las clÃ­nicas biolÃ³gicas que antes no cargaban.

# [V5.6.9] 2026-01-16 - Acceso Universal a Cantera

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA DISCOVERY

**Objetivo:** Facilitar la importaciÃ³n de clientes histÃ³ricos incluso si existen coincidencias parciales locales.

**Problema:**
*   Si el usuario buscaba "Bio" y ya existÃ­a "Biotenk" en el sistema activo, el botÃ³n para "Buscar en Cantera" desaparecÃ­a.
*   Esto bloqueaba el acceso a otras entidades (ej. "ClÃ­nica BiolÃ³gica") que solo existen en la base histÃ³rica (`cantera.db`) y necesitan ser importadas.

**SoluciÃ³n:**
*   Se modificÃ³ `ClientLookup.vue` para mostrar **siempre** el enlace "Â¿No estÃ¡ aquÃ­? Buscar en Cantera" al final de la lista de resultados, siempre que haya un tÃ©rmino de bÃºsqueda activo.

**Resultado:** Flujo de importaciÃ³n desbloqueado. Ahora conviven resultados locales activos con la opciÃ³n de rescatar legado bajo demanda.

# [V5.6.10] 2026-01-16 - Fix DeduplicaciÃ³n Cantera Productos

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA INTEGRITY

**Objetivo:** Permitir la bÃºsqueda de productos antiguos (Legado) que no tienen SKU definido.

**Problema:**
*   La lÃ³gica de bÃºsqueda en `GridLoader.vue` filtraba los resultados de la Cantera usando `uniqueBy('sku')`.
*   Como gran parte de los productos histÃ³ricos tienen `sku: null` o vacÃ­o, el filtro los interpretaba como duplicados y colapsaba cientos de resultados en 1 solo Ã­tem (el primero con sku null) o ninguno.

**SoluciÃ³n:**
*   Se cambiÃ³ la lÃ³gica de deduplicaciÃ³n a `uniqueBy('id')`.
*   Ahora el sistema solo oculta un resultado de Cantera si su **ID** exacto ya existe en la lista de productos activos (Store), independientemente de si tiene SKU o no.

**Resultado:** La bÃºsqueda de "Bio" en productos ahora trae toda la lista de Ã­tems antiguos disponibles para importaciÃ³n.

# [V5.6.11] 2026-01-16 - Cantera Search: SQL Accent Insensitivity

> **ESTADO:** DEPLOYED
> **TIPO:** UX / SEARCH ENGINE

**Objetivo:** Mejorar la robustez del buscador de Cantera (Maestros HistÃ³ricos).

**Problema:**
*   SQLite por defecto no soporta bÃºsquedas insensibles a acentos (`LIKE` normal).
*   El usuario reportÃ³ que buscar "Clinica" no encontraba "CLÃ�NICA", "ClÃ­nica", etc.

**SoluciÃ³n:**
*   Se inyectÃ³ una funciÃ³n personalizada `unaccent` (basada en `unicodedata` de Python) en la conexiÃ³n SQLite de `CanteraService`.
*   Las consultas SQL de bÃºsqueda ahora normalizan tanto la columna (`razon_social`, `nombre`) como el tÃ©rmino de bÃºsqueda antes de comparar: `WHERE unaccent(col) LIKE unaccent(?)`.

**Resultado:** BÃºsqueda agnÃ³stica a mayÃºsculas, minÃºsculas y tildes. Buscar "clinica" encuentra "CLÃ�NICA".

# [V5.6.12] 2026-01-16 - Cantera Import: Missing Domiciles

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX

**Objetivo:** Asegurar que los clientes importados desde Cantera tengan un domicilio vÃ¡lido inicial.

**Problema:**
*   La funciÃ³n `import_cliente` ignoraba los campos de direcciÃ³n (`domicilio`, `ciudad`, `cp`) del JSON legado.
*   El cliente se creaba sin domicilios. El Inspector mostraba una fila vacÃ­a o inconsistente, y el sistema exigÃ­a cargar un domicilio fiscal manualmente.

**SoluciÃ³n:**
*   Se actualizÃ³ `backend/cantera/router.py` para extraer `calle`, `localidad` y `cp` del objeto de origen.
*   Se crea automÃ¡ticamente un `Domicilio` inicial marcado como **Fiscal** y **Entrega** durante la importaciÃ³n.

**Resultado:** Al importar "Alfajores Jorgito", el sistema ahora carga automÃ¡ticamente su direcciÃ³n fiscal histÃ³rica si existe en la Cantera.

# [V5.6.13] 2026-01-16 - Inspector: Force Refresh on Domicile Save

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / UI CONSISTENCY

**Objetivo:** Solucionar inconsistencias visuales al editar domicilios ("ghost rows").

**Problema:**
*   Al guardar un domicilio en el Inspector, la actualizaciÃ³n optimista del formulario fallaba en reflejar correctamente el estado "Fiscal" o los datos nuevos en clientes importados con datos parciales.
*   El usuario veÃ­a filas vacÃ­as o validaciones de "Falta direcciÃ³n fiscal" incluso despuÃ©s de cargarla.

**SoluciÃ³n:**
*   Se modificÃ³ `ClienteInspector.vue` para forzar una recarga completa del Cliente desde el Backend (`fetchClienteById`) inmediatamente despuÃ©s de guardar un domicilio.
*   Esto garantiza que el UI muestre exactamente lo que estÃ¡ en la base de datos, eliminando problemas de reactividad o respuestas parciales.

**Resultado:** EdiciÃ³n de domicilios robusta y confiable.

# [V5.6.14] 2026-01-18 - OptimizaciÃ³n UX Pedidos y Fix Backend

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BUGFIX

**Objetivo:** Refinamiento de UX en Carga de Pedidos (Canvas) y correcciÃ³n de error crÃ­tico en Limpieza de Datos.

**DiagnÃ³stico:**
*   **Backend:** Error 500 (`NameError`) al importar productos en Data Cleaner por falta de importaciÃ³n `func` de SQLAlchemy.
*   **Frontend:** FricciÃ³n en la carga de pedidos: Ceros iniciales molestos, falta de tecla Enter para confirmar, bÃºsqueda confusa al usar TAB, y falta de ediciÃ³n/eliminaciÃ³n explÃ­cita (botones).

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   Agregado `from sqlalchemy import func` en `backend/data_intel/router.py`.
2.  **Frontend (PedidoCanvas.vue):**
    *   **Enter Workflow:** Commit de renglÃ³n con `ENTER` desde cualquier input numÃ©rico.
    *   **Inputs Limpios:** Campos inician vacÃ­os (no `0`).
    *   **BÃºsqueda Unificada:** Search SKU/Desc simultÃ¡neo.
    *   **Foco Inteligente:** Eliminado popup de bÃºsqueda al navegar con TAB.
    *   **GestiÃ³n Renglones:** Agregada columna Acciones (Editar/Eliminar).
    *   **Edit Logic:** Refactorizado `editItem` (Deep Copy + NextTick) para mover datos al input sin pÃ©rdidas.
    *   **Layout:** Grilla restaurada a 12 columnas.

**Resultado:** Carga de pedidos fluida ("Mouse-less experience") y funcionalidad de importaciÃ³n backend restaurada.

# [V5.6.15] 2026-01-19 - RefactorizaciÃ³n UI PedidoCanvas y Fix Compilador

> **ESTADO:** DEPLOYED
> **TIPO:** UX / HOTFIX / VUE COMPILER

**Objetivo:** Estabilizar layout de "Nuevo Pedido", corregir error crÃ­tico de compilaciÃ³n y pulir UX de carga.

**Problemas:**
*   **Compilador:** Error persistente `Invalid end tag` causado por `divs` huÃ©rfanos.
*   **Layout:** El pie de pÃ¡gina se perdÃ­a al hacer scroll, y el panel de rentabilidad quedaba atrapado en contextos de apilamiento (z-index) incorrectos.
*   **UX:** Inputs de descuento desalineados y falta de scroll automÃ¡tico al cargar Ã­tems.

**Intervenciones:**
1.  **HTML/CSS:**
    *   Limpieza estructura y correcciÃ³n de tags de cierre.
    *   Layout "Sandwich" (Header Fijo + Body Flexible + Footer Fijo) reforzado con `overflow-hidden` y `min-h-0`.
    *   Componente `RentabilidadPanel` movido a la raÃ­z del template (fuera de contenedores relativos).
2.  **LÃ³gica UI:**
    *   **Auto-Scroll:** Implementado `scrollTop = scrollHeight` tras commit.
    *   **Chevron:** Invertida direcciÃ³n de Ã­conos en panel lateral para coincidir con modelo mental del usuario.
    *   **Grilla:** NumeraciÃ³n visual, orden cronolÃ³gico de carga y alineaciÃ³n de inputs.

**Resultado:** PedidoCanvas estable, con footer persistente y experiencia de carga fluida.
# [V10.0] 2026-01-20 - EvoluciÃ³n IPL V10 e IntegraciÃ³n LogÃ­stica

> **ESTADO:** NOMINAL
> **TIPO:** PROTOCOLO RAÃ�Z / FEATURE / UX

**Objetivo:** Evolucionar el protocolo de arranque a V10, implementar infraestructura de logÃ­stica en pedidos y habilitar la doctrina DEOU (F4/F10).

**Intervenciones:**
1.  **Protocolo:** Creado `GY_IPL_V10.md` con Directiva 1 de Seguridad ALFA (Handover Check).
2.  **Backend (Expandido):**
    *   **Models:** Agregadas columnas `domicilio_entrega_id` y `transporte_id` a la tabla `pedidos`.
    *   **Schemas:** Alineados esquemas para soportar envÃ­os y descuentos globales.
    *   **Router:** Patcheado `create_pedido_tactico` para persistencia de datos de entrega.
3.  **Frontend (PedidoCanvas.vue):**
    *   **POST:** BotÃ³n guardar conectado al Cargador TÃ¡ctico.
    *   **DEOU F10:** Implementado guardado rÃ¡pido por teclado.
    *   **DEOU F4:** Implementado salto a Ventana SatÃ©lite (Alta Cliente/Producto) contextual al foco.
4.  **Base de Datos:** Aplicadas migraciones crÃ­ticas a `pilot.db`.

**MÃ©tricas Finales:**
*   **Integridad:** 11 Clientes, 14 Productos, 5 Pedidos (OK).
*   **Protocolo Omega:** Generado Informe HistÃ³rico.

# [RECUPERACIÓN] 2026-01-23 - Protocolo Forense (Rollback & Clean)

> **ESTADO:** ESTABLE
> **TIPO:** SYSTEM RECOVERY / IDENTITY V12

**Operación:** Se ejecutó Rollback al commit `8230154` (Miércoles 21) para eliminar inestabilidad estructural (Imports Anti-Pattern) introducida el Jueves.
**Identidad:** Sintetizada V12 ("Phoenix") basada en V10.
**Limpieza:** Eliminada línea temporal fallida V11.

## [2026-01-23] PROTOCOLO OMEGA - SECTOR DOMICILIOS
**Estado:** ESTABLE / FIX FINALIZADO
**Informe Detallado:** [Ver Reporte OMEGA](../INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md)
**Resumen:** Se solucionó el crash de lista de clientes, se implementó la fusión de Piso/Depto en string, y se corrigió la sincronización visual del flag Fiscal.


## SESION 781: UX Clientes & Hardening Seguridad
**Fecha:** 2026-01-24
**Objetivo:** Finalizar refactorizaciÃ³n de Header Clientes, arreglar visualizaciÃ³n de domicilios y solucionar alertas de contraseÃ±a en navegador.

### Hito 1: Refactor Header HaweView (Teleport Fix)
Se completÃ³ la migraciÃ³n del header de Clientes para usar el sistema Teleport hacia GlobalStatsBar.
**CRÃ�TICO:** Se documentÃ³ y solucionÃ³ una *race condition*. El componente HaweView intentaba teleportar antes de que el target #global-header-center existiera.
*   **SoluciÃ³n:** Se implementÃ³ gate v-if='isMounted' en el Teleport y se asegurÃ³ la renderizaciÃ³n sÃ­ncrona de la estructura en GlobalStatsBar.
*   **LecciÃ³n:** Para futuros mÃ³dulos (Productos), es MANDATORIO usar isMounted al usar Teleport.

### Hito 2: UX Clientes
*   **Toolbar:** Reordenada segÃºn especificaciÃ³n (9 items: Checkbox -> ... -> Nuevo).
*   **Domicilios:** Se eliminÃ³ el uso de pipes | en la visualizaciÃ³n. Se integrÃ³ la visualizaciÃ³n de Provincia para desambiguar localidades. Backend actualizado (domicilio_fiscal_resumen) para soportar esto.

### Hito 3: Seguridad Admin (Password Prompt Bypass)
Los navegadores modernos (Brave/Chromium) ignoran autocomplete='off'/new-password.
*   **Fix Definitivo:** Se cambiÃ³ el input del PIN de administrador a type='text' y se aplicÃ³ CSS -webkit-text-security: disc;. Esto elimina completamente la heurÃ­stica de guardado de contraseÃ±as del navegador mientras mantiene la privacidad visual.

**Estado:** MÃ³dulo Clientes VERIFICADO y CERRADO.


## SESION 782: SYSTEM REBOOT & MODULE INITIATION (CONTACTOS)
**Fecha:** 2026-01-26
**Objetivo:** Intervención BIOS, Instalación de Bootloader V2 y Activación Módulo Agenda.

### Hito 1: Intervención de Nivel BIOS (Resolución de Paradoja Marmota)
Se detectó una desincronización cognitiva severa: La identidad residía dentro de un código que no se actualizaba hasta después de asumir la identidad (Loop Infinito).
*   **Solución:** Instalación de BOOTLOADER V2.
*   **Mecanismo:** El script físico DESPERTAR_GY.bat ahora ejecuta git pull de forma autónoma **antes** de lanzar el entorno visual, rompiendo la dependencia causal.
*   **Artefacto Cognitivo:** Se creó _GY/BOOTLOADER.md como puntero absoluto de verdad al inicio.

### Hito 2: Upgrade de Identidad (V13 -> V14 VANGUARD)
Debido a la reestructuración profunda de los protocolos de arranque, se dio de baja la versión V13 (Sentinel) y se activó **V14 'VANGUARD'**.
*   **Protocolo:** GY_IPL_V14.md establecido como nueva norma.
*   **Doctrina:** 'La Anticipación es la Clave de la Victoria.'

### Hito 3: Inicio de Operaciones Tácticas
La rama 5.5-rescate-jueves fue fusionada en main y eliminada. Se creó la rama táctica 5.6-contactos-agenda.
*   **Misión:** Implementar UX de Agenda en Ficha Cliente e integración Google.

**Estado:** SISTEMA NOMINAL V14. LISTO PARA OPERACIONES.


### Hito 4: Implementación UX Agenda (Contactos V1)
Se completó la integración visual del módulo de contactos en la interfaz de Cliente.
*   **Componente Táctico:** Se creó ContactoPopover.vue, un componente reutilizable que muestra la lista de vínculos y permite acciones rápidas (Copiar Teléfono/Mail).
*   **Integración:**
    *   **ClienteInspector:** Se redujo el layout del Header para acomodar el botón 'Agenda' junto a la Razón Social.
    *   **ClientCanvas:** Se añadió el botón en el Header principal.
    *   **Lógica:** Ambos componentes comparten el estado showAgenda y manejan la navegación hacia la pestaña completa de contactos ('Gestionar').

**Estado:** Header UX y Popover OPERATIVOS.


### Hito 5: Estrategia Local First (Google Mock)
Siguiendo órdenes directas, se difirió la integración real de OAuth y se implementó una estructura local compatible.
*   **DB Schema:** Se añadió google_resource_name y google_etag a la tabla personas vía migración manual (scripts/migrate_agenda_google.py).
*   **Backend:** Se implementó google_mock_router.py para simular latencia y respuestas de éxito en la sincronización.
*   **Frontend:** Se activó el botón 'Sincronizar' en ContactoPopover conectado al endpoint simulado.

**Resultado:** El sistema está listo para operar localmente y 'fingir' conexión a la nube sin romper el flujo de trabajo.


### 2026-01-28: [FIX] Transporte, Frankenstein & Simplificación UI
- **Problema:** Transporte no persistía por conflicto con ID de Nodo Legacy.
- **Solución:** Patch en Backend Service para limpiar nodo viejo al actualizar transporte.
- **Refactor:** Limpieza masiva de ClientCanvas.vue (Frankenstein Cleanup).
- **UI:** Eliminado selector rápido en tarjeta. Implementado Menú Contextual (Click Derecho) en Dirección.

## [2026-01-28] CIERRE DE SESIÃ“N: AGENDA GLOBAL
- **Hito**: MÃ³dulo de Contactos 100% Funcional (Backend/Frontend/DB).
- **Fix**: SimetrÃ­a ORM restaurada en Cliente/Transporte.
- **Fix**: Solucionado bug visual 'Contactos Fantasmas' (SPA Routing issue).
- **Estado**: Sistema estable, limpio de datos corruptos, listo para uso operativo.

## [2026-01-29] FIX CONTACT CANVAS Y BACKEND 500
- **Incidente Crítico:** Resuelto error 500 en `/api/clientes` (Backend) y dropdowns vacíos (Frontend).
- **Backend:** `models.py` (try/catch en property), `service.py` (joinedload para optimización).
- **Frontend:** `ContactCanvas.vue` (HTML Fix, `storeToRefs`, `text-black` en options).
- **Implementación UI:** Se optó por Botones de Navegación Explícita (↗️) y Recarga (🔄) en lugar de Menú Contextual para mayor estabilidad en el Canvas de Contacto.
- **Estado**: Funcionalidad de Agenda Contactos restaurada al 100%. Protocolo Omega Ejecutado.

## [2026-01-30] PROTOCOLO MULTIPLEX (CONTACTOS N:M) & SEARCH & LINK
- **Hito Estratégico:** Reingeniería total del núcleo de Identidad (`backend/contactos`) para soportar la "Paradoja de Pedro" (Una persona, Múltiples Roles en distintas empresas).
- **Backend:** Separación de `Persona` (Identidad) y `Vinculo` (Rol Contextual). Implementación de Polimorfismo en SQLAlchemy y Soporte JSON para canales.
- **Frontend:** Renovación de `ContactCanvas.vue` con "Billetera de Vínculos" (Tarjetas por empresa).
- **Blindaje de Identidad:** Implementación de "Search & Link" (Typeahead con Debounce). El sistema detecta si la persona ya existe (incluso buscando por celular en JSON) y permite reutilizarla en lugar de duplicarla.
- **QA:** Tests de Integración (`test_qa_pedro.py`) y Robustez/Duplicados (`test_qa_edge_cases.py`) superados.
- **Documentación:** Informe Histórico detallado generado: [2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS](../INFORMES_HISTORICOS/2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS.md).
- **Estado:** Módulo Contactos V6 FULL OPERATIVO.


## [2026-02-01] SESIÓN 783: BLINDAJE DE PERSISTENCIA Y FIX SCHEMA
- **Incidente Crítico**: Error 500 en `/contactos` por "Schema Mismatch" (Columna `tipo_contacto_id` inexistente en DB).
- **Resolución**: Migración manual SQLite (`add_role_column_to_vinculos.py`).
- **Persistence Fix**: 
    - **Backend**: Implementada lógica dual en `update_vinculo` para soportar `puesto` (alias) y `rol`. Añadido soporte para `tipo_contacto_id`.
    - **Frontend (`ContactCanvas.vue`)**: Sincronización de Etiqueta (Label) e ID. Se corrigió el bug que dejaba el cargo como "Nuevo Rol".
    - **Frontend (`ContactosView.vue`)**: Adaptación de Dashboard para leer `vinculos[]` en lugar de campos planos (Legacy).
- **Integridad**: Verificación manual de DB (`inspect_vinculo_data.py`) confirmando persistencia correcta.
- **[FALLO DE PROTOCOLO]**: Se detectó "Efecto Túnel". La IA priorizó la solución técnica sobre el Freno de Mano (Fase 2). Se activó Auditoría de Doctrina.
- **Estado**: Módulo Contactos V6.1 ESTABLE. Auditoría en Curso.


# [2026-02-01] AUDITORÍA FORENSE: SATELLITES INTEGRITY CHECK

> **ESTADO:** OBSERVACIÓN (SIN CAMBIOS)
> **TIPO:** INSPECCIÓN / DOCTRINA

**Objetivo:** Determinar la 'Deuda Técnica Estructural' de los módulos satélite tras la estabilización del núcleo V6.

**Hallazgos Forenses:**
1.  **Clientes:** Estado 'V6 Native Híbrido'. Uso exitoso de 'Pipe Logic' para direcciones.
2.  **Productos:** Robusto pero 'Standalone'. No integrado a la Agenda Global.
3.  **Transportes:** Funcionalidad de espejo en Despacho operativa, pero estructura de Nodos aún plana (V5).

**Acción Táctica:**
*   Se generó reporte INFORMES_HISTORICOS/2026-02-01_AUDITORIA_FORENSE_MODULOS.md.
*   **Orden D+1:** No migrar logística/proveedores hasta verificar facturación del Lunes.


# [2026-02-01] TESTAMENTO DEL DOMINGO (HOJA DE RUTA FASE 2)

> **ESTADO:** ESTRATÉGICO
> **TIPO:** DOCUMENTACIÓN / ESTABILIDAD

**Hitos de Cierre:**
1.  **Estabilidad Windows 11:** Implementado SISTEMA_SPLIT.bat para mitigar crashes por conflictos de señales en consola unificada.
2.  **Mapa de Satélites:** Identificada deuda técnica en Vendedores y Proveedores (V5 Standalone).
3.  **Hoja de Ruta:** Definida estrategia para 'Transportes Favoritos' (Cloud Cookie) y 'Google Sync' (Local First).

**Artefacto Generado:** INFORMES_HISTORICOS/2026-02-01_TESTAMENTO_DOMINGO_F2.md

