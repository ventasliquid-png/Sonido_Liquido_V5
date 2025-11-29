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
