# SESION HANDOVER - TRANSICIÓN A PILOTO V5

**Fecha:** 10/12/2025
**Objetivo:** Iniciar la operación "Piloto" con datos reales y herramienta de carga táctica.

## Estado Actual (Lo que se logró hoy)
1.  **Infraestructura:** Creada carpeta `BUILD_PILOTO` con estructura de producción (portable).
2.  **Minería de Datos:** Script `harvest_excel.py` ejecutado con éxito.
3.  **Resultados de la Cosecha:**
    *   `data/clientes_raw.csv`: ~200 clientes detectados. Muchos duplicados ("Centro Pet" vs "Centro PET") y faltantes de CUIT.
    *   `data/productos_raw.csv`: ~300 productos. Variaciones de nombre ("1 litro", "1 Lt", "1L"). Precios de referencia capturados (último detectado).

## Plan para Mañana (Día de la Marmota)

### FASE 2: Limpieza (First Task)
*   **No vamos a limpiar CSV a mano.**
*   Vamos a crear un script rápido que inyecte todo esto en `produccion.db` marcado como "A Revisar".
*   Usaremos la UI de V5 (que es más amigable) para fusionar clientes y renombrar productos.

### FASE 3: Implementación "Cargador Táctico"
Desarrollar la pantalla sencilla de pedidos que solicitaste:
1.  **Inputs:** Cliente (Select) + Producto (Select) + Cantidad + Precio Manual.
2.  **Output A:** Guarda en BD limpia.
3.  **Output B:** Genera Excel "Old Style" para enviar/imprimir.

## Próximos Pasos (To-Do List para Gy Mañana)
1.  [ ] Crear script `inject_raw_data.py`: Leer los CSVs crudos e insertar en `sql_app.db` (o `produccion.db`).
2.  [ ] Agregar campo `origen_dato="IMPORTADO_RAW"` en modelos para identificar lo sucio.
3.  [ ] Implementar herramienta de "Fusión de Clientes" en Frontend (Si selecciono 2, que quede 1).
4.  [ ] Diseñar la vista `PedidoTacticoView.vue`.

**Mensaje para Gy del Futuro:**
"La cosecha fue buena pero ruidosa. Enfocate en herramientas de limpieza en la UI antes de abrir el grifo de pedidos. No te olvides del CUIT."
