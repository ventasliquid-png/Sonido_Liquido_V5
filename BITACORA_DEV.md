# Bitácora de Desarrollo - Sonido Líquido V5

## Normas de UX / UI (Doctrina DEOU)

### 1. Atajos de Teclado Globales
*   **F10 (Guardar y Cerrar):** En cualquier formulario o modal de carga (ABM), la tecla `F10` debe actuar como el botón "Aceptar" o "Guardar".
    *   Si la operación es exitosa, el modal debe cerrarse automáticamente.
    *   Si hay errores de validación, deben mostrarse y el modal permanecer abierto.
*   **F4 (Abrir ABM Relacionado):** Estando posicionado en un campo que referencia a una entidad maestra (ej: Combo de "Transporte", "Ramo", "Vendedor"), la tecla `F4` debe abrir el ABM de dicha entidad en modo "Stacked" (apilado).
    *   Al cerrar el ABM apilado (con F10 o Cancelar), el foco debe volver al campo original y la lista debe actualizarse.

### 2. Comportamiento de Modales
*   **Cierre Automático:** Tras una operación exitosa de "Guardar" o "Actualizar", el modal debe cerrarse automáticamente. No deben quedar alertas bloqueantes (alert) que requieran un clic extra del usuario, salvo para errores críticos.
*   **Stacked Modals:** Los modales deben soportar la propiedad `isStacked` para renderizarse correctamente cuando son invocados desde otro modal (ej: sin header completo, con botón "Volver").

### 3. Acciones de Listado
*   **Baja / Eliminación:** Todos los listados maestros deben incluir una opción explícita para "Dar de Baja" o "Eliminar" (generalmente Soft Delete), accesible directamente desde la fila del registro (icono 🗑️).

---

## Protocolo de Continuidad (Caja Negra)

Este protocolo define cómo los agentes (Gy OF, Gy CA, y otros) mantienen una memoria compartida y persistente del contexto de trabajo, permitiendo alternancia entre equipos sin pérdida de información.

### 1. Identidad del Agente
Cada entorno de trabajo debe tener un archivo **local** (no versionado) llamado `.gy_identity` en la raíz del proyecto.
*   Contenido: Un código único de 2-3 letras.
    *   `OF`: Oficina (PC Principal)
    *   `CA`: Casa (PC Secundaria)
    *   `NB`: Notebook / Viaje
*   **Importante:** Este archivo debe estar en `.gitignore`.

### 2. Archivo de Memoria (`MEMORIA_SESIONES.md`)
Este archivo actúa como la "Caja Negra" del proyecto. Es un log acumulativo de las sesiones de trabajo.
*   **Ubicación:** Raíz del proyecto.
*   **Formato:** Markdown cronológico inverso (Sesión más reciente arriba).
*   **Contenido:** Resúmenes de alto nivel, decisiones tomadas, y estado de tareas críticas.

### 3. Gestión de Sesiones (Script `session_manager.py`)
Se utiliza el script `scripts/session_manager.py` para automatizar la apertura y cierre de sesiones, aplicando una lógica de "Poda Inteligente" para no saturar el archivo.

**Lógica de Retención:**
1.  **Cadena Actual:** Mantiene TODAS las sesiones continuas del agente actual (ej: Si Gy OF trabaja lunes, martes y miércoles, se guardan las 3).
2.  **Última del Otro:** Mantiene la última sesión registrada por un agente distinto (ej: La última de Gy CA del domingo).
3.  **Eslabón de Enlace:** Mantiene la última sesión propia *anterior* a la intervención del otro agente (para dar contexto de qué estaba haciendo yo antes de que el otro tocara el código).

### 4. Procedimiento Estándar

#### A. Inicio de Sesión
Al comenzar a trabajar, el agente debe ejecutar:
```bash
python scripts/session_manager.py start
```
*   Esto inserta un bloque "EN CURSO" en `MEMORIA_SESIONES.md`.
*   El agente debe leer este archivo para obtener contexto inmediato.

#### B. Cierre de Sesión
Al finalizar (antes de hacer commit/push o cerrar), el agente debe ejecutar:
```bash
python scripts/session_manager.py end "Resumen de lo hecho..."
```
*   **Resumen:** Debe ser conciso pero técnico. Mencionar archivos clave tocados y bugs resueltos.
*   El script se encargará de cerrar el bloque, poner la fecha de fin, y podar las sesiones antiguas según la lógica de retención.

