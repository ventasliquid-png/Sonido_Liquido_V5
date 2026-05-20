# INFORME HISTÓRICO — Sesión 812 OF
**Fecha:** 2026-05-20  
**Locación:** OF  
**Sesión:** 812  
**Estado:** NOMINAL GOLD — pendiente commit PIN 1974  
**Agente:** Claude Code Sonnet 4.6  

---

## RESUMEN EJECUTIVO

Sesión de implementación del **Bit 40 DISCRIMINA_IVA** y saneamiento de base de datos. El objetivo fue habilitar la discriminación fiscal entre Responsables Inscriptos (Factura A, precio neto / 1.21) y el resto de clientes (CF / Mono / Exento / Rosa — Factura B, precio final con IVA incluido). Adicionalmente se ejecutó una purga crítica: 5 clientes en `pilot_v5x.db` tenían el Bit 15 (32768) encendido por error de IA anterior que confundió "Nivel 15" (valor nominal del Códice Arlequín) con "Bit 15" (posición del genoma de facturas). La doctrina fue sellada en BIBLIOTECA_NIKE.md. El diff 4 de PedidoCanvas.vue fue evaluado y postergado a sesión 813.

---

## 1. BIT 40 — DISCRIMINA_IVA

### 1.1 Motivación
La lógica de precios en PedidoCanvas tenía una división incondicional `/1.21` para Lista 5 (`isSinIVA`). Esto era incorrecto: un cliente CF de Lista 5 recibe precio **final** (IVA ya incluido), no precio neto. La solución requería un bit canónico en el cliente que indique si discrimina IVA.

### 1.2 Implementación — 3 nodos

#### `backend/clientes/constants.py`
```python
# --- [DISCRIMINACIÓN DE IVA] (Bit 40) ---
# 1 = Responsable Inscripto (discrimina IVA, Factura A, precio final / 1.21)
# 0 = CF / Monotributo / Exento / Rosa (no discrimina, Factura B, precio de lista)
DISCRIMINA_IVA = 1 << 40  # 1099511627776
```

#### `backend/clientes/services/afip_bridge.py`
Auto-encendido en consulta RAR: si `condicion_iva` retornada por AFIP contiene "RESPONSABLE INSCRIPTO" (o el sufijo "(INFERIDO)"), el dict de respuesta incluye `"flags_estado": ClientFlags.DISCRIMINA_IVA`. Permite que el frontend reciba el bit pre-calculado al validar AFIP, sin fricción para el operador.

#### `backend/clientes/service.py` — `_audit_sovereignty` REGLA 3
Toggle permanente en cada `create_cliente` / `update_cliente`:
- `condicion_iva.nombre` contiene "RESPONSABLE INSCRIPTO" → `flags_estado |= DISCRIMINA_IVA`
- CF / Mono / Exento / None → `flags_estado &= ~DISCRIMINA_IVA`

Garantiza que el bit sea siempre coherente con la condición IVA real, sin importar el origen del dato (alta manual, ingesta AFIP, migración).

### 1.3 Impacto en flujo de precios (sesión 813)
La lógica pendiente en `PedidoCanvas.vue selectProduct`:

| Situación | Comportamiento |
|---|---|
| Operación negra (`pedido.flags_estado & 4096`) | Precio neto siempre |
| Operación blanca + RI (`cliente.flags_estado & Bit40`) | Precio neto + IVA discriminado al pie |
| Operación blanca + CF/Mono/Exento/Rosa | Precio final, IVA incluido en el valor |

---

## 2. PURGA — HEREJÍA DEL 15

### 2.1 Diagnóstico
Búsqueda de `32768` en el proyecto (findstr recursivo sobre *.py, *.vue, *.js, *.ts, *.json) reveló:
- **Código fuente**: única ocurrencia legítima en `backend/facturacion/constants.py:17` — `FacturaFlags.PASADO_A_PEDIDO = 1 << 15`
- **DB pilot_v5x.db**: 5 clientes con Bit 15 encendido — ilegítimo

### 2.2 Causa raíz
El Códice Arlequín denomina coloquialmente "Nivel 15" al estado **Blanco Gold Virgen**, que resulta de sumar sus componentes: `EXISTENCE(1) + IS_VIRGIN(2) + GOLD_ARCA(4) + V14_STRUCT(8) = 15`. Una IA anterior interpretó ese nombre como la posición de bit e inyectó `1 << 15 = 32768` en `clientes.flags_estado` en lugar del valor entero `15`.

### 2.3 Corrección
```sql
UPDATE clientes SET flags_estado = flags_estado & ~32768 
WHERE flags_estado & 32768;
-- 5 registros saneados
```
Canario post-purga: NOMINAL GOLD (`flags_estado LAVIMAR = 13`).

### 2.4 Doctrina sellada — BIBLIOTECA_NIKE.md Módulo 2
Nuevo ítem: **"La Herejía del 15"** — prohíbe explícitamente `1<<15` en `clientes.flags_estado`. El Bit 15 (`32768`) es propiedad exclusiva de `FacturaFlags.PASADO_A_PEDIDO`. Para asignar "Nivel 15" a un cliente se usa el entero `15` directamente, o la suma de las constantes base (`EXISTENCE | IS_VIRGIN | GOLD_ARCA | V14_STRUCT`).

---

## 3. ESTADO FINAL

| Ítem | Estado |
|---|---|
| `constants.py` — Bit 40 definido | ✅ |
| `afip_bridge.py` — auto-detección RAR | ✅ |
| `service.py` — Regla 3 _audit_sovereignty | ✅ |
| Purga Bit 15 pilot_v5x.db (5 registros) | ✅ |
| BIBLIOTECA_NIKE.md — Herejía del 15 | ✅ |
| INBOX.md — pendiente sesión 813 | ✅ |
| Diff 4 PedidoCanvas.vue | ⏸ → Sesión 813 |
| Commit D (pendiente PIN 1974) | ⏳ Fase 3 |
| Cherry-pick → P (pendiente) | ⏳ Post-commit |

---

## 4. PENDIENTE → SESIÓN 813

**Diff 4 PedidoCanvas.vue** — `selectProduct` y presentación del campo precio:
- `isClienteRI = !!(BigInt(cliente.flags_estado) & BigInt(1) << BigInt(40))` — computed ya diseñado
- Lógica: negra siempre neto / blanca+RI neto+IVA al pie / blanca+CF precio final
- Presentación: label del campo precio debe cambiar según contexto ("Precio neto" vs "Precio final")

---

*Arquitectura: Claude Sonnet 4.6 — Ejecución: Claude Code Sonnet 4.6 — OF 2026-05-20 — OMEGA Sesión 812*
