# CAJA NEGRA (BLACK BOX) - SONIDO LÍQUIDO V6 2026
**Última Actualización:** 04-Ene-2026

## 🛡️ Núcleo de Seguridad
- **Credencial IOWA (PSQL):** `SonidoV5_2025`
- **Host IOWA:** `104.197.57.226`
- **Usuario:** `postgres`

## 🔗 Estructura de Datos
- **Maestro Local:** `pilot.db` (SQLite)
- **Espejo Nube:** IOWA (Postgres)
- **Paridad Actual:** 271 Productos / 135 Clientes ✅

## 🛠️ Herramientas Críticas
- **Etiquetador PDF:** `tools/arca_oc_stamper/etiquetador_escritorio.py`
  - Lanzador: `ETIQUETADOR_PDF.bat`
  - Requisito: Directorio `backend` reconocido como paquete (vía `__init__.py`).
  - Dependencias: `customtkinter`, `pikepdf`, `reportlab`, `pypdf`.

## 📜 Doctrina de Sincronización
1. Toda modificación de productos o clientes DEBE iniciarse en el local (`pilot.db`).
2. El volcado a IOWA se realiza vía `scripts/force_push_absolute.py` (Modo Force Push).
3. IDs de Productos en IOWA son INTEGER (Alineados con el local).
