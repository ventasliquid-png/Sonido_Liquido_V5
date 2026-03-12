# INFORME HISTÓRICO: REINGENIERÍA MULTIPLEX (CONTACTOS V6)
**Fecha:** 30 de Enero, 2026
**Responsable:** Agente Antigravity (Gy V14)
**Módulo:** Contactos / Identidad
**Estado:** ✅ DEPLOYED (N:M STABLE)

---

## 1. Misión y Contexto
El objetivo era resolver la **"Paradoja de Pedro"**: La incapacidad del sistema V5 de permitir que una misma persona física ("Pedro Polivalente") tuviera roles distintos en múltiples empresas (ej. "Jefe de Taller" en Transporte y "Comprador" en Cliente) sin duplicar su registro.

## 2. Solución Arquitectónica (Protocolo Multiplex)

### A. Modelo de Datos (Separación de Identidad)
Se refactorizó el esquema de base de datos para desacoplar a la **Persona** (el ser humano) de su **Vínculo** (el rol contextual).

*   **Tabla `personas`**:
    *   Almacena datos inmutables/personales: Nombre, Apellido, DNI, Fecha Nacimiento.
    *   **Canales Personales (JSON)**: `[{"tipo": "WHATSAPP", "valor": "+549...", "etiqueta": "Personal"}]`.
    *   Notas Globales: Preferencias personales (ej. "Fan de Racing").

*   **Tabla `vinculos`**:
    *   Relación N:M entre `Persona` y Entidades (`Cliente` o `Transporte`).
    *   **Polimorfismo**: Usa `entidad_tipo` ('CLIENTE'/'TRANSPORTE') y `entidad_id` (UUID).
    *   **Roles (JSON)**: `["DECISOR", "COBRANZAS"]` (Tags múltiples).
    *   **Canales Laborales (JSON)**: Emails corporativos, internos.
    *   Activo/Inactivo: Switch independiente por vínculo.

### B. Servicio de Búsqueda (Search & Link)
Para prevenir duplicados accidentales, se implementó un motor de búsqueda híbrido en el Backend (`service.get_contactos`):
*   Busca coincidencias parciales (`ILIKE`) en Nombre y Apellido.
*   **Búsqueda Profunda**: Penetra en el JSON de `canales_personales` (ej. busca por número de celular).
*   **Frontend (Typeahead)**: Implementado en `ContactCanvas.vue` con `debounce` de 300ms. Al detectar coincidencia, sugiere "Vincular Persona Existente" en lugar de crear una nueva.

## 3. Incidentes Críticos y Resoluciones

### incident-01: Error 500 en Listado de Clientes
*   **Síntoma**: El endpoint `/api/clientes` fallaba con `DetachedInstanceError` o `500 Internal Server Error`.
*   **Causa**: La propiedad computada `contacto_principal_nombre` en el modelo `Cliente` intentaba acceder a `self.vinculos` fuera de la sesión de base de datos.
*   **Solución**: Se implementó `options(joinedload(Cliente.vinculos_rel))` en la consulta del servicio para traer las relaciones en una sola query (Eager Loading), y se blindó el modelo con `try/except` para fallar con gracia (retornando "Sin Contacto") en caso de inconsistencia.

### incident-02: Dependencias Circulares (Legacy Hell)
*   **Síntoma**: Los scripts de QA (`test_qa_pedro.py`) fallaban al importar modelos. `Pedido` dependía de `Cliente`, que dependía de `Vinculo`, que dependía de `Cliente` (para relación inversa).
*   **Solución**: Se movieron los imports dentro de las clases o funciones en `models.py` y se ordenaron estrictamente en los scripts de prueba para asegurar que el `Mapper` de SQLAlchemy tuviera todas las clases definidas antes de resolver relaciones.

### incident-03: Duplicación en Vínculos
*   **Síntoma**: Las pruebas de robustez (`test_qa_edge_cases.py`) mostraron que era posible vincular a Pedro 2 veces con la misma empresa.
*   **Solución**: Se agregó validación *pre-flight* en `service.add_vinculo`. Si existe un vínculo activo con la misma tupla `(persona_id, entidad_tipo, entidad_id)`, se retorna el existente sin crear uno nuevo.

## 4. Estado Final
El sistema soporta ahora 100% de la funcionalidad N:M requerida.
*   **Backend**: Estable y protegido contra duplicados.
*   **Frontend**: UI renovada con "Billetera de Vínculos" (Tarjetas por empresa) y Buscador Inteligente.
*   **Migración**: Datos existentes migrados. Scripts disponibles para futuras limpiezas.

---
**Firma:** Gy V14 (Antigravity)
**Protocolo:** Omega Fase 1
