# PLAN TÉCNICO GY - HOJA DE RUTA INMEDIATA (V5.3)

**Contexto:** Transición a Fase Piloto. Ingesta de datos legacy y creación de herramienta de carga táctica.

## 1. INGENIERÍA DE DATOS (Estrategia "Master CSV")
**Principio:** Los datos validados ("ciudadanos de primera") deben residir en archivos CSV Maestros (`_master.csv`) que sirven como respaldo ante catástrofes. La base de datos es una proyección de estos archivos.

### A. Flujo de Limpieza y Persistencia
1.  **Fuente:** `_raw.csv` (Datos crudos de legacy).
2.  **Depurador:** Lee Raw o Limpios temporales.
3.  **Acción "IMPORTAR/APROBAR":**
    *   **DB:** Inserta el registro en la base de datos operativa (SQLite/Cloud).
    *   **Master CSV:** *Appendea* (agrega al final) el registro validado a `clientes_master.csv` o `productos_master.csv`.
4.  **Recuperación:** En caso de desastre, se puede repoblar la base re-importando los `_master.csv`.

### B. Estructura de Archivos (BUILD_PILOTO/data)
*   `clientes_raw.csv` / `productos_raw.csv`: Ingesta inicial sucia.
*   `clientes_master.csv` / `productos_master.csv`: La "Verdad" validada y acumulada.


## 2. FRONTEND - HERRAMIENTAS DE LIMPIEZA

### A. UI de Fusión (Merge Tool)
*   **Lugar:** `ClienteList.vue` y `ProductosList.vue`.
*   **Feature:**
    *   Selectbox múltiple (Checkboxes en la lista).
    *   Botón de Acción: "Fusionar Seleccionados".
    *   **Modal de Fusión:**
        *   Muestra los candidatos.
        *   Pregunta: "¿Cuál es el Master?" (El que queda).
        *   Acción: Reasigna relaciones (si las hubiera, aunque en inicio no hay) y hace Soft Delete de los otros.

## 3. EL "CARGADOR TÁCTICO" (Tactical Order Loader)

### A. Nueva Vista: `PedidoTacticoView.vue`
*   **Ruta:** `/pedidos/tactico` (Nueva entrada en Sidebar).
*   **Componentes:**
    1.  **Header:** Fecha, N° Pedido (Autogenerado o Manual), Nota/OC.
    2.  **Cliente:** `SmartSelect` (Buscando en la base ya inyectada).
    3.  **Grid de Ítems:**
        *   Producto (`SmartSelect` de Productos).
        *   Cantidad (Input Number).
        *   Precio Venta (Input Currency - Inicializado con precio de lista si existe).
        *   Subtotal (Calculado).
        *   Botón Eliminar Fila.
    4.  **Footer:** Totales. Botón "GUARDAR Y EXPORTAR".

### B. Servicio de Exportación (Backend)
*   **Endpoint:** `POST /pedidos/tactico`
*   **Payload:** Estructura del pedido.
*   **Acción:**
    1.  Guardar en BD (Tabla `pedidos` - ¿Existe? Si no, crear modelo simplificado o usar JSON por ahora).
    2.  **Generación Excel:** Usar `openpyxl` o `pandas`.
        *   Template: Cargar el formato "Viejo" que le gusta al usuario.
        *   Fill: Llenar celdas.
    3.  **Response:** Devolver el archivo binario (`blob`) para descarga inmediata.

## 4. INFRAESTRUCTURA PILOTO
*   Verificar que `BUILD_PILOTO` sea autosuficiente.
*   Probablemente necesitemos copiar el `venv` o instruir cómo crearlo en la máquina destino (el `.bat` ya lo contempla).
