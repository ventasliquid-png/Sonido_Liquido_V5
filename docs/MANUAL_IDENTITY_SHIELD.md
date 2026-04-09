# Manual Técnico: Protocolo Identity Shield (Nike)

## Introducción
El Protocolo Identity Shield (basado en la doctrina "Bag of Words") es un sistema de prevención nuclear de duplicados diseñado para asegurar la integridad de la base de datos de clientes en entornos V5x.

## Motor de Normalización (`normalize_name`)
El núcleo del sistema reside en la creación de una **Clave Canónica** única para cada razón social.

### Proceso de Transformación:
1.  **Limpieza Unicode**: Eliminación de acentos y caracteres especiales (NFKD).
2.  **Unificación de Siglas**: Remoción de puntos (ej: `S.R.L.` -> `SRL`).
3.  **Tokenización**: División de la cadena en palabras (tokens) alfanuméricos.
4.  **Filtrado de Ruido**: Eliminación de conectores o siglas de menos de 2 caracteres.
5.  **Ordenamiento Alfabético**: El orden de las palabras no altera la clave (ej: `DISTRIBUIDORA JUAN` == `JUAN DISTRIBUIDORA`).
6.  **Sellado**: Unión de tokens en una cadena continua en mayúsculas.

## Implementación en Backend
- **Columna**: `razon_social_canon` (String, Indexada).
- **Validación en Creación**: El sistema realiza un `Strict Check` contra la clave canónica antes de insertar. Si la clave existe, el servidor retorna un `HTTP 400 - BLOQUEO NUCLEAR`.

## Implementación en Frontend
- **Sensor Reactivo**: Ubicado en `ClientCanvas.vue`.
- **Modo Asíncrono**: Utiliza `debounce` (500ms) para evitar saturación del backend.
- **Alertas Visuales**:
    - **Roja (Riesgo Crítico)**: Coincidencia del 100% (Canon). Impide el guardado.
    - **Naranja (Peligro)**: Coincidencia por similitud difusa (Fuzzy Match >= 85%).

## Mantenimiento
Para re-generar las claves canónicas en masa, se debe utilizar el script `scripts/reparacion/repair_canon_identities.py`.
