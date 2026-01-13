# Diseño Técnico: Cargador Táctico (Grid V5)
**Nombre Clave:** "Excel Killer"
**Objetivo:** Interfaz de carga de pedidos de alta velocidad que simula una planilla de cálculo pero opera directamente sobre la base de datos V5.

## 1. Filosofía de Diseño
*   **Keyboard First, Mouse Friendly:** Optimizado para teclado (`Enter`, `Tab`), pero con botón "OK" / "Procesar" accesible vía click para cierres rápidos.
*   **Feedback Inmediato:** Precios, descuentos y stock se calculan en tiempo real.
*   **Flexibilidad "Anti-Bloqueo":** Si el precio no existe, permite carga manual (con log). Si falta un dato, permite avanzar (dentro de lo legal).

## 2. Interfaz de Usuario (UI) - Estructura Tríptica

### A. Cabecera (Contexto Administrativo)
*   **Datos Identitarios:** Ficha de Cliente (Nombre, CUIT, Semáforo).
*   **Datos Operativos:** 
    *   **Fecha/Hora:** Automática.
    *   **Numero de Pedido:** Contador correlativo.
    *   **OC Cliente:** Campo opcional para referencia externa.
*   **Semántica:**
    *   Color de fondo cambia según el tipo de documento.

### B. El Cuerpo (Grilla Transaccional)
Es el corazón del sistema. Una lista de "n" renglones con:
1.  **#:** Número de renglón.
2.  **SKU:** Identificador único.
3.  **Descripción:** Nombre del producto.
4.  **Cant:** Cantidad solicitada.
5.  **Unidad:** Medida (UN, CJ, etc).
6.  **Precio Unitario:** Valor base.
7.  **Subtotal:** (Cant * Precio).
*   **Descuentos:** Se agregan como un renglón especial con valor negativo antes del final.

### C. Pie (Liquidación y Logística)
*   **Totales:**
    *   **Subtotal Neto:** Suma de renglones.
    *   **IVA:** Discriminado (21% / 10.5%).
    *   **Total Final:** Monto a pagar.
*   **Logística:**
    *   **Cambio Logístico:** Selector para alterar el destino/transporte por defecto del cliente (Override).

## 3. Semántica Visual (Color Coding)
El fondo general de la grilla (muy suave) comunica el estado/tipo de documento:
*   🟢 **Verde Suave:** PEDIDO (Firme).
*   🟣 **Lila Suave:** PRESUPUESTO (Cotización).
*   🟡 **Amarillo Suave:** COMPLETADO / ARCHIVADO.
*   🔴 **Rojo Suave:** ANULADO.

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
