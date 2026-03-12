# 🎨 INFORME TÉCNICO: SISTEMA DE COLORES E IDENTIDAD DE CLIENTES (V14)

**Para:** IA Nike (Arquitectura)
**De:** Antigravity (Operaciones)
**Fecha:** 2026-02-19

---

## 1. EL ESPECTRO DE IDENTIDAD (The Color Logic)
El sistema visual de V5 clasifica a los clientes en 4 estados cuánticos basándose en la calidad de sus datos fiscales (`cuit` y `estado_arca`). Esta lógica reside en el frontend (`HaweView.vue`), actuando como un semáforo interactivo.

### 🌸 ROSA (PINK) - "El Informal / Consumidor Final"
*   **Condición:** 
    *   CUIT Vacío/Nulo (`!cuit`).
    *   CUIT Genérico de AFIP (`00000000000`, `11111111119`, etc.).
    *   CUIT Incompleto (< 5 dígitos).
*   **Significado:** Cliente de mostrador, sin pretensiones fiscales. Operativamente válido, fiscalmente neutro.
*   **Visual:** Texto Fuchsia 400 + Glow Rosa.

### ❄️ BLANCO (WHITE) - "El Dorado / Validado"
*   **Condición:** 
    *   Campo `estado_arca === 'VALIDADO'`.
*   **Significado:** La "Cantera de Oro". Datos consistidos contra el padrón oficial de ARCA. Es el estado ideal y objetivo de todo registro.
*   **Visual:** Texto Blanco Puro.

### 🌊 AZUL (BLUE) - "El Colectivo / Caso UBA"
*   **Condición:** 
    *   CUIT válido (11 dígitos).
    *   **Duplicado detectado:** El mismo CUIT aparece >1 vez en la base activa.
*   **Significado:** Entidades grandes (Universidades, Ministerios) o Cadenas donde la logística (Sucursales) requiere múltiples fichas separadas bajo una misma identidad fiscal.
*   **Visual:** Texto Cyan 300 + Glow Azul.

### ⚠️ AMARILLO (YELLOW) - "El Pendiente / Inconsistente"
*   **Condición:** 
    *   Tiene CUIT válido (formato correcto).
    *   **NO** está marcado como 'VALIDADO' ni es duplicado (Azul).
*   **Significado:** Cliente cargado manualmente o migrado de legado que aun no ha pasado por el "Puente RAR" de validación. Requiere atención (clic en la lupa).
*   **Visual:** Texto Amarillo 400.

---

## 2. IMPLICANCIA PARA "MINER PDF"
Para que los clientes extraídos de los PDFs (Facturas Oficiales de ARCA) ingresen al sistema con la jerarquía correcta, el script `miner.py` debe realizar dos acciones simultáneas en el `INSERT`:

1.  **Setear Flags:** `flags_estado = 15` (Activo | Virgen | Fiscal | Validado).
2.  **Setear Estado:** `estado_arca = 'VALIDADO'`.

**Resultado Esperado:** Al finalizar la importación, los nuevos clientes aparecerán inmediatamente en **BLANCO (White)**, confirmando su calidad "Gold" sin intervención humana.
