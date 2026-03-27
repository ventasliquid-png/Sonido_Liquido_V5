# PROTOCOLO OMEGA: El Cierre (V5 - Atenea)

Este protocolo asegura que la sesión de desarrollo se cierre de forma que el próximo "Despertar" sea coherente, incluso en situaciones de desastre.

## 1. Auditoría de Salud (Health Check)
Antes de cerrar, el agente debe declarar el estado del sistema:
- **NOMINAL**: Todo funciona, rama correcta, tests pasados.
- **ALERTA**: Funciona pero con deudas técnicas o rama provisional.
- **CRITICO (Catatónico)**: Nada funciona, DB corrupta o desincronía total de Git.

## 2. Inyección de Marcadores
Si el estado no es **NOMINAL**, el agente DEBE:
1.  **Bit de Estado**: Ejecutar `python scripts/manager_status.py set 3` (Bit CRÍTICO).
2.  **Situación Crítica**: Crear un bloque `> [!CAUTION]` al inicio de `INFORME_CIERRE_SESION.md` detallando el problema.

## 3. Generación de Documentación (Obligatorio)
No se considera una sesión finalizada sin:
1.  **Informe de Cierre**: `INFORME_CIERRE_SESION.md` (Situación actual).
2.  **Informe Histórico**: Guardar en `INFORMES_HISTORICOS/` con fecha y prefijo `YYYY-MM-DD_INFORME_SESION_...`.
3.  **Caja Negra**: Actualizar `_GY/_MD/CAJA_NEGRA.md` con los últimos movimientos técnicos.

## 4. Auditoría de Peso y Seguridad
Antes del PUSH, el agente debe:
1.  **Filtro de Tamaño**: Listar archivos que superen los 5MB (excepto .db si es intencional). Abortar si se detectan `.exe` o `.zip` no autorizados.
2.  **Verificación de .gitignore**: Asegurar que no se estén subiendo binarios pesados por error.
3.  **Regla de Oro (Límite 100)**: 
    - **PROHIBIDO** realizar un commit que incluya más de 100 archivos modificados/nuevos sin autorización explícita del usuario.
    - Esta regla previene la subida accidental de directorios como `node_modules`.
4.  **Ojo de Halcón (Auditoría V5.2)**: 
    - Ejecutar `python audit_v5.py`.
    - **Bloqueo de Seguridad**: Si `audit_v5.py` reporta archivos modificados que `git status` no tiene en Staging, o que no están en `ARCHIVOS_SESION`, la sesión queda BLOQUEADA. Prohibido solicitar PIN 1974. Corregir discrepancias antes de seguir.

## 5. Autorización y Ejecución Física (Fase de Abordaje Completo)
- **Procedimiento Obligatorio**:
    1.  `git add .` (Asegura captura de informes nuevos en `INFORMES_HISTORICOS/`).
    2.  `git status` (Verificación final contra `ARCHIVOS_SESION`).
    3.  `git commit -m "Omega: [Resumen de Misión]"` (Referencia al PIN 1974).
    4.  `git push` (Sello final).
- **Control de Salida (Ticket de Certificación)**: 
    - Tras el push, es OBLIGATORIO ejecutar `git show --name-only HEAD`. Este es el comprobante físico de la sincronización.
- **PIN 1974**: Solo tras superar la auditoría de Halcón y presentar el plan de cierre, el agente solicitará el PIN.

---
**Estado Final**: El agente declara el estado. Si se activa el Bit 3, la sesión queda marcada como **SITUACIÓN DE EMERGENCIA**. La limpieza de este bit es responsabilidad del próximo agente al ejecutar el **Punto 5 del Protocolo ALFA**, una vez verificado el retorno a la normalidad.
