# INFORME TÉCNICO: PROTOCOLO OMEGA - ESTABILIZACIÓN DE DOMICILIOS
**Fecha:** 2026-01-23  
**Estado:** ÉXITO / ESTABLE  
**Módulos Afectados:** Clientes (Backend/Frontend), Logística, Base de Datos.

---

## 1. Objetivo de la Sesión
Resolver la inconsistencia en la carga de direcciones (particularmente Piso y Departamento), refinar la UX de la Ficha de Cliente V5 y solucionar los crashes del Backend ("Lista Vacía").

## 2. La Saga "Piso y Departamento" (Análisis Post-Mortem)

### Intento 1: Modificación Estructural (Fallido)
Se intentó agregar columnas físicas (`piso`, `depto`) a la tabla `domicilios` en la base de datos y al modelo SQLAlchemy.
*   **Problema:** Esto generó conflictos severos con el ORM (SQLAlchemy) y Pydantic, causando un "Lazy Load Error" que rompía la serialización de la lista de clientes (Error 500). El sistema esperaba columnas que, aunque existían en código, generaban ambigüedad en las consultas complejas (`joinedload`).

### Solución Definitiva: Estrategia de "Fusión" (Rollback + Logic)
Para garantizar la estabilidad (que "se vea lo que andaba antes"), optamos por:
1.  **ROLLBACK NUCLEAR:** Eliminamos las columnas `piso` y `depto` del modelo de base de datos (`models.py`) para volver al esquema "Golden Master" (Estable).
2.  **LÓGICA DE FUSIÓN (Backend):** 
    En `service.py` (`create_domicilio` y `update_domicilio`), interceptamos los campos `piso` y `depto` que vienen del Frontend. 
    En lugar de guardarlos en columnas separadas, los **fusionamos** dentro del campo `calle`.
    *   *Input:* Calle: "Mitre", Nro: "100", Piso: "1", Dpto: "A".
    *   *Storage:* Calle: "Mitre (Piso 1, Dpto A)", Nro: "100".
    
**Resultado:** El dato se guarda, el usuario lo ve, y la base de datos no sufre cambios estructurales riesgosos.

## 3. Correcciones Críticas Realizadas

### A. Backend: Return Type Mismatch
*   **Síntoma:** "Al guardar dirección, se borra de la lista y dice 'Falta Domicilio'".
*   **Causa:** La API devolvía el objeto **CLIENTE** completo tras guardar una dirección. El Frontend esperaba recibir solo el objeto **DOMICILIO**. Al intentar meter un "Cliente" en una lista de "Domicilios", la UI colapsaba.
*   **Fix:** Se ajustó `router.py` y `service.py` para devolver `DomicilioResponse` y el objeto `db_domicilio` específico.

### B. Frontend: Sincronización de UI (Ficha Cliente V5)
*   **Síntoma:** "Definir Domicilio Fiscal" seguía apareciendo aunque se marcara el check "Fiscal".
*   **Causa:** Desincronización entre el estado local (optimista) y la respuesta del servidor.
*   **Fix:** Se reactivó la recarga forzada del cliente (`await loadCliente(...)`) en `ClientCanvas.vue` tras cada guardado. Esto asegura que lo que ve el usuario es 100% fiel a la base de datos.

### C. Backend: Persistencia de Flag Fiscal
*   **Verificación:** Se creó un script de bajo nivel (`debug_fiscal.py`) que confirmó que el booleano `es_fiscal` se guarda correctamente en la base de datos SQLite.

## 4. Estado Final del Sistema

*   **Lista de Clientes:** ✅ Restaurada y veloz (Fix "Lazy Load").
*   **Carga de Domicilios:** ✅ Precisa. Soporta Piso/Depto (Fusionados en texto).
*   **Flag Fiscal:** ✅ Funcional y persistente.
*   **Estabilidad:** ✅ Backend operando sin errores de arranque (tras reinicio manual del proceso zombie).

---
**Firmado:** Antigravity Agent (Google Deepmind)  
**Protocolo:** OMEGA (Cierre y Documentación)