#### C. Configuración de Nuevo Agente (Ej: Viaje)
Si se clona el repo en una nueva máquina:
1.  Crear archivo `.gy_identity` con el código del nuevo agente (ej: `NB`).
2.  Ejecutar `python scripts/session_manager.py start`.
3.  El sistema reconocerá al nuevo agente y comenzará a trackear sus sesiones, manteniendo la referencia a OF y CA según corresponda.

---

## Historial de Cambios Relevantes

### [2025-11-25] Operación Constelación (Maestros Satélites)
*   Implementación de módulos: Ramos, Vendedores, Listas de Precios, Agenda.
*   Seed de transporte virtual "RETIRO EN LOCAL" (ID 1).
*   Ajuste de UX en Transportes: Cierre automático de modal al guardar y botón de Baja.

### [2025-11-25] Estandarización UX Global (Norma DEOU)
*   **Implementación Masiva:** Se aplicaron las normas de atajos y comportamiento en todos los módulos (Transportes, Ramos, Vendedores, Listas, Personas, Clientes).
    *   `F10`: Guardar y Cerrar.
    *   `F4`: Nuevo registro (en listados).
    *   `Papelera`: Botón de baja lógica en listados.
*   **Refactor Técnico:** Creación de composable `useKeyboardShortcuts` para manejo centralizado de eventos.
*   **Base de Datos:** Migración para agregar campo `activo` a la tabla `personas`.

### [2025-11-25] Refactorización Ramo -> Segmento
*   **Cambio Semántico:** Se renombró la entidad "Ramo" a "Segmento" en todo el sistema (Base de Datos, Backend, Frontend, Documentación) para evitar ambigüedades con el concepto de "Rubro" de productos.
*   **Corrección de Bugs:**
    *   Solución a crash del Backend por error en Router de Maestros.
    *   Corrección en módulo Agenda (Personas): Se visualizaban como "Inactivos" por falta del campo `activo` en el schema de respuesta de la API.
*   **UI Standard:** Alineación de filtros "Todos/Activos/Inactivos" a la derecha en todos los listados para consistencia con el módulo Clientes.

    *   Se actualizó `ClienteService` para propagar el transporte seleccionado en la ficha del cliente hacia su domicilio predeterminado (Fiscal/Entrega).
*   **Frontend (ClienteForm):**
    *   **Tab 1 (General):** Integración de campos de domicilio legal para alta rápida. Creación automática de domicilio Fiscal/Entrega al guardar.
    *   **Transporte:** Campo obligatorio (con asterisco rojo). Se preselecciona "RETIRO EN LOCAL" si no hay otro.
    *   **Persistencia:** Solucionado bug donde el transporte no se guardaba/recuperaba correctamente en clientes existentes.
*   **SmartSelect:**
    *   Soporte para propiedad `required` (asterisco rojo).
    *   Corrección de "Race Condition" que borraba el valor seleccionado al cargar la lista asincrónicamente o al hacer click fuera prematuramente.
*   **Base de Datos:**
    *   Script de migración (`fix_legacy_transportes.py`) para asignar "RETIRO EN LOCAL" a todos los domicilios legados que no tenían transporte asignado.

### [2025-11-27] Pulido de Clientes y Domicilios
*   **Corrección de Bugs Críticos:**
    *   **Crash Frontend:** Solucionado `ReferenceError: onUnmounted` en `DomicilioGrid`.
    *   **Error de Guardado:** Se eliminó el campo `zona_id` del payload de Domicilios ya que no existía en el modelo, permitiendo guardar direcciones con "S/N".
*   **UX Domicilios:**
    *   **Dashboard:** Visualización en tiempo real de domicilios en la pestaña "General" (sin recarga).
    *   **Lógica de Transporte:**
        *   **Auto-relleno:** Al crear un nuevo destino, copia el transporte del Domicilio Fiscal.
        *   **Fallback:** Si se deja vacío, asigna automáticamente "Retiro en Local" (o el primero disponible) al guardar.
        *   **F10:** Se corrigió la captura de tecla para que F10 guarde el modal de domicilio si está abierto.
    *   **Visualización:** Se filtró el Domicilio Fiscal de la lista de entregas para evitar duplicados y conteo erróneo.

