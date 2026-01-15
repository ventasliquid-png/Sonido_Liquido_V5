# 🕵️ REPORTE DE INTELIGENCIA: ESTRUCTURA Y DATOS DE COMBATE

**Estado:** REALIDAD DEL TERRENO (Auditado en `pilot.db`)
**Fecha:** 2026-01-15 11:30

---

## 1. MAPEO DE ESTRUCTURA (Schema Real)

### 🏗️ CLIENTES (`backend/clientes/models.py`)
- **Tabla:** `clientes`
- **Campos Clave Confirmados:**
    - `segmento_id` (GUID) -> FK a tabla `segmentos`.
    - `condicion_iva_id` (GUID) -> FK a tabla `condiciones_iva`.
    - `estrategia_precio` (String) -> Campo de texto libre (Ej: "MAYORISTA_FISCAL").
    - `lista_precios_id` (GUID) -> FK a `listas_precios`.

### 🛒 PRODUCTOS (`backend/productos/models.py`)
- **Tabla:** `productos` + `productos_costos`
- **Campos Clave Confirmados:**
    - `costo_reposicion` (Numeric 12,4): ✅ Definido así en código, aunque SQLite almacena como REAL/FLOAT.
    - `rentabilidad_target` (Numeric 6,2): Campo clave para fórmula.
    - `precio_roca` (Numeric 12,2): Campo para precio base.

### 🧬 SEGMENTOS (`backend/maestros/models.py`)
- **Tabla:** `segmentos`
- **Campos Activos:** `id` (GUID), `nombre` (String), `descripcion`.
- **CRÍTICO:** ❌ El campo `nivel` **NO EXISTE** en la base de datos actual. Requiere migración urgente para soportar lógica 1-7.

---

## 2. ESTADO DE LOS DATOS (Consistencia)

### 👥 Clientes (Saneamiento: ALTO)
- **Segmentación:** ✅ 100% de cobertura. No hay clientes con `segmento_id` Nulo.
- **Fiscal:** ✅ 100% de cobertura. No hay `condicion_iva_id` Nulo.
- **Ejemplo Sano:** "Clinica Santa Isabel" (CUIT 30-5000...) tiene Segmento y Estrategia asignados.

### 📦 Productos (Saneamiento: BAJO - ALERTA ROJA)
- **Costos Vacíos:** ⚠️ Alta prevalencia de productos con `costo_reposicion = 0`.
    - *Ejemplo:* "Barbijo Recto con elástico" -> Costo 0, Roca 0.
- **Precios Calculados:** La mayoría en 0.
- **Excepción:** "Barbijos rectos con tiras" tiene Costo $23.00 y Rentabilidad 80%, pero Precio Roca $0.00 (Posiblemente cálculo viejo o no ejecutado).

---

## 🎯 CONCLUSIÓN Y ACCIONES

1.  **Migración de Segmentos:** Es imperativo correr el `ALTER TABLE` para agregar `nivel` a `segmentos` y asignar manualmente los valores 1-7 (General=1, Distribuidor=3, etc.).
2.  **Carga de Costos:** El motor de precios V5 funcionará matemáticamente, pero devolverá **$0.00** para casi todos los productos hasta que se carguen costos reales.
3.  **Ejecución de Batch:** Se requiere un script que recorra todos los productos y recalcule `precio_roca` una vez que los costos existan.
