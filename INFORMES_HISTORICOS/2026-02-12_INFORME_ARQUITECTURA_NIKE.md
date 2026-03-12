# 🏛️ INFORME DE ARQUITECTURA: PROTOCOLO PUENTE & MDM (Para Nike)

**Fecha:** 12 de Febrero de 2026
**Autor:** Antigravity
**Destinatario:** Nike (Arquitecta de Sistemas V5)
**Contexto:** Integración RAR V1 (Satélite) -> Sonido Líquido V5 (Núcleo)

## 1. Misión Cumplida: "The Bridge"
Hemos establecido una conexión orgánica entre la capacidad de validación fiscal de RAR y la operación diaria de V5, sin duplicar código ni crear microservicios complejos.

### Arquitectura Implementada
- **Modelo:** *Satellite Library Pattern*.
- **Mecanismo:** V5 realiza un `sys.path.append('C:/dev/RAR_V1')` en tiempo de ejecución (Lazy Load) solo cuando se solicita validación fiscal.
- **Seguridad:** V5 utiliza las credenciales y certificados que residen físicamente en el directorio de RAR (`certs/`), manteniendo la custodia en el satélite.

## 2. Estrategia MDM: "The Golden Flag" (Gestión de Datos Maestros)
Para resolver la tensión entre "Datos Sucios Operativos" (lo que permite facturar hoy) y "Datos Puros" (lo que AFIP dice), hemos implementado:

### A. Entidad `Cliente`
- Se agregó columna `estado_arca` (String: `PENDIENTE`, `VALIDADO`, `CONFLICTO`).
- **Lógica de Negocio:**
    - El operador puede seguir vendiendo con datos "Barro" (`PENDIENTE`).
    - Al usar el botón "Consultar AFIP", el sistema inyecta los datos oficiales y marca `VALIDADO`.
    - **Protección UI:** Un `Cliente` validado muestra un escudo verde ("ARCA OK") y futuras ediciones sobre Razón Social/CUIT advertirán sobre la ruptura de integridad.

### B. Definición Estratégica: Productos (Próxima Fase)
**Decisión Crítica:** V5 es la **AUTORIDAD SUPREMA** de SKUs.
- RAR V1 pasará a modo "Read-Only" respecto al inventario.
- **Flujo:** RAR lee `pilot.db`. Si el producto existe, usa su SKU. Si no existe, bloquea la operación y obliga al alta en V5.
- **Justificación:** Evitar la "esquizofrenia de inventario" donde dos sistemas numeran distinto el mismo artículo.

## 3. Refactorización & Deuda Técnica Resuelta
- **Bugfix (RAR Core):** Se corrigió un crash en `rar_core.py` al procesar Personas Físicas (CUIT 20/27) donde AFIP no devuelve `formaJuridica`. Patch aplicado y validado.
- **Frontend V5:** Se limpió un error de sintaxis en `ClienteInspector.vue` (llave extra) y se modularizó la llamada al servicio de puente.

## 4. Estado del Sistema (Handover)
- **Base de Datos:** Migrada (`migration_v7_arca_flags.py` ejecutado).
- **Dependencias:** `zeep`, `lxml` instaladas en V5.
- **Conectividad:** Probada y funcional.

**Recomendación para Nike:**
En la próxima iteración de "Pedidos", considerar capturar el evento de `estado_arca` para, quizás, bonificar o facilitar condiciones de pago a clientes "Golden" (validados), incentivando la limpieza del padrón.

---
*Antigravity - Session 9e53ded8*