### [2025-11-27] Agenda y UX Avanzada (Sesión Nocturna)
*   **Módulo Agenda:**
    *   **Fix "Desconocido":** Se corrigió el schema del backend para incluir datos de la persona en la respuesta del vínculo.
    *   **Edición:** Se implementó la funcionalidad completa de edición de contactos (PUT) con botón dedicado.
    *   **Roles al Vuelo:** Implementación de creación de "Tipos de Contacto" directamente desde el formulario (F4).
*   **UX Premium:**
    *   **CopyTooltip:** Componente estilo "Gmail" para Email y WhatsApp. Al pasar el mouse, muestra el dato completo y permite copiarlo con un clic.
    *   **WhatsApp Input:** Campo inteligente con prefijo automático (+54 9) y limpieza de basura.
*   **Correcciones:**
    *   **Fix 422:** Sanitización de payloads para evitar errores de validación con campos vacíos.
    *   **Fix Top Clients:** Se blindó el schema de `ClienteResponse` para tolerar valores nulos en `saldo` y `contador_uso`, recuperando la lista de frecuentes.
    *   **Fix Import:** Corrección de referencia circular/errónea en `backend/clientes/router.py`.

### [2025-11-29] Replicación de Menú Contextual y ABM Maestros
*   **Backend (Maestros):**
    *   Implementación de CRUD completo (API + Schemas) para `Provincias`, `CondicionesIva` y `TiposContacto`.
    *   Validación de integridad referencial y manejo de errores.
*   **Frontend (Context Menu):**
    *   **Componente Reutilizable:** Creación de `ContextMenu.vue` para uso global.
    *   **Dashboard (HaweView):**
        *   Integración en lista lateral de "Segmentos" (Editar/Borrar).
        *   Integración en tarjetas de "Clientes" (Nueva Ficha, Administrar, Editar, Baja, IA).
        *   Integración en enlace "Clientes" del sidebar (Nuevo, Administrar).
    *   **ClientCanvas:**
        *   Integración en etiqueta "Segmento" del formulario (Nuevo, Administrar).
*   **UI/UX Refinements:**
    *   **Navegación:** Corrección de flujo entre "Fichas", "Nuevo Cliente" y Dashboard.
    *   **Estilos:** Rediseño de botones en cabecera de ficha para evitar confusión (Fichas resaltado, Nuevo sutil).
    *   **Feedback:** Mejoras en la indicación visual de contexto.

### [2025-11-30] Refactorización Logística y Domicilios (Tabs)
*   **Cambio Arquitectónico:**
    *   **Interfaz por Pestañas:** Se reemplazó el uso de modales flotantes por un sistema de pestañas (`CLIENTE`, `DOMICILIO`, `CONTACTO`) integrado en el canvas central de `ClientCanvas.vue`.
    *   **DomicilioForm:** Conversión de componente modal a componente de canvas, con botones "Volver" y "Guardar" integrados.
*   **UX/UI:**
    *   **Sidebar Logística:** Botones "FICHA - NUEVO" siempre visibles en cabecera de Domicilios.
    *   **Menú Contextual:** Implementado en cabecera de Domicilios (Nuevo, Administrar) y en tarjetas individuales (Editar, Eliminar).
    *   **Navegación:** Doble clic en tarjeta de domicilio abre la pestaña de edición correspondiente.
*   **Corrección de Bugs:**
    *   **Inicialización Formulario:** Se corrigió bug donde el doble clic abría el formulario de alta en lugar de edición (watcher de `domicilio` con `immediate: true`).
*   **Próximos Pasos (Pendientes):**
    *   Implementar navegación en bucle (loop) con flechas Arriba/Abajo en tarjetas de Domicilio.
    *   Implementar ABM completo de Transportes.

### [2025-11-30] Navegación Domicilios y ABM Transportes
*   **Domicilios (UX):**
    *   **Navegación por Teclado:** Se implementó navegación con flechas Arriba/Abajo en la lista de domicilios (`DomicilioGrid`).
    *   **Looping:** La navegación es circular (del último al primero y viceversa).
    *   **Foco:** Se añadió `tabindex="0"` y feedback visual para indicar la tarjeta activa.
*   **Transportes (Hawe):**
    *   **ABM Completo:** Se implementó la gestión completa de Transportes en `HaweTransportesView.vue`.
    *   **Funcionalidad:** Alta, Baja (Soft Delete), Modificación y Listado.
    *   **Campos:** Nombre, Teléfono Reclamos, Web Tracking, Activo, Requiere Carga Web, Formato Etiqueta.
    *   **Integración:** Conectado a `useLogisticaStore` y `useNotificationStore`.
