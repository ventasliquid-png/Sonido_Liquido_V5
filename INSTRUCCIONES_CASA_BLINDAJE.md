# 🦅 DOCTRINA GY: PROTOCOLO ALFA (CASA - SINCRONIZACIÓN Y BLINDAJE)

**Gy (CASA), soy Gy (OFICINA).**
Esta noche tu misión es crítica: **Debes asegurar que el código de anoche suba a la nube, y debes hacerlo incluyendo el nuevo protocolo de seguridad.**

## PASO 1: ACTUALIZACIÓN INMEDIATA DE OMEGA
Antes de hacer cualquier push, edita el archivo `_GY/_SKILLS/PROTOCOLO_OMEGA.md` e INSERTA este bloque obligatorio después del paso "Git Push":

```markdown
### 🔎 FASE 3.5: VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)
**OBLIGATORIO:** Tras el `git push`, el Agente **TIENE PROHIBIDO** reportar éxito sin antes verificar la realidad en el servidor.

1.  **Ejecutar:** `git log origin/[RAMA_ACTIVA] -n 1 --format="%h - %s"`
2.  **Validar:** El hash devuelto **DEBE** coincidir con el hash de tu commit local (`git rev-parse HEAD`).
3.  **Sentencia:** Si el comando da error, no devuelve nada, o los hashes no coinciden, **EL PUSH NO OCURRIÓ**.
    *   🛑 **ACCIÓN:** Reportar "FALLO DE SINCRONIZACIÓN" y **NO** proceder al cierre.
    *   ⚠️ **JAMÁS** asumir que el push funcionó solo porque no hubo mensajes de error explícitos en el paso anterior.
```

## PASO 2: EJECUCIÓN DE BLINDAJE
Una vez actualizado el archivo Omega, ejecuta lo siguiente en la terminal:

1.  **Verificar Estado:** `git status` (Deberías ver modificado `PROTOCOLO_OMEGA.md` y todos los archivos del refactor de anoche).
2.  **Empaquetar Todo:** `git add .`
3.  **Compromiso Final:** `git commit -m "feat(core): Refactor 4 modulos V5-X + Protocolo Omega Blindado"`
4.  **Sincronización:** `git push origin feat/v5x-universal`

## PASO 3: LA PRUEBA DE FUEGO (NUEVO PROTOCOLO)
Ejecuta inmediatamente:
`git log origin/feat/v5x-universal -n 1 --format="%h - %s"`

*   Si ves el hash y el mensaje "Refactor 4 modulos...", **MISIÓN CUMPLIDA.**
*   Si no lo ves, **NO APAGUES LA MÁQUINA.** Intenta de nuevo.
