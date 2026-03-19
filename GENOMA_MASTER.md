# 🧬 GENOMA MASTER - DOCTRINA DE UNIFICACIÓN (V14)
> **STATUS:** CRÍTICO // VIGENTE DESDE 13/03/2026
> **AUTORIZACIÓN:** PIN 1974

## 1. Fundamentos de Identidad
El sistema utiliza una lógica de **Suma de Potencias de 2** para definir jerarquías y estados. Queda prohibido el uso de bits arbitrarios sin sustento matemático en la suma.

### A. Genoma de Clientes (Lógica 13/15)
Se define en los 4 bits bajos del campo `flags_estado`.

| Bit | Valor | Etiqueta | Descripción |
|---|---|---|---|
| 0 | 1 | ACTIVO | Registro funcional en el sistema. |
| 1 | 2 | VIRGINIDAD | 1 = Virgen (Sin movimientos) / 0 = Operado. |
| 2 | 4 | ORO ARCA | Homologado por Satélite RAR (AFIP). |
| 3 | 8 | ESTRUCTURA V14 | Compatible con Protocolo Apolo (Bóveda N:M). |

**Niveles Maestros:**
- **15 (1+2+4+8):** Cliente Nuevo/Virgen (Validado).
- **13 (1+4+8):** Cliente con Historia (Se apaga el 2 tras la primera operación).

### B. Bóveda de Domicilios (Vanguard Vault)
Estados de independencia geográfica definidos por la suma:

| Bit | Valor | Etiqueta | Descripción |
|---|---|---|---|
| 0 | 1 | ACTIVO | Indispensable para existir. |
| 1 | 2 | CONFLICTO | Detectado por el Sereno / Cuarentena. |
| 2 | 4 | ORO FISCAL | Fuente ARCA/Validado. |
| 3 | 8 | ORO CURADO | Validado manualmente por el Operador. |
| 4 | 16 | LOGÍSTICA | Apto para emisión de Remitos. |

**Estados de Operación:**
- **21 (16+4+1):** Verde ARCA (Automático).
- **25 (16+8+1):** Verde Manual (Curado).
- **29 (16+8+4+1):** Oro Total (Máxima confianza).
- **23 (16+4+2+1):** Amarillo (Conflicto ARCA / Requiere atención).

### C. Genoma de Sistema (64 Bits)
Control jerárquico del Byte 0:
- Bit 0 (1): **TÉRMICA (ROJO)** - Bloqueo total. Solo lectura. Requiere PIN 1974.
- Bit 1 (2): **ADVERTENCIA (AMARILLO)** - Discrepancias de datos (Sereno).
- Bit 2 (4): **AISLAMIENTO (NARANJA)** - Sin conexión ARCA. Solo local.

---

## 2. Auditoría de Capas Superiores (Paz Binaria V15.1)
- **Bit 19 (524288):** POWER_PINK. Soberanía Informal Éxito (Niveles 9/11).
- **Bit 20 (1.048.576):** ARCA_OK. Soberanía Formal Auditada (Niveles 13/15).

---
**NOTA:** El Amarillo es el estado base por defecto si no hay medallas de soberanía (Bits 19/20).

---
*Firma: Antigravity / Gy V14 - Bajo supervisión de Carlos.*
