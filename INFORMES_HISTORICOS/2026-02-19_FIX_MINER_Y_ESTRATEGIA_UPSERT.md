# INFORME HISTÓRICO: IMPLEMENTACIÓN UPSERT INTELIGENTE (MINER PDF)
**Fecha:** 2026-02-19
**Versión:** V6.5
**Estado:** HÍBRIDO (Backend Script OK / Frontend Pendiente)

## 1. OBJETIVO TÁCTICO
Implementar una estrategia de "Upsert Inteligente" para la ingesta de facturas PDF de ARCA (AFIP). El sistema debe ser capaz de:
1.  Detectar si el cliente ya existe (por CUIT o Nombre).
2.  **Actualizar (Upsert):** Si existe pero tiene un status de calidad bajo (ej. Flag 3 Temporal), elevarlo a **Flag 13** (Gold Candidate) y eliminar la marca de "Virginidad".
3.  **Crear (Insert):** Si es nuevo, insertarlo directamente con Flag 13 y estado `PENDIENTE_AUDITORIA` para revisión humana ("Peaje de Calidad").

## 2. INTERVENCIONES REALIZADAS

### A. Refactorización de `miner.py` (Script de Backend)
Se reescribió la lógica de inserción para cumplir con la Doctrina V14:
*   **Búsqueda Dual:** Primero por CUIT exacto. Si falla, búsqueda difusa (`LIKE`) por Razón Social.
*   **Bitmask Logic (Flags):**
    *   **Antes:** Creaba Flag 3 (Activo + Virgin) o fallaba.
    *   **Ahora:**
        *   `IS_VIRGIN` (0x02) se **ELIMINA** (`flags & ~2`).
        *   `FISCAL_REQUIRED` (0x04) y `ARCA_VALIDATED` (0x08) se **AÑADEN**.
        *   Resultado: **Flag 13** (1 | 4 | 8).
    *   **Estado Visual:** `estado_arca` se setea a `'PENDIENTE_AUDITORIA'`, disparando el color Amarillo en la UI.
*   **Corrección Crítica Regex:**
    *   Se detectó que la limpieza de texto (`replace(" ", "")`) destruía los límites de palabras en facturas compactas (ej. LAVIMAR), fusionando el CUIT con el nombre.
    *   **Solución:** El script ahora escanea primero el texto crudo (`text`) buscando patrones de CUIT válidos antes de intentar limpiar.

### B. Verificación y Pruebas
*   **Caso LAVIMAR:** El script detectó correctamente el CUIT `30-53660291-3` en el PDF que antes fallaba.
*   **Idempotencia:** Ejecuciones sucesivas del script no duplican clientes, sino que actualizan la fecha `updated_at` y reafirman los flags.

## 3. INCIDENTE ABIERTO (HANDOVER PARA PRÓXIMA SESIÓN)
Durante la verificación final, el usuario reportó:
> "Error: El servidor no pudo interpretar el archivo" al subir el mismo PDF en la Web.

**Diagnóstico:**
*   El Frontend utiliza el endpoint `/remitos/ingesta-pdf`, el cual es manejado por `backend/remitos/pdf_parser.py`.
*   Este parser utiliza la librería `pypdf`, la cual tiene un motor de extracción de texto menos robusto que `pdfplumber` (usado en `miner.py`).
*   **Resultado:** El backend web falla al parsear el PDF que el script local procesa perfectamente.

## 4. ESTRATEGIA PARA PRÓXIMA SESIÓN
1.  **Refactorizar `pdf_parser.py`:** Reemplazar `pypdf` por `pdfplumber`.
2.  **Portar Lógica de `miner.py`:** Copiar la lógica de "Regex sobre Texto Crudo" al endpoint de la API.
3.  **Unificar Criterios:** Asegurar que la subida web también aplique la lógica de Upsert Inteligente.

---
**Firma:** Agente Gy (Protocolo Omega V14)
