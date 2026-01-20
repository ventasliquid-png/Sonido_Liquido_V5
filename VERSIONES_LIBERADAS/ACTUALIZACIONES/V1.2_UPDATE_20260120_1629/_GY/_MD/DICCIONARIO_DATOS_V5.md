# 🗺️ EL GRAN MAPA: DICCIONARIO DE DATOS V5 (Sonido Líquido)

**Estado del Documento:** GENERADO AUTOMÁTICAMENTE
**Fecha:** 2026-01-15
**Versión:** 1.0 "Steel Core"

---

## 🔍 DETECCIÓN DE AMENAZAS (IOWA/VAGÓN FANTASMA)

**¿Código Activo conectando a G:/ o Google Drive?**
> **NO.** 
> Análisis de `backend/main.py` y `backend/core/database.py` confirma que **IOWA está DESACTIVADO** (`ENABLE_AI="False"`, Credenciales vacías). La base de datos opera en modo LOCAL (`sqlite:///pilot.db`) o PostgreSQL directo, sin montajes de disco en red detectados en código.

---

## 🏗️ ESTRUCTURA DE LA BASE DE DATOS

### 📦 Módulo Clientes
**Tabla: `clientes` (La Cuenta)**
- `id` (GUID, PK)
- `razon_social` (String)
- `cuit` (String, Index)
- `condicion_iva_id` (FK -> `condiciones_iva`)
- `lista_precios_id` (FK -> `listas_precios`)
- `segmento_id` (FK -> `segmentos`)
- `vendedor_id` (FK -> `usuarios`)
- `saldo_actual` (Numeric)
- `historial_cache` (JSON) - *Vector de Historial V5.3*
- `activo` (Bool)

**Tabla: `domicilios` (Logística)**
- `id` (GUID, PK)
- `cliente_id` (FK -> `clientes`)
- `alias` (String)
- `calle`, `numero`, `localidad` (String)
- `provincia_id` (FK -> `provincias`)
- `transporte_id` (FK -> `empresas_transporte`)
- `es_fiscal`, `es_entrega` (Bool)
- `metodo_entrega` (String) - *Estrategia Logística*

### 🛒 Módulo Productos
**Tabla: `productos` (El Ítem)**
- `id` (Int, PK)
- `sku` (Int, Unique)
- `nombre` (String)
- `rubro_id` (FK -> `rubros`)
- `proveedor_habitual_id` (FK -> `proveedores`)
- `tipo_producto` (String: VENTA, INSUMO...)
- `unidad_stock_id`, `unidad_compra_id` (FK -> `unidades`)
- `factor_compra`, `venta_minima` (Numeric)
- `activo` (Bool)

**Tabla: `productos_costos` (Doctrina Roca Sólida)**
- `id` (Int, PK)
- `producto_id` (FK -> `productos`)
- `precio_roca` (Numeric) - *Precio Base Real*
- `costo_reposicion` (Numeric)
- `rentabilidad_target` (Numeric)

**Tabla: `rubros` (Categorías)**
- `id` (Int, PK)
- `codigo`, `nombre` (String)
- `margen_default` (Numeric)

### 📦 Módulo Pedidos
**Tabla: `pedidos` (Transacción)**
- `id` (Int, PK)
- `fecha` (DateTime)
- `cliente_id` (FK -> `clientes`)
- `total` (Float)
- `estado` (String: PENDIENTE, CUMPLIDO...)
- `oc` (String)
- `fecha_compromiso` (DateTime)

**Tabla: `pedidos_items` (Detalle)**
- `id` (Int, PK)
- `pedido_id` (FK -> `pedidos`)
- `producto_id` (FK -> `productos`)
- `cantidad` (Float)
- `precio_unitario` (Float)
- `subtotal` (Float)

### 🚚 Módulo Logística (Transportes)
✅ **CONFIRMADO: EXISTENTE**

**Tabla: `empresas_transporte`**
- `id` (GUID, PK)
- `nombre` (String)
- `web_tracking` (String)
- `servicio_retiro_domicilio` (Bool)

**Tabla: `nodos_transporte` (Sucursales/Depósitos)**
- `id` (GUID, PK)
- `empresa_id` (FK -> `empresas_transporte`)
- `nombre_nodo` (String)
- `es_punto_despacho`, `es_punto_retiro` (Bool)

**Tabla: `depositos` (Almacenes Internos)**
- `id` (Int, PK)
- `nombre`, `tipo` (String)

### 📒 Módulo Agenda (Contactos)
✅ **CONFIRMADO: EXISTENTE (CRM Relacional)**

**Tabla: `personas` (Individuos)**
- `id` (GUID, PK)
- `nombre_completo` (String)
- `celular_personal`, `email_personal` (String)

**Tabla: `vinculos_comerciales` (Roles en Clientes)**
- `id` (GUID, PK)
- `cliente_id` (FK -> `clientes`)
- `persona_id` (FK -> `personas`)
- `tipo_contacto_id` (FK -> `tipos_contacto`) - *Ej: COMPRAS, PAGOS*
- `email_laboral` (String)

### 🏭 Módulo Proveedores
✅ **CONFIRMADO: EXISTENTE**

**Tabla: `proveedores`**
- `id` (GUID, PK)
- `razon_social` (String)
- `cuit` (String)
- `email`, `telefono` (String)

### 🎛️ Módulo Maestros & Config
**Tablas Auxiliares:**
- `provincias` (`id`, `nombre`)
- `condiciones_iva` (`id`, `nombre`)
- `listas_precios` (`id`, `nombre`, `coeficiente`)
- `segmentos` (`id`, `nombre`)
- `vendedores` (`id`, `nombre`, `comision_porcentaje`)
- `tipos_contacto` (`id`, `nombre`)
- `tasas_iva` (`id`, `nombre`, `valor`)
- `unidades` (`id`, `codigo`, `nombre`)

### 🔐 Auth
- `usuarios` (`id`, `username`, `email`, `rol_id`)
- `roles` (`id`, `name`)

---
**BÚSQUEDA ESPECÍFICA:**
1.  **Transportes**: ✅ SI (`logistica.models`). Completo con Nodos.
2.  **Contactos**: ✅ SI (`agenda.models`). Modelo relacional Persona-Vínculo-Cliente implementado.
3.  **Proveedores**: ✅ SI (`proveedores.models`).
