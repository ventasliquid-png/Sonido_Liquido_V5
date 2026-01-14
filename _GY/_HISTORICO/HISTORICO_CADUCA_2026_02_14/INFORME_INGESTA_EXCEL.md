# Informe de Análisis de Datos para Ingesta (Piloto V5)

## 1. Estado del Arte (Fuente de Datos)
El archivo `pedidos_raw.xlsx` contiene la historia transaccional del negocio. Su estructura no es una base de datos plana, sino una **colección de "Fichas de Pedido"** dispuestas en una hoja de cálculo.

### Estructura Detectada
Se identificaron dos patrones principales de almacenamiento:

#### A. Patrón Moderno (2024 - 2025)
*   **Disposición:** Vertical (Un pedido abajo del otro).
*   **Formato de Lista de Precios:** "Venta Primero" (Optimizado para copiar/pegar al cliente).
*   **Columnas Clave:**
    *   `C`: Precio de Venta (Más caro)
    *   `G`: Costo Unitario (Más barato)
*   **Datos de Cabecera:** Pedido N°, Cliente, Fecha, CUIT (A veces ausente).

#### B. Patrón Clásico (Hoja "Pedidos")
*   **Disposición:** **Matriz Compleja**. Se detectaron pedidos en paralelo (Varias columnas de pedidos en la misma fila).
    *   *Ejemplo:* Filas 0-7 contienen un pedido, y filas 8-15 contienen OTRO pedido distinto a la misma altura.
*   **Formato de Lista de Precios:** "Costo Primero" (Formato contable tradicional).
    *   `Costos`: Columnas previas.
    *   `Ventas`: Columnas posteriores.

## 2. Anomalías y Desafíos Detectados
1.  **Multi-Columna en Histórico:**  **ACLARACIÓN (11/12):** El usuario confirma que los pedidos válidos terminan en la **Columna 8 (H)**. Todo lo que esté a la derecha (Columnas I en adelante) es basura/auxiliar y debe ser ignorado por el script. Esto simplifica el barrido: cada fila contiene *solo un pedido* (o vacío), no múltiples.
2.  **Identidad de Productos:**
    *   Variaciones de nombre: `Surgizime E2 botella x 1 Lt` vs `Surgizime E2 * 1 litro`.
    *   **Acción:** El importador generará una lista de "Productos Únicos" y tendremos que decidir cuáles se fusionan.
3.  **Identidad de Clientes:**
    *   Faltantes de CUIT: Varios pedidos tienen `NaN` en el campo CUIT.
    *   Nombres informales: `DÚbora Rosario`.

## 3. Plan de Ataque (Estrategia de Ingesta)

### FASE 1: El Extractor
Desarrollaré un script en Python ("The Harvester") que:
1.  Recorra cada celda buscando la palabra clave **"Pedido N°"**.
2.  Al encontrarla, capture el "Bloque" circundante.
3.  Detecte automáticamente si es formato Nuevo o Viejo (mirando si dice "PRECIO DE VENTA" o "Costo Unitario").
4.  Extraiga: Fecha, Cliente, CUIT y Líneas de Ítems.

### FASE 2: Normalización (Tu Tarea)
El script generará dos archivos CSV intermedios:
1.  `clientes_detectados.csv`: Nombre | CUIT | Frecuencia
2.  `productos_detectados.csv`: Nombre Original | Precio Promedio | Frecuencia

**Tu misión será:**
*   En `clientes`: Completar CUITs faltantes y unificar nombres (ej: "Juan" y "Juan Perez" -> Mismo ID).
*   En `productos`: Mapear nombres viejos a nombres nuevos oficiales.

### FASE 3: Inyección
Una vez limpios los CSVs, corremos el inyector final que puebla `produccion.db`.

---
**Pregunta para el Usuario:**
¿Es correcto que en las hojas viejas ("Pedidos") haya múltiples pedidos en la misma fila (hacia la derecha)? El análisis preliminar sugiere que sí (Columna 0 y Columna 8 tienen encabezados "Pedido N°").
