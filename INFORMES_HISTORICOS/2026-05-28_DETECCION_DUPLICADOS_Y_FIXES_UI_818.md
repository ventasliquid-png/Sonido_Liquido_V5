# INFORME HISTÓRICO SESIÓN 818 OF: Detección Temprana Duplicados + Fixes UI

**Fecha:** 2026-05-28  
**Locación:** OF  
**PIN:** 1974  
**Hash D:** f7a48c08  
**Estado:** NOMINAL GOLD  

---

## 1. Misión
Implementar la detección temprana de facturas duplicadas durante la ingesta de PDFs raw para evitar colisiones de datos. Asegurar que al re-ingestar un duplicado se conserve la trazabilidad histórica de auditoría marcando registros viejos como "ANULADA" y se prevenga la creación de registros huérfanos. Corregir bugs activos en la interfaz de usuario: error de lectura sobre CUIT nulo en clientes y redirecciones no deseadas en Nuevo Pedido Táctico.

---

## 2. Trabajo Realizado

### A. Detección Temprana de Duplicados & Ciclo de Anulación y Reingesta
- **Detección Precoz:** Se modificó `POST /ingesta/raw` para verificar si existe una factura con la clave única (`tipo_comprobante`, `punto_venta`, `numero_comprobante`). Si hay coincidencia, se incluye la información del duplicado en la respuesta JSON.
- **Frontend Comparador:** En `IngestaFacturaView.vue`, se agregó un panel de comparación de datos cuando se detecta un duplicado.
  - Si el remito asociado se encuentra en estado **BORRADOR**, se habilita el botón "Anular procesado y re-ingestar con este PDF" solicitando la validación del PIN Maestro "1974".
  - Si el remito ya fue despachado (estado distinto de BORRADOR), se bloquea la re-ingesta y se provee un acceso directo para visualizar el remito actual.
- **Endpoint de Re-ingesta (`POST /ingesta/raw/{raw_id}/anular-y-reingestar`):**
  - Valida el PIN de seguridad "1974".
  - Enciende el Bit 11 (`DUPLICATE` = 2048) en el RAW viejo.
  - Cambia el estado de la factura procesada vieja a `"ANULADA"` para conservar el registro de auditoría.
  - Si el pedido asociado nació de la factura (Bit 38 `ORIGEN_FACTURA` encendido), se anula actualizando su estado a `"ANULADO"` y aplicando `ES_ANULADO` en sus flags.
  - Elimina físicamente el remito viejo en BORRADOR y la factura espejo vieja.
  - Restablece el nuevo RAW a estado `"RECIBIDO"` y limpia su bit de duplicado para que el flujo de procesamiento continúe con los nuevos datos.

### B. Cascada de Borrado en Remito & Integridad
- Se analizó la cascada de borrado en el modelo `Remito`. La relación `items` ya contaba con `cascade="all, delete-orphan"`.
- Se detectó que la relación intermedia `vinculos_facturas` (hacia `FacturaRemito`) no poseía cascada, lo cual generaba registros huérfanos al eliminar remitos puente. Se añadió `cascade="all, delete-orphan"` a dicha relación en `backend/remitos/models.py`.

### C. Fix A — HaweView null.includes()
- **Causa raíz:** En `HaweView.vue:771`, el método computed de filtrado llamaba `cliente.cuit.includes(query)`. Al existir registros en la base de datos sin CUIT (valor `null`), el método arrojaba un error crítico de javascript.
- **Resolución:** Se inyectó un guard de fallback de string vacío: `(cliente.cuit || '').includes(query)`.

### D. Fix B — Redirección Nuevo Pedido Táctico
- **Causa raíz:** Al salir del canvas de Ingesta sin procesar o cancelando el modal, los datos quedaban en el store Pinia (`pedidosStore.ingestaData`). Al navegar posteriormente a "Nuevo Pedido (Táctico)", el canvas detectaba `ingestaData` y redirigía al usuario automáticamente de vuelta a Ingesta de Factura.
- **Resolución:** Se añadió `pedidosStore.clearIngestaData()` en el gancho `onUnmounted` de `PedidoCanvas.vue`, garantizando que el store se limpie al salir de la pantalla de Pedido.

---

## 3. Estado del Ecosistema
- **Canario:** NOMINAL GOLD (flags=13).
- **WAL Checkpoint:** Ejecutado exitosamente en `pilot_v5x.db`.
- **Silo de Respaldo:** Base de datos lista para copiar en `Q:\Mi unidad\V5_Silo_Claude\`.