*   **UI/UX:**
    *   **ClientCanvas:** Se separó el encabezado "Logística & Contactos" en dos secciones independientes: "LOGÍSTICA" y "CONTACTOS" para mayor claridad visual.
    *   **Estilo de Títulos:** Se aplicó un diseño destacado (texto cyan, fondo sutil, borde) a los títulos de sección en el panel derecho.
    *   **Fondo Global:** Se cambió el color de fondo principal de Negro (`#0a0a0a`) a Azul Profundo (`#0a1f2e`) para alinear con la identidad del módulo Clientes.
    *   **Listas de Gestión:** Se estandarizó el diseño de "Administrar Segmentos" y se creó "Administrar Domicilios" con tema oscuro, búsqueda y acciones con íconos, accesibles desde el menú contextual.
*   **Limpieza de Proyecto:**
    *   **Eliminación de Legacy:** Se eliminaron las carpetas `views/Clientes` y `views/Logistica` que contenían código obsoleto.
# Bitácora de Desarrollo - Sonido Líquido V5

## Normas de UX / UI (Doctrina DEOU)

### 1. Atajos de Teclado Globales
*   **F10 (Guardar y Cerrar):** En cualquier formulario o modal de carga (ABM), la tecla `F10` debe actuar como el botón "Aceptar" o "Guardar".
    *   Si la operación es exitosa, el modal debe cerrarse automáticamente.
    *   Si hay errores de validación, deben mostrarse y el modal permanecer abierto.
*   **F4 (Abrir ABM Relacionado):** Estando posicionado en un campo que referencia a una entidad maestra (ej: Combo de "Transporte", "Ramo", "Vendedor"), la tecla `F4` debe abrir el ABM de dicha entidad en modo "Stacked" (apilado).
    *   Al cerrar el ABM apilado (con F10 o Cancelar), el foco debe volver al campo original y la lista debe actualizarse.

### 2. Comportamiento de Modales
*   **Cierre Automático:** Tras una operación exitosa de "Guardar" o "Actualizar", el modal debe cerrarse automáticamente. No deben quedar alertas bloqueantes (alert) que requieran un clic extra del usuario, salvo para errores críticos.
*   **Stacked Modals:** Los modales deben soportar la propiedad `isStacked` para renderizarse correctamente cuando son invocados desde otro modal (ej: sin header completo, con botón "Volver").

### 3. Acciones de Listado
*   **Baja / Eliminación:** Todos los listados maestros deben incluir una opción explícita para "Dar de Baja" o "Eliminar" (generalmente Soft Delete), accesible directamente desde la fila del registro (icono 🗑️).

---

## Protocolo de Continuidad (Caja Negra)

Este protocolo define cómo los agentes (Gy OF, Gy CA, y otros) mantienen una memoria compartida y persistente del contexto de trabajo, permitiendo alternancia entre equipos sin pérdida de información.

### 1. Identidad del Agente
Cada entorno de trabajo debe tener un archivo **local** (no versionado) llamado `.gy_identity` en la raíz del proyecto.
*   Contenido: Un código único de 2-3 letras.
    *   `OF`: Oficina (PC Principal)
    *   `CA`: Casa (PC Secundaria)
    *   `NB`: Notebook / Viaje
*   **Importante:** Este archivo debe estar en `.gitignore`.

### 2. Archivo de Memoria (`MEMORIA_SESIONES.md`)
Este archivo actúa como la "Caja Negra" del proyecto. Es un log acumulativo de las sesiones de trabajo.
*   **Ubicación:** Raíz del proyecto.
*   **Formato:** Markdown cronológico inverso (Sesión más reciente arriba).
*   **Contenido:** Resúmenes de alto nivel, decisiones tomadas, y estado de tareas críticas.

### 3. Gestión de Sesiones (Script `session_manager.py`)
Se utiliza el script `scripts/session_manager.py` para automatizar la apertura y cierre de sesiones, aplicando una lógica de "Poda Inteligente" para no saturar el archivo.

**Lógica de Retención:**
1.  **Cadena Actual:** Mantiene TODAS las sesiones continuas del agente actual (ej: Si Gy OF trabaja lunes, martes y miércoles, se guardan las 3).
2.  **Última del Otro:** Mantiene la última sesión registrada por un agente distinto (ej: La última de Gy CA del domingo).
3.  **Eslabón de Enlace:** Mantiene la última sesión propia *anterior* a la intervención del otro agente (para dar contexto de qué estaba haciendo yo antes de que el otro tocara el código).

