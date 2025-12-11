# Diseño Técnico: Cargador Táctico (Grid V5)
**Nombre Clave:** "Excel Killer"
**Objetivo:** Interfaz de carga de pedidos de alta velocidad que simula una planilla de cálculo pero opera directamente sobre la base de datos V5.

## 1. Filosofía de Diseño
*   **Keyboard First, Mouse Friendly:** Optimizado para teclado (`Enter`, `Tab`), pero con botón "OK" / "Procesar" accesible vía click para cierres rápidos.
*   **Feedback Inmediato:** Precios, descuentos y stock se calculan en tiempo real.
*   **Flexibilidad "Anti-Bloqueo":** Si el precio no existe, permite carga manual (con log). Si falta un dato, permite avanzar (dentro de lo legal).

## 2. Interfaz de Usuario (UI)

### A. Cabecera (Contexto del Pedido)
*   **Info Operativa:**
    *   **Nº Pedido:** Contador Automático (Sugiere el siguiente).
    *   **Fecha:** Selector de Fecha (Default: Hoy).
*   **Selector de Cliente (F2):** Autocompletado. Muestra:
    *   *Deuda Actual* (Color coded).
    *   *Saldo a Favor*.
*   **Modo de Transacción:**
    *   **Tipo:** [Pedido] / [Presupuesto] (Toggle).
    *   **Fiscal:** [Con IVA] / [Sin IVA/X] (Oculta impuestos en totales).
*   **Comentarios:** Campo de texto libre para notas logísticas ("Entregar por puerta lateral", "Entrega Parcial acorada", etc.).

### B. La Grilla (Carga de Items)
Comportamiento tipo hoja de cálculo.
Columnas:
1.  **Código:** Buscador exacto.
2.  **Producto (F3):**
    *   Búsqueda difusa al escribir.
    *   **F3 (DEOU):** Abre modal de "Ayuda de Búsqueda" con listado filtrable.
3.  **Cant:** Número.
4.  **Unidad:** Selector rápido.
5.  **Precio Unit:**
    *   Automático desde Lista V5.
    *   **Editable:** Permite sobre-escritura manual.
    *   *Helper:* Mostrar "Último Precio Pagado" por este cliente (Tooltip o panel lateral).
6.  **Desc %:** Descuento manual de línea.
7.  **Subtotal:** (Cant * Precio * (1-Desc)).
8.  **Acciones:** Icono Papelera (Eliminar fila).

### C. Pie (Totales y Cierre)
*   **Desglose:** Neto, IVA (si aplica), Total Final.
*   **Botones:**
    *   `[F10] PROCESAR PEDIDO`: Guarda en DB y limpia formulario.
    *   `[Guardar Borrador]`: Persiste en LocalStorage sin enviar a DB.

## 3. Comportamientos Clave
*   **Navegación:** `Flechas` para moverse entre celdas. `Enter` para avanzar/confirmar.
*   **F3 (Smart Lookup):** En cualquier campo "Buscable" (Cliente, Producto), F3 abre el catálogo completo.
*   **Historial de Precios:** Al seleccionar un producto, consultar asíncronamente "Última venta a este cliente" y mostrarla discretamente.

## 4. Estrategia Técnica
*   **Componente:** `views/Ventas/GridLoader.vue`.
*   **Store:** `usePedidoStore` (Pinia) para gestión de estado reactivo complejo.
*   **Persistencia Local:** `localStorage` bajo key `v5_draft_grid`.
*   **Backend:** Reutilizar y robustecer `POST /pedidos`. Agregar endpoint `GET /ventas/ultima_venta/{cliente_id}/{producto_id}`.

## 5. Plan de Implementación
1.  **Fase 1 (Esqueleto):** UI Grilla + Cabecera con los nuevos campos (Fecha, Modo, Comentarios).
2.  **Fase 2 (Conectividad):**
    *   Buscadores (Clientes/Productos).
    *   Implementar F3 (Modal de Ayuda).
    *   Endpoint y UI de "Último Precio".
3.  **Fase 3 (Lógica de Negocio):**
    *   Cálculo de Totales (con/sin IVA).
    *   Validación "Flexible" (Precios manuales).
4.  **Fase 4 (Commit):** Guardado final en DB y manejo de errores.
