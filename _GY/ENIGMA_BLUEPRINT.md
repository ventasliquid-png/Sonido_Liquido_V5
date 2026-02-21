# 🧬 ENIGMA BLUEPRINT: ESTRUCTURA PRIMARIA DE IDENTIDAD (V14)

> **ESTADO:** MASTER / INMUTABLE
> **AUTORIDAD:** ALMIRANTE (GY)
> **FECHA:** 2026-02-20
> **MISIÓN:** Estabilización de Stage 5 y definición del Códice de Identidad.

---

## 💾 1. LA CINTA PERFORADA (Bitmask)
Cada cliente se define por la suma de sus bits de estado. El valor final del `Flag` determina su color y su jerarquía comercial.

| Bit | Valor ($2^n$) | Nombre Técnico | Función |
| :--- | :--- | :--- | :--- |
| 0 | 1 | **EXISTENCE** | El registro existe físicamente en la DB. |
| 1 | 2 | **VIRGINITY** | 1: Virgen (Sin movimientos) / 0: Activo (Tiene remitos/facturas). |
| 2 | 4 | **GOLD_ARCA** | El dato fue homologado por el satélite RAR (ARCA). |
| 3 | 8 | **V14_STRUCT** | El registro cumple con la arquitectura de 32 bits. |
| 4 | 16 | **OPERATOR_OK** | Sello Rosa: Validado manualmente por el operador. |
| 5 | 32 | **MULTI_CUIT** | Sello Azul: CUIT compartido (UBA, Sedes, etc.). |

---

## 🎨 2. EL CÓDICE DE COLORES (Jerarquía Visual)
El Frontend debe interpretar los `Flags` según esta lógica de dominancia (Bitwise Logic):

### 🟡 AMARILLO (Aspirante/Cantera)
*   **Flag = 9** (Bits $1 + 8$)
*   **Estado:** Registro base, sin validación externa.

### ⚪ BLANCO GOLD (Homologado ARCA)
*   **Flag = 15** (Bits $1 + 2 + 4 + 8$) $\rightarrow$ **Virgen Gold**.
*   **Flag = 13** (Bits $1 + 4 + 8$) $\rightarrow$ **Activo Gold**.
*   **Insignia:** Sello "Gold" visible.

### 🌸 ROSA (Validado por Operador)
*   **Flag = 25** (Bits $1 + 8 + 16$)
*   **Lógica:** ARCA falló o no aplica, pero el operador dio el "Sí" manual.

### 🔵 AZUL (Multicliente)
*   **Flag = 47** (Bits $15 + 32$)
*   **Lógica:** CUIT duplicado pero validado como unidad de negocio distinta.

---

## 📥 3. IMPLEMENTACIÓN Y AUDITORÍA
1. **Transición 9 -> 15:** Ocurre solo tras handshake exitoso con el satélite RAR.
2. **Transición 15 -> 13:** Ocurre automáticamente en la primera emisión de comprobante oficial.
3. **Persistencia:** El campo `flags_estado` debe coincidir con el estado visual reportado por el sistema.
