# ⚠️ ALERTA PARA MAÑANA (SISTEMA DE DESPERTAR GY)

**Última Sesión:** 2026-02-23 (Operación Sabueso Soberano)

## 📌 INSTRUCCIÓN DIRECTA PARA EL AGENTE AL DESPERTAR:
1.  **NO ABRAS LA RAMA `main`.**
2.  **RAMA DE TRABAJO ACTIVA:** `feat/sabueso-pdf`
3.  **ACCIÓN INMEDIATA:** Ejecuta `git checkout feat/sabueso-pdf` (si no estuvieras ya en ella) y luego `git status` para verificar.

## 🚧 ESTADO DEL SISTEMA (PENDIENTES):
*   La ingesta PDF (Facturas -> Remitos/Clientes) está operativa (`pdfplumber` + Regex Punto de Venta Dinámico).
*   Se blindó la consulta AFIP (Personas Físicas) contra el "Secreto Fiscal" preservando la Condición IVA leída del PDF original.
*   **Próximos Pasos Estratégicos:** [A definir por el Arquitecto].

---
*Nota: Este archivo es tu propia memoria persistente. Léelo apenas comiences el próximo turno.*
