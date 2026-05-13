# Informe Histórico — Sesión 806
**Fecha:** 2026-05-13
**Título:** Arlequín V2 — Inferencia Rosa + GENOMA_UNIVERSAL + fix NO_FISCAL_FORCE
**Estado:** NOMINAL GOLD — PIN 1974
**Hash D:** abd34332 | **Hash P:** 2d7c5c2

## Resumen Ejecutivo

La sesión 806 cerró tres frentes críticos que venían acumulándose desde las sesiones 798-805:

### 1. GENOMA_UNIVERSAL sellado
`docs/GENOMA_UNIVERSAL.md` es el primer documento canónico unificado del ecosistema V5.
Mapea los bits de flags_estado para todas las entidades (Clientes, Productos, Pedidos, Facturas RAW/PRC/Madre, Remitos).
Resuelve por escrito tres contradicciones forenses: la herejía Bit10, la semántica de Virginidad y la arquitectura de Esclusa de Verdad en ingesta.

### 2. Herejía NO_FISCAL_FORCE purgada
`NO_FISCAL_FORCE` vivía en Bit10 (1024) colisionando con `V15_STRUCT` — marca de agua arquitectónica intocable.
Corregido a Bit12 (4096) en:
- `backend/pedidos/constants.py`
- `frontend/src/views/Pedidos/PedidoList.vue` (6 referencias hardcodeadas)
- `backend/pedidos/router.py` (comentario docstring)

### 3. Doctrina Arlequín V2 implementada
Sistema completo de clasificación de clientes por bits:
- **Amarillo** (sin Bit2 ni Bit4): sin GOLD_ARCA, sin OPERATOR_OK
- **Rosa** (Bit4 = OPERATOR_OK = 16): inferido automáticamente por `_audit_sovereignty()` si tiene segmento y carece de CUIT real
- **Blanco/Gold** (Bit2 = GOLD_ARCA = 4): datos homologados ARCA
- **Consumidor Final**: CUIT 00000000000 forzado GOLD_ARCA, nunca cae en inferencia Rosa
- **MOSTRADOR/GENÉRICO**: CUIT 00000000000 declarado exclusivo — bloqueo de duplicados en create y update

### 4. Sincronización D→P
Cherry-pick de 4 commits D→P sin conflictos. Push a ambos remotos confirmado.
`PROTOCOLO_EMERGENCIA_MT.md` sellado — doctrina de flujo canónico D→P→MT para incidentes de producción.

## Archivos modificados (sesión 806)
```
docs/GENOMA_UNIVERSAL.md                        (nuevo)
docs/protocolos/PROTOCOLO_EMERGENCIA_MT.md      (nuevo)
docs/roadmap/MIRROR_PEDIDOS_DRIVE.md            (nuevo)
backend/pedidos/constants.py                    (NO_FISCAL_FORCE Bit12)
backend/pedidos/router.py                       (comentario 4096)
backend/clientes/constants.py                   (OPERATOR_OK=16)
backend/clientes/service.py                     (Arlequín V2 + Reglas 1 y 2)
frontend/src/views/Pedidos/PedidoList.vue       (6x 1024→4096)
frontend/src/views/Ventas/PedidoCanvas.vue      (clientValidation bits)
frontend/src/composables/useAuditSemaphore.js   (evaluateCliente bits)
```

## Deuda técnica registrada (7 ítems)
1. Botón Completar en badge naranja PedidoCanvas — no visible (D/P)
2. Modal confirmación Rosa — pendiente de implementar (D/P)
3. MT — git pull + segmento Pao Tandil + rebuild frontend (MT)
4. Script limpieza verdura MT — CUIT cero duplicados, MYM Odontológicos (MT)
5. Encoding corrupto INICIO_TOMY.bat — charset á→├í (MT)
6. Task Scheduler MT — verificar reboot (MT)
7. PedidoCanvas — badge/avatar color Arlequín V2 según genoma del cliente (D/P)

---
*Documento generado sesión 806 — Carlos + Claude Sonnet 4.6 + Nike Arq 5.5*
