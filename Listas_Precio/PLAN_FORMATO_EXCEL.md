# 📊 IMPLEMENTATION PLAN: EXCEL FORMATTING (2026-02)

**Goal:** Replicate the visual structure of sheet `2025-05` in the new `2026-02` update.

## 1. ANALYSIS OF MODEL SHEET (2025-05)
*   **Header Row:** 4 (Index 3).
*   **Key Columns:**
    *   **B:** Código (`701`, `720`)
    *   **C:** Descripción (`Botella 1 lt...`)
    *   **E:** "Lista 20 con -7 y -2" (Base Cost) -> **MAPPED TO `Costo Nuevo`**
    *   **F:** "Mayorista" (Calculated)
    *   **G:** "Minorista" (Calculated)
    *   **H:** "Minorista con IVA" (Calculated)

## 2. PROPOSED STRATEGY
We will use `openpyxl` directly (more control than pandas) to:
1.  **Clone Formatting:** (Ideal, but complex) or **Mimic Structure**.
2.  **Map Data:**
    *   CSV `Codigo` -> Excel Col **B**.
    *   CSV `Descripcion` -> Excel Col **C**.
    *   CSV `Costo Nuevo` -> Excel Col **E**.
3.  **Formulas (The "Smart" Excel):**
    *   Instead of hardcoding values for Mayorista/Minorista, we will inject **Excel Formulas**.
    *   Col F (Mayorista) = `=E{row}*1.30` (Estimated 30% margin, adjustable).
    *   Col G (Minorista) = `=F{row}*1.20` (Estimated 20% margin over Mayorista).
    *   **Why?** Allows the user to change the margin later by just dragging.

## 3. ORDERING
*   Move the new sheet `2026-02` to **Index 0** (First tab).

## 4. VERIFICATION
*   Script: `scripts/update_excel_formatted.py`.
*   Manual Check: User opens Excel to verify layout.
