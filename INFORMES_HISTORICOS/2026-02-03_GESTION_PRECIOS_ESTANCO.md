# INFORME TÉCNICO: LABORATORIO DE PRECIOS (SISTEMA ESTANCO)
**ID DE SESIÓN:** 785
**FECHA:** 03 de Febrero de 2026
**ESTADO FINAL:** 🟢 OPERATIVO (MODO LABORATORIO)

## 1. OBJETIVOS TÁCTICOS (CUMPLIDOS)
El objetivo fue implementar un sistema para gestionar listas de precios de proveedores (Celtrap) sin alterar la base de datos operativa, permitiendo simulación y generación de entregables formateados.

## 2. ARQUITECTURA "SISTEMA ESTANCO"
Se definió el módulo `LISTAS_PRECIO` como una "Esclusa de Aire".
*   **Entrada:** `LISTAS_PRECIO/Proveedores/Celtrap` (Archivos crudos: PDF, XLSX).
*   **Proceso:** Scripts Python en `scripts/` (Sin acceso de escritura a DB).
*   **Salida:** Archivos Excel generados en la misma carpeta (Versiones incrementales).

## 3. INTERVENCIONES REALIZADAS

### A. Herramientas Desarrolladas
1.  **`scripts/simulate_price_impact.py`**: Lee CSV y cruza con DB para ver variación % (Dry Run).
2.  **`scripts/create_celtrap_v3.py`**: Motor de "Inyección de Template".
    *   Toma la hoja modelo `2025-05` de `Celtrap (2).xlsx`.
    *   Clona estilos, agrupaciones y fórmulas.
    *   Inyecta precios nuevos del CSV.
    *   Genera `Celtrap (3).xlsx`.

### B. Reglas de Negocio Implementadas
*   **Regla 301 (Camilleros):** Se hardcodeó una excepción lógica. Si SKU es 301, el precio no viene del CSV, sino que es `Costo Historico * 1.10`.
*   **Márgenes Automáticos:**
    *   Mayorista: `=Costo * 1.38`
    *   Distribuidor: `=Mayorista / 0.895`
    *   Minorista: `=Distribuidor * 1.25`

## 4. LECCIONES APRENDIDAS
*   **Excel Locking:** Los scripts de `openpyxl` fallan si el usuario tiene el archivo abierto (`PermissionError`). Es vital cerrar el Excel antes de correr procesos.
*   **Template Strategy:** Para mantener agrupaciones visuales complejas ("Jabones", "Toallas"), es más eficiente clonar una hoja vieja y rellenar celdas que intentar recrear el formato desde cero con código.

## 5. ESTADO DE DOCTRINA
*   **Protocolo:** Se respetó la orden "Estanco". No se realizaron `UPDATE` en la tabla `productos` de `pilot.db`.
*   **Seguridad:** Se requiere PIN 1974 para el cierre de sesión.

---
**OPERADOR:** Antigravity (Gy V14)
