# 📓 BITÁCORA MAESTRA UX SISTEMA V5

**Propósito:** Registro centralizado de interacciones reales, incidentes de usabilidad y puntos de fricción reportados por operadores.
**Objetivo:** Base de conocimiento empírica para futuros Manuales y Guías de Solución.

---

## FOLIO #001
**FECHA:** 2026-01-12
**OPERADOR:** Tomás (Usuario No-Técnico)
**CATEGORÍA:** Despliegue e Instalación Inicial
**NIVEL DE USUARIO:** Básico
**TAGS:** #Instalación #PythonPath #MiedoConsola #PermisosWindows #UX

### RESUMEN DEL INCIDENTE
El usuario experimentó fricción crítica durante el despliegue del sistema V5 en un entorno Windows virgen.
1. **Confusión ZIP:** Intentó ejecutar sin descomprimir.
2. **Error de Ubicación:** Intentó instalar en G: (Drive) generando latencia y en C: generando error de permisos. Solución: Instalación en Escritorio, Backup en G:.
3. **Pánico CLI:** Miedo ante las ventanas de comandos ("pantalla negra").
4. **Fallo Crítico Python:** No marcó "Add to PATH" en la instalación, causando que el sistema no reconozca los comandos.
5. **Edición .env:** Desconocimiento de cómo abrir archivos sin extensión asociada.

### LECCIONES APRENDIDAS (PARA EL MANUAL)
- [ ] La guía de instalación debe prohibir instalar en G: y obligar el uso del Escritorio.
- [ ] Se debe advertir visualmente sobre el checkbox "Add Python to PATH" antes de descargar el instalador.
- [ ] Se debe explicar que las ventanas negras son normales ("el motor trabajando").
- [ ] No decir "editar .env", sino dar la instrucción de "Abrir con Bloc de Notas".

---
