# Bitácora de Migración de Legado (Legacy System)

Este documento registra el análisis, estrategias y herramientas desarrolladas para migrar datos desde sistemas heredados (Excel, CSV, Bases anteriores) hacia Sonido Líquido V5.

## Principios
*   **Separación de Intereses:** Este proceso corre paralelo al desarrollo de V5 y no debe ensuciar el código fuente principal.
*   **Triangulación:** No confiar en un único dato (ej: CUIT) para identificar entidades. Usar múltiples puntos de validación (Nombre + CUIT + Dirección).
*   **Polimorfismo:** Los scripts de ingesta deben adaptarse a los cambios de formato históricos (ej: enroque de columnas Precio/Costo en pestañas de años recientes).

---

## [2025-12-06] Análisis Inicial de "Pedidos Real" (Excel)

Se analizó el archivo `pedidos_raw.xlsx` provisto por el usuario.

### Hallazgos Estructurales
1.  **Metadata Dispersa:**
    *   Cliente: En encabezado (Fila 1 aprox).
    *   CUIT: En cuerpo superior (Fila 13 aprox).
    *   Referencia Pedido: En encabezado.
2.  **Cuerpo del Pedido:**
    *   Estructura tabular variable.
    *   Patrón detectado: Descripción de producto seguido de Cantidad y Valores monetarios.
3.  **Variaciones Temporales (El "Enroque"):**
    *   Se detectó que en pestañas recientes cambió el orden de columnas (Precio Venta / Costo), presumiblemente para captura de pantalla (WhatsApp).

### Estrategia de Ingesta Propuesta
1.  **Detección de Versión:** El script debe leer las primeras filas para identificar qué versión de plantilla es (Pre-Enroque o Post-Enroque).
2.  **Validación Difusa:** Si el CUIT parece inválido o duplicado por error de "Copy/Paste", usar el Nombre del Cliente para sugerir o validar contra la base maestra.
3.  **Offline-First:** Todo el análisis y limpieza se hace localmente con Python (`pandas`). Solo la escritura final requiere conexión a la DB de V5.

### Scripts Desarrollados
*   `analyze_pedidos.py`: Escaneo general de estructura y hojas.
*   `get_patterns.py`: Búsqueda de patrones específicos (keywords, regex de CUIT).
*   `get_patterns.py`: Búsqueda de patrones específicos (keywords, regex de CUIT).
*   `dump_excel.py`: Volcado crudo para inspección visual.

### [2025-12-06] Definición Estrategia de Recuperación de Historial
Ante la limitación de "Mis Comprobantes" (solo cabeceras) y la necesidad de detalle de productos:
1.  **Triangulación Principal:** Cruzar Cabeceras ARCA (CSV) vs Totales Pedidos Internos (Excel).
    *   Si Monto y Fecha coinciden -> Asumimos que los ítems del Excel son la verdad.
2.  **Scraping Selectivo (Fallback):** Para las facturas que NO coincidan (inconsistencias o pedidos no registrados), se desarrollará un "Micro-Scraper" para consultar RCEL (Comprobantes en Línea).
    *   **Táctica:** Lotes pequeños (6-7 consultas) espaciados en el tiempo para evitar bloqueos de AFIP.
    *   **Objetivo:** Obtener el detalle de ítems solo cuando sea estrictamente necesario.
