# 📔 BITÁCORA DE DESARROLLO (V5)
**Fecha:** 2026-01-09
**Operador:** Gy (Antigravity) | **User:** Carlos
**Estado:** 🟢 ACTIVO

---

## 📅 SESIÓN [2026-01-09] | Independencia V1 (Gy V9)
- **Hito:** Despliegue de infraestructura autónoma ("Twin Towers").
- **Backend:** Implementado `BackupManager` y `ExcelExportService`.
- **Frontend:** Mejoras visuales (GlobalStatsBar) y botón de exportación.
- **DevOps:**
    - Creado `scripts/build_release.py` para empaquetado seguro.
    - Creados `.bat` de instalación/inicio.
    - Definida estrategia Update vs Install.
- **Estado:** V1.0 Congelada y lista para entrega.

## 📅 SESIÓN [2026-01-08] | Zen Mode Fix (Gy V8)

## 📅 SESIÓN [2026-01-09] - "CIMIENTOS DE ACERO"

### 🎯 Objetivos Tácticos
1.  **Estabilización de Rutas:** Fix crítico en `backend/core/database.py` para usar rutas absolutas y evitar `pilot.db` fantasmas.
2.  **Sincronización IOWA:** Implementación de protocolo "Wipe & Replace" exitoso (Clientes, Productos, Pedidos).
3.  **Documentación:** Creación de `MANUAL_TECNICO_V5.md` y `GLOSARIO_TACTICO.md`.

### 🛠️ Cambios Realizados
*   **Backend:** Refactor de `database.py` para detectar `project_root`.
*   **Scripts:** Backend de sincronización (`push_session_to_iowa.py`) con sanitizador de booleanos y orden topológico.
*   **Base de Datos:** Update de modelos `Provincia` y `Domicilio` (String(1) -> String(5)) para soportar legacy codes.
*   **Archivos:** Migración de logs antiguos a `ARCHIVE_LOGS_LEGACY.md`.

### 🚨 Incidencias y Soluciones
*   **Incidencia:** Error `value too long` en Provincias.
*   **Solución:** Resize de columna `id` a varchar(5) en modelos SQLAlchemy y recreación de esquema.
*   **Incidencia:** Booleanos rechazados por Postgres (`0`/`1`).
*   **Solución:** Sanitizer en script python para convertir a `True`/`False` nativo.

### 📊 Estado Final (SITREP)
*   **IOWA:** Sincronizado (4 Clientes, 5 Productos, 2 Pedidos).
*   **PILOT:** Estable en Raíz.
*   **Rutas:** Absolutas.

---

## 📅 SESIÓN [2026-01-13] | Release V1.1 & UX Refactor
- **Hito:** Lanzamiento de versión V1.1 y Refactorización UX Alta Clientes.
- **Backend:** 
    - Fix crítico en `clone_pedido`: Copia profunda de atributos financieros.
    - Release Script: Inclusión de `cantera*.db` en paquetes de actualización.
- **Frontend:**
    - **Alta Clientes:** Migración a Modal Central (Canvas) en `HaweView` para mejorar usabilidad y visibilidad de controles.
    - **SmartSelect:** Parche lógica de búsqueda para incluir `razon_social` y `cuit`.
    - **Búsqueda Global:** Integración de "Buscar en Cantera" dentro de módulos operativos (Pedidos).
- **Estado:** V1.1 Generada. Protocolo Omega Ejecutado.
- **Métricas Cierre:** Clientes: 4 | Productos: 5 | Pedidos: 2

---
**Nota:** Para historial anterior, consultar `ARCHIVE_LOGS_LEGACY.md`.
