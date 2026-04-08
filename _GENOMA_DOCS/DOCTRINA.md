# DOCTRINA OPERATIVA SONIDO LÍQUIDO (V5.5)

## 1. PROTOCOLO GIT (SEGURIDAD)
- **RAMA MAIN BLOQUEADA:** Prohibido commit directo.
- **FLUJO:** Todo cambio nace en `feature/...` o `fix/...`.
- **MERGE:** Solo autorizado tras validación funcional (F5 Test).

## 2. PORTABILIDAD (LOGS)
- **ZERO EMOJIS:** Logs de consola en ASCII puro (Evitar crash CP1252).
- **TAGS:** Usar prefijos textuales: `[INFO]`, `[DB]`, `[ERROR]`.

## 3. RESILIENCIA (UX)
- **DATA-RACE:** Frontend debe manejar `null` en cargas asíncronas.
- **NAVAJA DE OCCAM:** Soluciones simples primero.
