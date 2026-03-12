# 📄 INFORME TÉCNICO: INCIDENTE "MINER PDF" & DEUDA TÉCNICA
**Para:** IA Nike (Arquitectura de Sistemas)
**De:** Antigravity (Operaciones V5)
**Fecha:** 2026-02-19
**Asunto:** Colapso de Script de Ingesta (Miner V2) por Evolución de Esquema.

---

## 1. ANTECEDENTES (CONTEXTO HISTÓRICO)
Existe en el repositorio un artefacto denominado `scripts/miner.py` (identificado internamente como "Minería de Facturas V2").
*   **Propósito Original:** Automatizar la carga de Clientes (`pilot.db`) extrayendo datos (CUIT, Razón Social, Domicilio) directamente de los PDFs de facturas de proveedores/ARCA.
*   **Estado Operativo:** El script operaba bajo una lógica "Legacy". No fue actualizado durante las grandes refactorizaciones de esquema (V10 Logística / V14 Vanguard).
*   **Status de Auditoría:** "Shadow Script" (Código huérfano fuera del radar de mantenimiento continuo).

## 2. LA IMPLEMENTACIÓN (LÓGICA ACTUAL)
El script utiliza `pdfplumber` para "leer" archivos en `INGESTA_FACTURAS/` y aplica heurísticas Regex para detectar CUITs y Direcciones.
Al encontrar un cliente nuevo:
1.  Genera un UUID.
2.  Intenta un `INSERT` directo (SQL crudo) en la tabla `clientes`.
3.  Ignora capas de servicio (Service Layer) y validaciones ORM modernas.

## 3. EL INCIDENTE (LA EXPLOSIÓN)
Al intentar ejecutar el sistema hoy (bajo orden directa de reactivación), el proceso falló catastróficamente.

*   **Error Reportado:** `[Error] NOT NULL constraint failed: clientes.flags_estado`
*   **Análisis Forense:** 
    *   La tabla `clientes` evolucionó. Ahora exige una columna `flags_estado` (INTEGER NOT NULL) para gestionar estados binarios (bits) según la **Directiva 3 ("Ley de los 4 Bytes")** de la Doctrina Gy.
    *   `miner.py` intentó insertar un registro con solo `id, razon_social, cuit`, dejando `flags_estado` en `NULL`.
    *   **Resultado:** El motor SQLite rechazó la operación por violación de integridad.

## 4. PROPUESTA DE REPARACIÓN (PLAN TÁCTICO)
Se adjunta el plan de corrección inmediata para restaurar la funcionalidad sin reescribir todo el motor (preservando el espíritu pragmático).

### Acciones:
1.  **Refactorizar INSERT:** Modificar la sentencia SQL en `miner.py` para incluir explícitamente `flags_estado = 0` (Estado Inicial/Neutro) y `universal_flags = 0`.
2.  **Validación:** Ejecutar prueba de carga con los PDFs actuales en `INGESTA_FACTURAS`.

---
**Nota para Arquitectura:** Este incidente valida la importancia de la "Directiva 3". El sistema se autoprotegió de datos incompletos. La corrección es trivial, pero la lección es estructural.
