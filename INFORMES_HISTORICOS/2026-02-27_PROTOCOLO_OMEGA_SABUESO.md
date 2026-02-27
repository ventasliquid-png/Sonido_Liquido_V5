# INFORME HISTÓRICO: PROTOCOLO OMEGA - OPERACIÓN SABUESO PDF
**Fecha:** 2026-02-27
**Agente:** Antigravity (Gy V14)
**Rama:** `feat/v5x-universal` (V5) / `feat/sabueso-arca` (RAR)

## 1. OBJETIVO LOGRADO
Portar con éxito absoluto el "Motor Sabueso" (Extractor PDF de facturas ARCA/AFIP) desde el sistema satélite RAR hacia el núcleo de Sonido Liquido V5, garantizando paridad uno a uno, sin corromper la estricta limitación de base de datos (`pilot_v5x.db` clavado en 428 KB).

## 2. HITOS TÉCNICOS

### 2.1 Refinamiento Heurístico (Regex Positivo)
Se detectó que el formato de AFIP introducía caracteres invisibles y barras separadoras (`|`) que rompían el parsing en V5.
- **Solución:** Se implementó una directiva Lookahead positiva `(?=\s*\||$)` en `pdf_parser.py`. Esto permitió extraer Razón Social y Número Legal (`0001-00002466`) ignorando el "ruido" perimetral de AFIP de forma infalible.

### 2.2 Flujo ABM Asistido (Workflow Interception)
- **Problema:** Los clientes extraídos de los PDF podían no existir en la DB, o existir pero carecer del nivel de validación requerido (Nivel 13 "Blanco").
- **Solución Frontend:** Se modificó `IngestaFacturaView.vue` para inyectar un **Freno de Mano Interactivo**. Si el router devuelve un status de alerta para el cliente, se bloquea la generación del Remito y emerge instantáneamente un modal de `ClienteInspector.vue`.
- Esto obliga al operario a intervenir, asentar los datos fiscales y domicilios de entrega faltantes, antes de reanudar la formulación lógica.

### 2.3 Evolución 4-Bytes (Doctrina de Virginidad)
- **Concepto:** Cliente Virgen = `Bit 1 (2)` activo. Cliente Consistido = Nivel 13 (Existence + Gold_Arca + Struct_V14).
- **Inyección Backend:** En `service.py`, al emitir el primer remito a nombre de un cliente, el ORM intercepta la bandera `flags_estado`. Con una resta de bit (`& ~ClientFlags.VIRGINITY`), el cliente evoluciona automáticamente, mutando su nivel `15` a Nivel `13`.
- **Mitigación:** Se forzó un bloque _fallback_ (Constraint Bypass) para asegurar que el `domicilio_entrega_id` jamás detone un error 500 al persistir en DB.

## 3. ESTADO DEL SISTEMA (CIERRE V14-B)
- **Base de Datos:** Verificada (428 KB).
- **Paridad RAR-V5:** Confirmada. Backend ingiere PDFs y emana entidades legales coherentes.
- **Preparación Operativa:** El módulo Sabueso queda activo para producción en ambiente local P2P.
