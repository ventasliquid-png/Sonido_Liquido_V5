# INFORME DE SESION: SOBERANIA OPERATIVA V14.8.4
**Fecha:** 2026-03-18
**Operador:** Antigravity (Gy)
**Referencia:** OMEGA-1974
**Version:** V14.8.4

---

## 1. OBJETIVO DE LA SESION

Correccion de dos colapsos criticos en el modulo Hawe e implementacion de la Directiva Estructural V14.8.4 de Soberania Operativa: el criterio de carga humana prevalece sobre la validacion ARCA/AFIP.

---

## 2. HITOS TECNICOS

### A. Fix Integridad — provincia_id 'X'
**Archivo:** `frontend/src/views/Hawe/ClientCanvas.vue` (L1437)
**Problema:** String literal invalido `provincia_id: 'X'` al inicializar un cliente en modo modal. Causaba violacion de FK en tabla `provincias` y Error 400 al intentar guardar.
**Consecuencia observada:** Salud Privada SRL quedaba atrapada en estado Amarillo porque el guardado fallaba antes de limpiar el Bit 20.
**Solucion:** Reemplazado `'X'` por `null`.

### B. Fix Logica — KEEP_OLD en DomicilioSplitCanvas
**Archivo:** `frontend/src/views/Hawe/components/DomicilioSplitCanvas.vue`
**Problema:** La funcion `resolveSync('KEEP_OLD')` leia `props.domicilio` directamente. Por la reactividad de Vue, `props.domicilio` podia ya reflejar el nuevo dato fiscal, pisando la direccion de entrega original que se queria conservar.
**Solucion:** Implementado `snapshotEntrega` (ref) que captura una deep copy del estado de entrega al montar el watcher. `resolveSync` usa el snapshot inmutable.

### C. Lupa No Destructiva
**Archivo:** `frontend/src/views/Hawe/ClientCanvas.vue` (bloque `consultarAfip`)
**Problema:** El bloque `else` de actualizacion de domicilio fiscal pisaba directamente la calle con el dato de ARCA sin preguntar, incluso cuando el operador habia hecho correcciones manuales.
**Solucion:** Verificacion: si el nodo fiscal ya tiene calle cargada, se muestra confirm() con el dato de ARCA vs el dato manual. El usuario decide.

### D. Color por Soberania (V14.8.4)
**Archivo:** `frontend/src/views/HaweView.vue` (funcion `getClientColorMode`)
**Cambio:** Eliminada la dependencia de `estado_arca === 'VALIDADO'`. El color blanco ahora se dispara si `!(flags & 1048576)` — es decir, si el Bit 20 (PENDIENTE_REVISION) esta apagado.

### E. Soberania Operativa — Promocion 15->13
**Archivos:** `ClientCanvas.vue` (Frontend) + `backend/clientes/service.py` (Backend)

**Logica de 4 Pilares:**
```
si (razon_social && lista_precios_id && segmento_id && domicilio_fiscal.calle > 2 chars):
    flags_estado &= ~2        // Bit 1 OFF: Quitar IS_VIRGIN (15->13)
    flags_estado &= ~1048576  // Bit 20 OFF: Quitar PENDIENTE_REVISION
    flags_estado |= 1         // Bit 0 ON: Asegurar IS_ACTIVE
```

**Caso parcial** (lista+segmento sin domicilio): solo limpia Bit 20.

**Escudo Doble:**
- Frontend opera antes de `payload.flags_estado = currentFlags` en `saveCliente`.
- Backend opera en `update_cliente` post-setattr, blindando la mutacion contra llamadas directas a la API.

---

## 3. ESTADO POST-SESION

| Componente | Estado |
|---|---|
| `ClientCanvas.vue` | FK fix + 4 Pilares + Lupa No Destructiva |
| `DomicilioSplitCanvas.vue` | KEEP_OLD corregido con snapshot inmutable |
| `HaweView.vue` | Color = f(Bit 20). Independiente de AFIP |
| `service.py` | Escudo backend: promocion 15->13 forzada |

---

## 4. CONCLUSION

El sistema evoluciona de ser un observador pasivo (esperando que ARCA valide para asignar color blanco) a un Escudo Proactivo: la calidad de carga del operador determina el estado del registro. La arquitectura de 64 bits (BigInteger `flags_estado`) permanece intacta. El protocolo de seguridad PIN 1974 fue respetado en todas las fases de escritura.

---
**SELLO OMEGA: 1974**
**Timestamp:** 2026-03-18T17:15:00-03:00
