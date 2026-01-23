# 🦅 DOCTRINA GIT: PROTOCOLO OMEGA

## 1. REGLA SUPREMA
**NUNCA TRABAJAR DIRECTAMENTE EN MAIN.**
La rama `main` es sagrada. Solo admite código probado y estable.

## 2. ESTRUCTURA DE RAMAS
Todas las ramas deben nacer de `main` (o la rama estable actual) y seguir esta nomenclatura:

-   `feat/[nombre-funcionalidad]`: Nuevas características (ej: `feat/alta-proveedores`).
-   `fix/[nombre-bug]`: Reparación de errores (ej: `fix/calculo-iva`).
-   `docs/[nombre-doc]`: Cambios en documentación (ej: `docs/manual-usuario`).
-   `refactor/[nombre-modulo]`: Mejoras de código sin cambiar comportamiento.

## 3. FLUJO DE TRABAJO (THE FLOW)
1.  **Check Status:** `git status` (Asegurar limpieza).
2.  **Pull:** `git pull origin main` (Sincronizar).
3.  **Branch:** `git checkout -b fix/nombre-tarea`.
4.  **Work:** Realizar cambios.
5.  **Commit:** `git commit -m "Fix: Descripción clara"`.
6.  **Push:** `git push origin fix/nombre-tarea`.
7.  **Merge:** (Vía Pull Request o Merge local controlado).

## 4. CHECKPOINT OBLIGATORIO
Antes de escribir una sola línea de código:
`git branch` -> Confirmar que NO estás en main.
