# 🐾 MACHE MAÑANA: EL SABUESO vs GELATO (PIN 1974)

### 1. El Estado Actual (V4 - Estrategia de Anclaje)
El Sabueso ahora no busca por toda la línea, sino que busca "Anclas" (unidades, un., kg).
- **Izquierda**: Toma el número anterior como Cantidad.
- **Derecha**: Toma el número siguiente como Precio Unitario.
- **Prioridad**: Si hay más de un ancla, elige la que esté más a la derecha (teoría: los datos reales de AFIP están al final).

### 2. ¿Por qué falló hoy? (Hipótesis)
En la factura de Gelato, el "100 UN" sigue ganando.
- **Opción A**: El servidor de Tomy no reinició y sigue corriendo el Sabueso viejo (V3).
- **Opción B**: Hay espacios múltiples o caracteres invisibles entre el número y la unidad.
- **Opción C**: El texto crudo del PDF viene con un orden distinto al visual.

### 3. Plan de Acción Inmediato
1. Reiniciar el servidor de Tomy (Uvicorn).
2. Tirar la factura 2529.
3. Si falla, abrir `backend/remitos/pdf_parser.py` y activar los `print(words)` para ver el "mapa de palabras" real.
