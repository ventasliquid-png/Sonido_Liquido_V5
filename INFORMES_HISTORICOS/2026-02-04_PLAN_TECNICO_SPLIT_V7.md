# 📋 PLAN TÉCNICO: PROTOCOLO SPLIT-VIEW Y SANEAMIENTO V7

**Fecha:** 2026-02-04
**Estado:** PENDIENTE DE EJECUCIÓN (PRIORIDAD ALFA)
**Autor:** Gy V14 (Bajo supervisión de Nike S)

## 1. Contexto y Objetivos
Se requiere una refactorización mayor del módulo de gestión de domicilios para "profesionalizar" la logística (V7).
*   **Problema:** Uso de "pipes" (`|`) para guardar piso/depto en un solo campo, falta de visualización clara entre Fiscal vs Entrega, y necesidad de soporte para Unidades de Negocio autónomas (Caso Nestlé).
*   **Solución:** Restitución de columnas nativas en DB, nueva UI "Split-View" 50/50, y lógica de negocio para CUITs duplicados.

---

## 2. Backend: Saneamiento de Base de Datos
**Archivo:** `backend/clientes/models.py`

### A. Schema Update (Tabla `domicilios`)
Abandonar hacks. Volver a la ortodoxia SQL.

```python
class Domicilio(Base):
    # ...
    # Restauración de campos físicos
    piso = Column(String, nullable=True)   # [NEW]
    depto = Column(String, nullable=True)  # [NEW]
    
    # Nuevas capacidades V7
    maps_link = Column(String, nullable=True) # URL o Coordenadas
    notas_logistica = Column(Text, nullable=True) # Instrucciones para chofer
    
    # Vinculación explícita con Staff (Caso Nestlé: "Llamar a Jorge")
    contacto_id = Column(Integer, nullable=True) # ID no foráneo estricto o link a Vinculo
```

### B. Migración (`scripts/migration_v7_domicilios.py`)
1.  **Add Columns:** Agregar `piso`, `depto`, `maps_link`, `notas_logistica`, `contacto_id`.
2.  **Data Rescue:** Iterar todos los domicilios. Si `calle` o `numero` contienen `|`, realizar `split()` y migrar datos a `piso`/`depto`. Limpiar campo original.

---

## 3. Frontend: Arquitectura Split-View
**Nueva Vista:** `src/views/Hawe/components/DomicilioSplitCanvas.vue`

### Diseño 50/50
*   **Trigger:** Click en tarjeta de domicilio en `ClienteInspector`.
*   **Lado Izquierdo (Fiscal):**
    *   Datos legales estrictos.
    *   Validación contra Padron AFIP (si aplica).
    *   Readonly sugerido si el usuario está editando Entrega, pero editable si se requiere corrección.
*   **Lado Derecho (Entrega - "La Verdad Logística"):**
    *   **Manda** sobre el fiscal para hoja de ruta.
    *   Inputs independientes para Piso/Depto.
    *   Campo Texto libre "Notas Logísticas".
    *   Selector de Contacto (Dropdown con iconos de staff).
    *   Botón "Copiar Fiscal" (Sync one-way).

### Componentes
*   Refactorizar `DomicilioForm.vue` para que sea "embeddable" (prop `embedded: Boolean`) sin su propio marco modal, o crear sub-componentes `DomicilioInputs.vue`.

---

## 4. Lógica de Negocio: Caso Nestlé (Unidades de Negocio)
**Problema:** Múltiples locales de una misma cadena (mismo CUIT) pero operan como clientes distintos.
**Solución:**
1.  **Backend:** Asegurar que `cuit` en `clientes` NO sea `unique`. (Confirmado: Es `index=True` pero `unique=False`).
2.  **Frontend (`ClienteInspector`):**
    *   Al detectar CUIT existente: Mostrar Advertencia "Este CUIT ya existe en X clientes".
    *   **Acción:** Permitir "Crear Nueva Unidad de Negocio" (botón explícito).
    *   Esto crea un `Cliente` nuevo (ID nuevo) con el mismo CUIT pero distinta "Razón Social Fantasía" o "Alias" y, crucialmente, su propio set de Domicilios y Contactos.

---

## 5. Ejecución (Para Mañana)
1.  Correr Script de Migración DB.
2.  Refactorizar Backend Models & Schemas.
3.  Crear `DomicilioSplitCanvas`.
4.  Conectar en `ClienteInspector`.
