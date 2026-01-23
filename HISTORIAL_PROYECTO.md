# HISTORIAL DEL PROYECTO ("MEMORIA ELEFANTE")

Archivo sagrado de hitos y batallas. Solo crece, nunca se borra.

## 📅 La Batalla del Domingo (19/01/2026 Ref del usuario, trabajo del 18/01)

Impacto Consolidado:
*   **Ventana Satélite**: Implementación exitosa de la ventana modal/overlay para operaciones rápidas sin perder contexto, funcional a 1700px.
*   **Layout Tokyo**: Refactorización del `PedidoCanvas` hacia un diseño de alta densidad ("Tokyo"), optimizando el espacio visual para carga intensiva de datos.
*   **Fix Teleport**: Corrección de problemas de renderizado y proyección de componentes (Teleport) que causaban artefactos visuales o errores de contexto.

### 📊 Estado de Datos (Snapshot)
*   **Clientes:** 11
*   **Pedidos:** 5
*   **Productos:** 14


---
*Fin del reporte del domingo.*

## 📅 La Recuperación del Jueves (22/01/2026) - Protocolo Omega V5.4 Beta

### 🛡️ Estabilización de Arquitectura Backend
Se erradicó el "Error 500" masivo unificando el espacio de nombres de Python.
*   **Problema:** Colisión de metadatos en SQLAlchemy por doble importación (`clientes` vs `backend.clientes`).
*   **Solución:** Normalización estricta a prefijo `backend.` en todos los módulos y limpieza de `sys.path`.

### 🎹 Fix de Usabilidad F10
*   **Problema:** Presionar F10 en un modal cerraba toda la pantalla.
*   **Solución:** Aislamiento del evento (`stopImmediatePropagation`) en componentes hijos.

### 📦 Entregables
*   **Rama:** `v5.4-beta-fix`
*   **Estado:** Sistema operativo y listo para pruebas de carga.
