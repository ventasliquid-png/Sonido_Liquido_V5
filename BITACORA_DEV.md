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
