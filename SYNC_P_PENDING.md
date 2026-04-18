# SINCRONIZACIÓN P (PRODUCCIÓN) — PENDIENTE

**Fecha:** 2026-04-17  
**Cambios:** Fixes rubros (soft-delete visibility + hard-delete serialization)

## ⚠️ CHECKLIST ANTES DE SINCRONIZAR P

- [ ] **Bajar PULL del GIT en P** (`C:\dev\v5-ls-Tom`)
  - Los commits están en main: `98a83a9c`, `9a48be21`
  
- [ ] **CRÍTICO: Reemplazar base de datos P**
  - Respaldar: `V5_LS_MASTER.db` → `V5_LS_MASTER.db.old`
  - Usar: `POLIZON_MAESTRO.bak` → `V5_LS_MASTER.db`
  - **SIN ESTO → tendrás los mismos problemas de schema desincronizado que tuviste ayer**

- [ ] **Frontend build** en P:
  - `cd frontend && npm run build`
  - Copiar `dist/*` → `static/`

- [ ] **Verificar Canario** en P

## Archivos modificados en D
- `backend/productos/service.py` (hard_delete JSON fix)
- `frontend/src/services/rubrosApi.js` (include_banned=true)

---
PIN 1974 ✓
