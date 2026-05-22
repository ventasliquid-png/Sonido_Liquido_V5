# INFORME HISTÓRICO — Sesión 814 OF
**Fecha:** 2026-05-22  
**Locación:** OF  
**Sesión:** 814  
**Estado:** NOMINAL GOLD — PIN 1974  
**Agente:** Antigravity (Gy)  

---

## RESUMEN EJECUTIVO

Sesión de canonización del **Genoma de Pedidos V6**, migración de base de datos de pedidos históricos (**Operación Mudanza**), blindaje de transiciones transaccionales en el backend y refactorización del frontend (**Diff 4 PedidoCanvas**). El objetivo fue centralizar todo el ciclo de vida e implicaciones del pedido en una única matriz de bits (`flags_estado` de 64 bits) y corregir la visualización y cálculo de impuestos en el frontend bajo la Ley 27.743, asegurando la compatibilidad de precisión numérica en Javascript mediante aserciones `BigInt`.

---

## 1. ARQUITECTURA DE PEDIDOS (GENOMA V6)

### 1.1 Motivación
Previamente, el estado del pedido se gestionaba a través de cadenas de texto (`estado` = "PENDIENTE", "CUMPLIDO", etc.) dispersas en el backend. Para unificar criterios impositivos y de ciclo de vida con la doctrina del genoma de 64 bits aplicada en clientes, se diseñó `PedidoFlags` en la banda 32+ de bits, reservando la banda baja para flags transversales e intocables de base de datos.

### 1.2 Implementación del Códice de Bits (`backend/pedidos/constants.py`)
- **Banda Baja (Bits de Base de Datos y Motor Bipolar):**
  - `EXISTENCE` = Bit 0 (1): Existencia lógica.
  - `PEDIDO_DUPLICATE_CONFIRMED` = Bit 6 (64): Flag de duplicidad.
  - `INGESTA_CON_CORRECCION` = Bit 9 (512): Ingesta con corrección manual.
  - `NO_FISCAL_FORCE` = Bit 12 (4096): Sello negro (Motor Bipolar).
- **Banda Alta (Bits >= 32):**
  - **Estados Excluyentes (`STATE_MASK`):**
    - `ES_PRESUPUESTO` = Bit 32 (1<<32): Cotización/borrador formal sin color impositivo.
    - `ES_FIRME` = Bit 33 (1<<33): Pedido en firme (operativo blanco o negro).
    - `ES_CUMPLIDO` = Bit 34 (1<<34): Cerrado por entrega.
    - `ES_ANULADO` = Bit 35 (1<<35): Baja lógica del documento.
  - **Flags Ortogonales (Auditoría Forense):**
    - `RESERVA_STOCK` = Bit 36 (1<<36)
    - `TUVO_CIRCUITO` = Bit 37 (1<<37)
    - `ORIGEN_FACTURA` = Bit 38 (1<<38)
    - `ORIGEN_RETROACTIVO` = Bit 39 (1<<39)
    - `CAMBIO_A_NEGRO` = Bit 41 (1<<41)
    - `CAMBIO_A_BLANCO` = Bit 42 (1<<42)

---

## 2. OPERACIÓN MUDANZA & RUTAS TRANSACCIONALES

### 2.1 Operación Mudanza (`pilot_v5x.db`)
- Script de migración masiva ejecutado para transformar la columna de estado textual a la estructura unificada de bits en la base de datos física.
- 31 pedidos históricos migrados nominalmente preservando toda la información de negocio anterior.
- Se agregó e inicializó el campo físico `fecha_vencimiento` en el esquema de pedidos.

### 2.2 Blindaje en Backend (`backend/pedidos/router.py`)
- **Paso A (Escrituras de Estado):** Las mutaciones del ciclo de vida limpian preventivamente la máscara de estados excluyentes antes de asignar el nuevo bit:
  `pedido.flags_estado = (pedido.flags_estado & ~STATE_MASK.value) | state_bit`
  Esto prohíbe inconsistencias de estado duales en la base de datos.
- **Paso B (Lecturas Legacy):** Reemplazo sistemático de las condicionales basadas en `pedido.estado` por evaluaciones de bits sobre `flags_estado`.

---

## 3. FRONTEND: DIFF 4 PEDIDOCANVAS.VUE

### 3.1 Soporte de Precisión de 64 bits (BigInt)
Javascript limita la precisión en operadores bitwise a enteros con signo de 32 bits. Para procesar bits en la banda 32+, se implementó aserción `BigInt` y sufijo literal `n`:
```javascript
const isClienteRI = computed(() => {
  const flags = BigInt(cliente.value?.flags_estado || 0);
  return !!(flags & (1n << 40n)); // Bit 40 del cliente
});
```

### 3.2 Lógica selectProduct (Precios LISTA_5)
Para evitar rebajas incorrectas a clientes finales en Lista 5 (donde el precio de lista ya incluye IVA), se refactorizó la lógica en `selectProduct`. El recálculo del neto (dividir por 1.21) se restringe únicamente a Responsables Inscriptos:
```javascript
if (res.origen === 'LISTA_5' && isClienteRI.value) {
    precioFinal = precioFinal / 1.21;
}
```

### 3.3 Desglose Fiscal en Pie de Pedido (Ley 27.743)
Se removió la propiedad computada `isExento` unificando las aserciones en el Motor Bipolar (`isSinIVA` basado en Bit 12 del pedido). La UI desglosa los impuestos según tres perfiles:
1.  **Responsable Inscripto (Operación Blanca):** Muestra "Subtotal", "IVA 21.00%" (discriminado) y "Total".
2.  **Consumidor Final / Monotributista (Operación Blanca):** Muestra "Total Neto" e "IVA" con la leyenda fiscal de advertencia sobre el impuesto contenido:
    *Ley 27.743: El IVA de 21% equivalente a $X.XX se encuentra incluido en el precio.*
3.  **Circuito Negro / Exento:** Muestra "Subtotal", "IVA 0.00%" y "Total" plano.

---

## 4. CERTIFICACIÓN DE INTEGRIDAD

- **Ejecución del Canario (`scripts/canario_v2.py`):**
  - Purgado de logs temporales SQLite (WAL/journal checkpoints).
  - Integridad verificada nominalmente en cliente maestro LAVIMAR (`flags_estado = 13`).
  - **Certificación:** NOMINAL GOLD (`CIELO DESPEJADO`).

---

## 5. ESTADO DE TAREAS Y MIGRACIONES

| Módulo / Cambio | Estado |
|---|---|
| `constants.py` — PedidoFlags & STATE_MASK | ✅ |
| `router.py` — Paso A (Escrituras con STATE_MASK) | ✅ |
| `router.py` — Paso B (Lecturas bitwise de estado) | ✅ |
| Migración pilot_v5x.db (31 pedidos mudados) | ✅ |
| `PedidoCanvas.vue` — BigInt en flags de 64-bit | ✅ |
| `PedidoCanvas.vue` — Motor Bipolar & Lógica LISTA_5 | ✅ |
| `PedidoCanvas.vue` — Desglose Ley 27.743 | ✅ |
| `scripts/canario_v2.py` — Verificación de Integridad | ✅ |
| Commits en main (`5e1e2445` final) | ✅ |

---

*Arquitectura: Antigravity (Gy) — Ejecución: Antigravity (Gy) — OF 2026-05-22 — OMEGA Sesión 814*
