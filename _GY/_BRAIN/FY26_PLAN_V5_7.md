# [V5.7] Plan de Implementación: Integridad y Datos Externos

> **CONTEXTO:** Generado en SESIÓN HOME (Recuperación).
> **ESTADO:** PROPUESTA (Para Sesión Siguiente)

## Objetivo General
Implementar rutinas de validación y enriquecimiento de datos utilizando fuentes externas (Web/ARCA) para garantizar la consistencia sanitaria de la base de datos `pilot.db` y `cantera.db`.

## Características Propuestas

### 1. Enriquecimiento Masivo "Cantera" (Batch)
Automatar la limpieza de la base de datos histórica (`cantera.db`) antes de importarla a V5.
- **Input:** Lista de nombres "sucios" (ej. "Lavimar", "Farmacia Luvianka").
- **Proceso:** 
  1. Agente Navegador busca en Google/CuitOnline.
  2. Extrae CUIT, Razón Social Oficial y Domicilio Fiscal.
  3. Compara con datos existentes.
- **Output:** Base de datos intermedia `enriched_clients.db` lista para importar.

### 2. Asistente de Alta "ARCA Lookup" (Real-time)
Herramienta para el operador durante el alta de clientes nuevos.
- **Workflow:**
  1. Operador ingresa CUIT o Nombre parcial.
  2. Sistema consulta fuente externa (Simuador o Web Scraping on-demand).
  3. Auto-completa el formulario de `ClienteInspector` con datos oficiales.
- **Beneficio:** Evita errores de tipeo y asegura domicilios fiscales válidos desde el día 0.

## Estrategia Técnica
*   Ultilizar **Browser Subagent** (Navegador Real) en lugar de API de búsqueda para sortear bloqueos y obtener datos renderizados.
*   Implementar Cache local para no re-consultar CUITs ya validados.

## Próximos Pasos (Sincronización)
1.  Hacer Pull de la rama oficial (Office).
2.  Ejecutar scripts de enriquecimiento.