### 4. Procedimiento Estándar

#### A. Inicio de Sesión
Al comenzar a trabajar, el agente debe ejecutar:
```bash
python scripts/session_manager.py start
```
*   Esto inserta un bloque "EN CURSO" en `MEMORIA_SESIONES.md`.
*   El agente debe leer este archivo para obtener contexto inmediato.

#### B. Cierre de Sesión
Al finalizar (antes de hacer commit/push o cerrar), el agente debe ejecutar:
```bash
python scripts/session_manager.py end "Resumen de lo hecho..."
```
*   **Resumen:** Debe ser conciso pero técnico. Mencionar archivos clave tocados y bugs resueltos.
*   El script se encargará de cerrar el bloque, poner la fecha de fin, y podar las sesiones antiguas según la lógica de retención.

#### C. Configuración de Nuevo Agente (Ej: Viaje)
Si se clona el repo en una nueva máquina:
1.  Crear archivo `.gy_identity` con el código del nuevo agente (ej: `NB`).
2.  Ejecutar `python scripts/session_manager.py start`.
3.  El sistema reconocerá al nuevo agente y comenzará a trackear sus sesiones, manteniendo la referencia a OF y CA según corresponda.

---

## Historial de Cambios Relevantes

### [2025-11-25] Operación Constelación (Maestros Satélites)
*   Implementación de módulos: Ramos, Vendedores, Listas de Precios, Agenda.
*   Seed de transporte virtual "RETIRO EN LOCAL" (ID 1).
*   Ajuste de UX en Transportes: Cierre automático de modal al guardar y botón de Baja.

### [2025-11-25] Estandarización UX Global (Norma DEOU)
*   **Implementación Masiva:** Se aplicaron las normas de atajos y comportamiento en todos los módulos (Transportes, Ramos, Vendedores, Listas, Personas, Clientes).
    *   `F10`: Guardar y Cerrar.
    *   `F4`: Nuevo registro (en listados).
    *   `Papelera`: Botón de baja lógica en listados.
*   **Refactor Técnico:** Creación de composable `useKeyboardShortcuts` para manejo centralizado de eventos.
*   **Base de Datos:** Migración para agregar campo `activo` a la tabla `personas`.

### [2025-11-25] Refactorización Ramo -> Segmento
*   **Cambio Semántico:** Se renombró la entidad "Ramo" a "Segmento" en todo el sistema (Base de Datos, Backend, Frontend, Documentación) para evitar ambigüedades con el concepto de "Rubro" de productos.
*   **Corrección de Bugs:**
    *   Solución a crash del Backend por error en Router de Maestros.
    *   Corrección en módulo Agenda (Personas): Se visualizaban como "Inactivos" por falta del campo `activo` en el schema de respuesta de la API.
*   **UI Standard:** Alineación de filtros "Todos/Activos/Inactivos" a la derecha en todos los listados para consistencia con el módulo Clientes.

    *   Se actualizó `ClienteService` para propagar el transporte seleccionado en la ficha del cliente hacia su domicilio predeterminado (Fiscal/Entrega).
*   **Frontend (ClienteForm):**
    *   **Tab 1 (General):** Integración de campos de domicilio legal para alta rápida. Creación automática de domicilio Fiscal/Entrega al guardar.
    *   **Transporte:** Campo obligatorio (con asterisco rojo). Se preselecciona "RETIRO EN LOCAL" si no hay otro.
    *   **Persistencia:** Solucionado bug donde el transporte no se guardaba/recuperaba correctamente en clientes existentes.
*   **SmartSelect:**
    *   Soporte para propiedad `required` (asterisco rojo).
    *   Corrección de "Race Condition" que borraba el valor seleccionado al cargar la lista asincrónicamente o al hacer click fuera prematuramente.
*   **Base de Datos:**
    *   Script de migración (`fix_legacy_transportes.py`) para asignar "RETIRO EN LOCAL" a todos los domicilios legados que no tenían transporte asignado.

### [2025-11-27] Pulido de Clientes y Domicilios
*   **Corrección de Bugs Críticos:**
    *   **Crash Frontend:** Solucionado `ReferenceError: onUnmounted` en `DomicilioGrid`.
    *   **Error de Guardado:** Se eliminó el campo `zona_id` del payload de Domicilios ya que no existía en el modelo, permitiendo guardar direcciones con "S/N".
