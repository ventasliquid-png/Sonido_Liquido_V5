# INFORME HISTÓRICO: Parche Defensivo Remitos + UI Z-Index Refactor (2026-06-10)

## Resumen Ejecutivo
Durante la sesión 823 en OF (Operaciones Front), se atacaron dos problemas críticos que estaban generando errores 500 y defectos visuales en la interfaz del sistema. Además, se limpió la base de datos de basura residual por la ausencia de un borrado en cascada en las relaciones de ítems.

## Intervención 1: Parche Defensivo PDF
- **El Problema:** Al intentar imprimir un remito cuyos renglones de pedido (`PedidoItem`) habían sido eliminados en la base de datos (debido al comportamiento de borrado físico / hard-delete que no propagaba en cascada a `RemitoItem`), el motor PDF fallaba estrepitosamente con un `AttributeError` (NoneType object has no attribute 'producto').
- **La Solución:** Se inyectó una guardia defensiva en `get_remito_pdf` (`backend/remitos/router.py`). Si `r_item.pedido_item` es nulo, o si no tiene producto, el PDF imprime `"ÍTEM DESCONOCIDO"` y continúa su ejecución en lugar de fallar.
- **Deuda Técnica Levantada:** Es imperativo agregar la cláusula `ON DELETE CASCADE` de `PedidoItem` a `RemitoItem` en el modelo, o manejar la consistencia en el servicio de borrado para evitar estos registros "zombies".

## Intervención 2: Refactor UI Z-Index en PedidoCanvas
- **El Problema:** El menú desplegable del buscador de productos Cantera en `PedidoCanvas.vue` quedaba truncado al final del contenedor de ítems. Esto se debía al comportamiento restrictivo de `overflow-hidden` aplicado a los contenedores padres.
- **La Solución:** Se aplicó una reestructuración espacial de las etiquetas. El `<footer>` se reubicó dentro del contenedor `overflow-hidden`. Se aumentó la jerarquía (Z-Index) del contenedor principal (`<main>` a `relative z-50`) superando al footer (`relative z-40`). Al compartir el mismo contexto de desbordamiento, el menú de la cantera ahora puede fluir sobre el footer sin ser "cortado" por un borde invisible.

## Intervención 3: Limpieza Transaccional (pilot_v5x.db)
- **Operación:** Intervención directa vía SQLite para eliminar restos transaccionales fallidos.
- **Ejecución:**
  - Borrado de **16 facturas huérfanas** que habían quedado desvinculadas.
  - Borrado de **12 remitos huérfanos** cuyas referencias al pedido original eran nulas.
  - Eliminación física de los **Pedidos #47 y #48**, usados como casos de prueba fallidos en la sesión.

## Sincronización P y Cierre OMEGA
- Ambos arreglos de código fueron fusionados en un par de commits, los cuales fueron replicados mediante `cherry-pick` en el repositorio paralelo de Producción (`v5-ls-Tom`).
- Se resolvieron conflictos menores en P (por discrepancias UI) y se hizo push a `origin`.
- **OMEGA V3.0** se ejecutó satisfactoriamente (Canario NOMINAL GOLD), finalizando la sesión y estableciendo la base estable para futuras interacciones.
