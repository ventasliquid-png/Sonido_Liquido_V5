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
2.  **Informe Histórico**: Guardar en `INFORMES_HISTORICOS/` con fecha y prefijo `PROTOCOLO_OMEGA_...`.
3.  **Caja Negra**: Actualizar `_GY/_MD/CAJA_NEGRA.md` con los últimos movimientos técnicos.

## 4. Auditoría de Peso y Seguridad
Antes del PUSH, el agente debe:
1.  **Filtro de Tamaño**: Listar archivos que superen los 5MB (excepto .db si es intencional). Abortar si se detectan `.exe` o `.zip` no autorizados.
2.  **Verificación de .gitignore**: Asegurar que no se estén subiendo binarios pesados por error.

## 5. Autorización y Ejecución Física (Cláusula Carlos)
- **NUNCA** ejecutar comandos de Git de forma automática o genérica.
- **Plan de Cierre**: El agente debe presentar un resumen de qué archivos va a subir.
- **PIN 1974**: Solo tras recibir el PIN exacto, el agente ejecutará el `git push`.
- **Certificación**: Al terminar, el agente debe mostrar la salida real de la consola de Git para confirmar la "Subida Física".

---
**Estado Final**: El agente declara el estado. Si se activa el Bit 3, la sesión queda marcada como **SITUACIÓN DE EMERGENCIA**. La limpieza de este bit es responsabilidad del próximo agente al ejecutar el **Punto 5 del Protocolo ALFA**, una vez verificado el retorno a la normalidad.
