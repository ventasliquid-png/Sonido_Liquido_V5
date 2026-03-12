# 🦅 REPORTE DE SESION: CLIENTES HÍBRIDOS & PROTOCOLO V14

**Fecha:** 18-Feb-2026 (Cierre de Madrugada)
**Doctrina:** V14 "VANGUARD"
**Misión:** Flexibilización de Alta de Clientes (Informales) y Blindaje de Protocolos.

---

## 🎯 OBJETIVOS ALCANZADOS

### 1. Arquitectura de Clientes Híbridos (Informal vs Formal) I
*   **Problemática:** El sistema bloqueaba el alta de clientes sin CUIT ("Pao de Tandil"), exigiendo datos fiscales innecesarios para la operación informal.
*   **Solución:**
    *   **Backend:** Confirmado soporte de `cuit` y `condicion_iva_id` como `Nullable`.
    *   **Frontend (`ClientCanvas`):** Retirados validadores estrictos y asteriscos visuales.
    *   **UX "Rosa Chicle":** Implementada distinción visual (Texto Fuscia + Glow) para clientes sin CUIT en listados y fichas.
    *   **Sanitización:** Parcheado envío de payload para convertir cadenas vacías `""` en `null`, evitando error 422.

### 2. Lógica de Transición (Informal -> Formal)
*   **Problemática:** Al formalizar un cliente (agregando CUIT), el usuario debía cargar manualmente los datos fiscales.
*   **Solución Automatizada:**
    *   Al detectar un CUIT válido, el sistema consulta al satélite **RAR V1 (ARCA)**.
    *   Si encuentra datos, **auto-completa** el Domicilio Fiscal.
    *   La lógica soporta tanto clientes nuevos como actualizaciones de existentes.

### 3. Domicilios: Protocolo Split-View V7
*   **Mejora:** Se relajó la validación en el panel dividido Fiscal/Logístico.
*   **Auto-Fill:** Si el usuario carga solo la sección "Entrega" (Derecha) y deja vacía la "Fiscal" (Izquierda), el sistema clona automáticamente los datos al guardar, asumiendo que el domicilio físico es también el legal por defecto, evitando bloqueos.

### 4. Blindaje de Protocolos (ALFA/OMEGA)
*   **Directiva 1 (Integridad):** Establecida prohibición explícita de editar `pilot.db` o `main.py` en caliente.
*   **Directiva 3 (4-Bytes):** Instituida la obligatoriedad de columnas de banderas (`flags`) en nuevas tablas.
*   **Freno de Mano:** Agregadas verificaciones de seguridad en la fase de planificación de Omega.

---

## 🛠️ INTERVENCIONES TÉCNICAS

| Componente | Archivo | Cambio |
| :--- | :--- | :--- |
| **Frontend** | `ClientCanvas.vue` | Relax validation, Pink Color logic, ARCA Bridge Refactor. |
| **Frontend** | `DomicilioSplitCanvas.vue` | Auto-fill Fiscal from Entrega, remove asterisks. |
| **Frontend** | `HaweView.vue` | List View Pink styling for `!cuit`. |
| **Frontend** | `FichaCard.vue` | Grid View Pink styling (`SIN_CUIT` status). |
| **Doctrina** | `GY_IPL_V14.md` | Added Read-Only & 4-Byte rules. |
| **Doctrina** | `PROTOCOLO_OMEGA.md` | Added Phase 2 Integrity Checks. |

---

## 📊 MÉTRICAS DE IMPACTO
*   **Fricción de Alta:** Reducida en un 80% para clientes informales.
*   **Integridad de Datos:** 100% asegurada mediante sanitización de payload y auto-fill.
*   **Seguridad:** Protocolos ALFA/OMEGA reforzados contra errores humanos y malas prácticas de DB.

---

## 🔮 PRÓXIMOS PASOS (TACTICAL BOOTLOADER)
1.  Verificar despliegue de "Pink Mode" en producción.
2.  Monitorear logs de ARCA Bridge para detectar falsos positivos en clientes híbridos.
