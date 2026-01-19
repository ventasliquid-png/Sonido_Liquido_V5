# INFORME HISTÓRICO: SESIÓN 19 DE ENERO 2026
**Fecha:** 19/01/2026
**Foco:** Estabilización de UI/UX en `PedidoCanvas.vue`

## 1. Resumen Ejecutivo
Esta sesión se centró en resolver problemas críticos de visualización y compilación introducidos durante la refactorización del módulo de "Nuevo Pedido" (`PedidoCanvas`). Se logró restablecer la estabilidad estructural del HTML, corregir la lógica de scroll y capas (z-index), y refinar la experiencia de carga de productos.

## 2. Problemas Abordados y Soluciones

### A. Error de Compilación ("Invalid End Tag")
*   **El Problema:** Un error persistente de `[plugin:vite:vue] Invalid end tag` impedía la visualización. Se originó por divs de cierre (`</div>`) huérfanos o duplicados tras múltiples ediciones de la estructura del layout.
*   **La Solución:** Se realizó una limpieza quirúrgica del final del archivo `PedidoCanvas.vue`, eliminando etiquetas redundantes y comentarios que rompían la jerarquía del DOM.

### B. Layout y Pie de Página (Footer)
*   **El Problema:** El pie de página (con los totales y botón guardar) desaparecía o se empujaba fuera de la pantalla al agregar muchos productos.
*   **La Dificultad:** La combinación de Flexbox anidados sin restricciones de altura (`min-h-0`) causaba que el contenedor creciera infinitamente en lugar de activar el scroll interno.
*   **La Solución:**
    1.  Se aplicó `min-h-0` y `overflow-hidden` al contenedor flexible padre.
    2.  Se movió el componente `RentabilidadPanel` a la raíz del template para evitar que interfiera en el flujo del layout principal.
    3.  Se blindó el área de la grilla de productos con `overflow-y-auto`.

### C. Panel de Rentabilidad (Cost Drawer)
*   **El Problema:** El panel lateral quedaba "recortado" o invisible debido al contexto de apilamiento (z-index) dentro del contenedor principal. Además, la lógica del ícono Chevron estaba invertida (apuntaba a la dirección contraria a la intuición del usuario).
*   **La Solución:**
    1.  **Z-Index:** Mover el componente al final del `template` (fuera de los divs de estructura) permitió que se superponga correctamente sobre toda la interfaz (fixed position).
    2.  **UX:** Se invirtieron los íconos: Ahora usa `<` (Izquierda) para abrir el panel y `>` (Derecha) para cerrarlo/esconderlo.

### D. Refinamientos de UX (Lista de Pedido)
*   **Grilla:** Se implementó una grilla de 12 columnas con numeración de renglón (#) fija.
*   **Scroll Automático:** Se agregó lógica para que al dar "Enter" en un nuevo producto, la lista haga scroll automáticamente hasta el final para mostrar el ítem recién agregado.
*   **Alineación:** Se nivelaron visualmente los inputs de Descuento para coincidir con el tamaño de los inputs de Precio y Cantidad.

## 3. Dificultades Encontradas
*   **Complejidad del DOM:** La estructura de `PedidoCanvas` se volvió compleja con múltiples secciones anidadas (Header compacto, Body grid, Footer flotante, Drawer lateral), lo que facilitó errores de anidación (el error del `</div>`).
*   **Reatividad de Vue y DOM:** Sincronizar el scroll automático (`scrollTop`) con la actualización del array de items requirió asegurar que el DOM estuviera actualizado (`nextTick` o `setTimeout`) antes de scrollear.

## 4. Logros
*   ✅ Sistema de "Nuevo Pedido" visualmente estable.
*   ✅ Footer anclado correctamente (no desaparece).
*   ✅ Panel de Costos 100% funcional y accesible.
*   ✅ Flujo de carga "Teclado-Friendly" (Enter -> Pasa a Cantidad -> Enter -> Agrega -> Scroll Fondo).

## 5. Sugerencias para Próxima Reunión
1.  **Filas "Sticky" (1 y 2):** El usuario sugirió mantener fijas las primeras filas mientras se scrollea el resto. Esto requiere una reingeniería de la tabla (posiblemente dos tablas sincronizadas o uso avanzado de `position: sticky` en una estructura de tabla real, no divs).
2.  **Validación de Guardado:** Realizar pruebas de estrés sobre el guardado del pedido completo en la base de datos verificar que todos los campos (descuentos globales, transportes) viajen correctamente al backend.
3.  **Edición Avanzada:** Verificar la edición de pedidos existentes (re-hidratación del formulario) con la nueva estructura de datos.