*   **UX Domicilios:**
    *   **Dashboard:** Visualización en tiempo real de domicilios en la pestaña "General" (sin recarga).
    *   **Lógica de Transporte:**
        *   **Auto-relleno:** Al crear un nuevo destino, copia el transporte del Domicilio Fiscal.
        *   **Fallback:** Si se deja vacío, asigna automáticamente "Retiro en Local" (o el primero disponible) al guardar.
        *   **F10:** Se corrigió la captura de tecla para que F10 guarde el modal de domicilio si está abierto.
    *   **Visualización:** Se filtró el Domicilio Fiscal de la lista de entregas para evitar duplicados y conteo erróneo.

### [2025-11-27] Agenda y UX Avanzada (Sesión Nocturna)
*   **Módulo Agenda:**
    *   **Fix "Desconocido":** Se corrigió el schema del backend para incluir datos de la persona en la respuesta del vínculo.
    *   **Edición:** Se implementó la funcionalidad completa de edición de contactos (PUT) con botón dedicado.
    *   **Roles al Vuelo:** Implementación de creación de "Tipos de Contacto" directamente desde el formulario (F4).
*   **UX Premium:**
    *   **CopyTooltip:** Componente estilo "Gmail" para Email y WhatsApp. Al pasar el mouse, muestra el dato completo y permite copiarlo con un clic.
    *   **WhatsApp Input:** Campo inteligente con prefijo automático (+54 9) y limpieza de basura.
*   **Correcciones:**
    *   **Fix 422:** Sanitización de payloads para evitar errores de validación con campos vacíos.
    *   **Fix Top Clients:** Se blindó el schema de `ClienteResponse` para tolerar valores nulos en `saldo` y `contador_uso`, recuperando la lista de frecuentes.
    *   **Fix Import:** Corrección de referencia circular/errónea en `backend/clientes/router.py`.

### [2025-11-29] Replicación de Menú Contextual y ABM Maestros
*   **Backend (Maestros):**
    *   Implementación de CRUD completo (API + Schemas) para `Provincias`, `CondicionesIva` y `TiposContacto`.
    *   Validación de integridad referencial y manejo de errores.
*   **Frontend (Context Menu):**
    *   **Componente Reutilizable:** Creación de `ContextMenu.vue` para uso global.
    *   **Dashboard (HaweView):**
        *   Integración en lista lateral de "Segmentos" (Editar/Borrar).
        *   Integración en tarjetas de "Clientes" (Nueva Ficha, Administrar, Editar, Baja, IA).
        *   Integración en enlace "Clientes" del sidebar (Nuevo, Administrar).
    *   **ClientCanvas:**
        *   Integración en etiqueta "Segmento" del formulario (Nuevo, Administrar).
*   **UI/UX Refinements:**
    *   **Navegación:** Corrección de flujo entre "Fichas", "Nuevo Cliente" y Dashboard.
    *   **Estilos:** Rediseño de botones en cabecera de ficha para evitar confusión (Fichas resaltado, Nuevo sutil).
    *   **Feedback:** Mejoras en la indicación visual de contexto.

### [2025-11-30] Refactorización Logística y Domicilios (Tabs)
*   **Cambio Arquitectónico:**
    *   **Interfaz por Pestañas:** Se reemplazó el uso de modales flotantes por un sistema de pestañas (`CLIENTE`, `DOMICILIO`, `CONTACTO`) integrado en el canvas central de `ClientCanvas.vue`.
    *   **DomicilioForm:** Conversión de componente modal a componente de canvas, con botones "Volver" y "Guardar" integrados.
*   **UX/UI:**
    *   **Sidebar Logística:** Botones "FICHA - NUEVO" siempre visibles en cabecera de Domicilios.
    *   **Menú Contextual:** Implementado en cabecera de Domicilios (Nuevo, Administrar) y en tarjetas individuales (Editar, Eliminar).
    *   **Navegación:** Doble clic en tarjeta de domicilio abre la pestaña de edición correspondiente.
*   **Corrección de Bugs:**
    *   **Inicialización Formulario:** Se corrigió bug donde el doble clic abría el formulario de alta en lugar de edición (watcher de `domicilio` con `immediate: true`).
*   **Próximos Pasos (Pendientes):**
    *   Implementar navegación en bucle (loop) con flechas Arriba/Abajo en tarjetas de Domicilio.
    *   Implementar ABM completo de Transportes.

