# PLAN TÉCNICO GY - HOJA DE RUTA INMEDIATA (V5.3)

**Contexto:** Transición a Fase Piloto. Ingesta de datos legacy y creación de herramienta de carga táctica.

## 1. INGENIERÍA DE DATOS (Ingesta y Limpieza)

### A. Script de Inyección (`scripts/inject_raw_data.py`)
*   **Input:** `BUILD_PILOTO/data/clientes_raw.csv` y `productos_raw.csv`.
*   **Lógica:**
    *   Iterar CSVs.
    *   Insertar en tablas `clientes` y `productos`.
    *   **Flag clave:** Establecer un campo (o tag) que identifique estos registros como `IMPORTADO_RAW` o `REQUIERE_REVISION`.
    *   *Nota:* Si el modelo no tiene campo de estado de validación, considerar agregarlo o usar una categoría especial (ej: Rubro "A CLASIFICAR").
    *   **Manejo de Duplicados:** Si el CUIT/Nombre ya existe, **no sobrescribir**, loguear la colisión o crear con sufijo "(DUP)".

### B. Backend Updates
*   **Schema `Cliente` / `Producto`:** Verificar si necesitamos un campo `is_validated` o `data_source`.
    *   *Decisión Rápida:* Usar un "Tag" o "Rubro" temporal es menos invasivo que cambiar el schema físico por ahora. Ej: Productos van al Rubro "SIN CLASIFICAR".

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