### [2025-11-30] Navegación Domicilios y ABM Transportes
*   **Domicilios (UX):**
    *   **Navegación por Teclado:** Se implementó navegación con flechas Arriba/Abajo en la lista de domicilios (`DomicilioGrid`).
    *   **Looping:** La navegación es circular (del último al primero y viceversa).
    *   **Foco:** Se añadió `tabindex="0"` y feedback visual para indicar la tarjeta activa.
*   **Transportes (Hawe):**
    *   **ABM Completo:** Se implementó la gestión completa de Transportes en `HaweTransportesView.vue`.
    *   **Funcionalidad:** Alta, Baja (Soft Delete), Modificación y Listado.
    *   **Campos:** Nombre, Teléfono Reclamos, Web Tracking, Activo, Requiere Carga Web, Formato Etiqueta.
    *   **Integración:** Conectado a `useLogisticaStore` y `useNotificationStore`.
*   **UI/UX:**
    *   **ClientCanvas:** Se separó el encabezado "Logística & Contactos" en dos secciones independientes: "LOGÍSTICA" y "CONTACTOS" para mayor claridad visual.
    *   **Estilo de Títulos:** Se aplicó un diseño destacado (texto cyan, fondo sutil, borde) a los títulos de sección en el panel derecho.
    *   **Fondo Global:** Se cambió el color de fondo principal de Negro (`#0a0a0a`) a Azul Profundo (`#0a1f2e`) para alinear con la identidad del módulo Clientes.
    *   **Listas de Gestión:** Se estandarizó el diseño de "Administrar Segmentos" y se creó "Administrar Domicilios" con tema oscuro, búsqueda y acciones con íconos, accesibles desde el menú contextual.
*   **Limpieza de Proyecto:**
    *   **Eliminación de Legacy:** Se eliminaron las carpetas `views/Clientes` y `views/Logistica` que contenían código obsoleto.
    *   **Router:** Se limpiaron las rutas antiguas `/clientes` y `/transportes`, centralizando todo en el módulo `Hawe`.
*   **Correcciones y Mejoras:**
    *   **Iconos:** Se actualizaron todos los iconos a `fa-solid` (FontAwesome 6) para solucionar problemas de visualización en listas y formularios.
    *   **Protección Fiscal:** Se implementó la lógica para impedir el borrado de domicilios fiscales en `DomicilioList.vue`.
    *   **Consistencia UI:**
        *   Se renombró "Maestro de Segmentos" a "Administrar Segmentos".
        *   Se habilitó el **doble click** en los títulos "SEGMENTOS" (en `ClientCanvas.vue` y en el sidebar de `HaweView.vue`) y "LOGÍSTICA" para abrir sus respectivas ventanas de administración.
        *   Se restauraron los **iconos** (Lápiz y Tacho) en las listas, asegurando su visibilidad con colores de alto contraste (`text-cyan-400` y `text-red-400`) y usando las clases más compatibles `fa-solid fa-pencil` y `fa-solid fa-trash` con dimensiones explícitas (`w-4 h-4`).
    *   **Corrección de Bug:** Se solucionó un error de sintaxis en `ClientCanvas.vue` (etiqueta `<aside>` mal cerrada) que surgió durante la refactorización.
    *   **Infraestructura:** Se instaló **FontAwesome localmente** (`npm install @fortawesome/fontawesome-free`) y se eliminó la dependencia del CDN para garantizar que los iconos funcionen offline y sin bloqueos de navegador (Brave Shields, AdBlockers).
    *   **Mejoras en DomicilioList:**
        *   Se agregaron los **filtros** "Todos / Activos / Inactivos" (reemplazando "Fiscal/Sucursal" en la barra de filtros para consistencia con Segmentos).
        *   Se corrigió la **edición**: Ahora al hacer click en el lápiz, se cierra la lista y se abre correctamente la pestaña de edición del domicilio seleccionado.
        *   **Baja Lógica (Soft Delete):** Se implementó la baja lógica para domicilios.
            *   **Backend:** Se agregó la columna `activo` a la tabla `domicilios` mediante script de migración.
            *   **Frontend:** La lista de domicilios ahora permite filtrar por estado. Los domicilios dados de baja se muestran en gris en la lista de "Inactivos" y se ocultan del panel principal del cliente.
    *   **Mejoras en DomicilioForm:**
        *   **Toggle Activo:** Se agregó un interruptor para activar/desactivar domicilios desde la edición.
        *   **Botón Guardar:** Se añadió un botón explícito "GUARDAR CAMBIOS" al final del formulario.
        *   **Fix F10:** Se mejoró la captura de la tecla F10 para evitar conflictos y asegurar el guardado.
    *   **Reactivación de Clientes:**
        *   Se reemplazó la etiqueta estática de estado en la cabecera de la ficha del cliente por un **Interruptor (Switch)** funcional.
        *   Esto permite reactivar clientes dados de baja (o desactivar activos) directamente desde la ficha.
    *   **Corrección de Persistencia de Domicilios:**
        *   Se modificó `ClientCanvas.vue` para que, al editar un cliente existente, las altas y modificaciones de domicilios se guarden **inmediatamente** en el backend (usando `store.createDomicilio` / `store.updateDomicilio`).
        *   Esto soluciona el problema de pérdida de datos, ya que el endpoint de actualización de cliente no procesaba los domicilios anidados.
    *   **Corrección Baja de Cliente:**
        *   Se habilitó la función `deleteCliente` en `ClientCanvas.vue` para permitir la baja lógica desde el botón inferior.
    *   **Corrección de Error de Sintaxis:**
        *   Se eliminó un bloque de código duplicado en `ClientCanvas.vue` que causaba un error de compilación `[vue/compiler-sfc] Unexpected token`.

## Cierre de Sesión - 01/12/2025

### Resumen de Logros
Se completó una sesión intensiva de depuración y mejora de la gestión de Clientes y Domicilios.

1.  **Infraestructura de Domicilios:**
    *   Implementación completa de **Soft Delete** (Baja Lógica) para domicilios.
    *   Refactorización de `DomicilioForm` con navegación por teclado, botón de guardado explícito y toggle de estado.
    *   Creación de `DomicilioList` estandarizado con filtros (Todos/Activos/Inactivos) y búsqueda.

2.  **Gestión de Clientes (Hawe):**
    *   **Reactivación:** Implementación de un **Switch de Estado** en la cabecera de la ficha del cliente, permitiendo reactivar clientes dados de baja de manera intuitiva.
    *   **Corrección Crítica de Datos:** Se solucionó el bug donde la reactivación de un cliente provocaba la pérdida de sus domicilios. Esto se logró desacoplando el guardado de domicilios del guardado del cliente principal, forzando la persistencia inmediata de los cambios logísticos.
    *   **Baja de Cliente:** Se reparó la funcionalidad del botón "Dar de Baja", asegurando la correcta actualización de estado y redirección.

3.  **Estabilidad del Código:**
    *   Se eliminó una duplicación masiva de código en `ClientCanvas.vue` que generaba errores de compilación y comportamiento errático.

### Próximos Pasos
*   **Monitoreo:** Verificar en producción (o entorno de pruebas extendido) que la reactivación de clientes con historiales complejos de domicilios funcione correctamente.
*   **Refactorización Backend:** Evaluar si el endpoint `update_cliente` debería soportar actualizaciones anidadas de domicilios para simplificar la lógica del frontend en el futuro, aunque la solución actual de "guardado inmediato" es robusta y previene pérdida de datos.




### [2025-12-01] Estandarización de Layouts y Terminología
*   **Layout Unificado:** Se estandarizó el diseño de los módulos `Transportes` y `Contactos` para que coincidan con `Clientes`:
    *   **Sidebar Izquierdo:** Menú de navegación persistente.
    *   **Contenido Central:** Listado de registros.
    *   **Inspector Derecho:** Panel fijo (320px) para edición/creación, siempre visible (con placeholder cuando no hay selección).
*   **Terminología Logística:**
    *   Se renombró "Depósitos" a **"Depósitos Internos"** en el menú lateral para diferenciar los almacenes propios de la empresa de los domicilios de entrega de los clientes.
    *   *Pendiente de revisión:* Evaluar si el término sigue siendo ambiguo.
*   **Corrección de Bugs:**
    *   **Ghost Screen:** Se solucionó el parpadeo del layout antiguo al recargar la página (`Ctrl+F5`) implementando un estado de carga (`ready`) en `App.vue` que espera a que el router esté listo.
    *   **Persistencia de Menú:** Se implementó `useUIStore` para recordar el estado (abierto/cerrado) de las categorías del sidebar entre navegaciones.
