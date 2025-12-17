# INFORME TÉCNICO DE AVANCE - SONIDO LÍQUIDO V5
**Fecha:** 17 de Diciembre de 2025
**Para:** Equipo de Arquitectura y Desarrollo
**Ref:** Sesiín de Mantenimiento de Datos y Conectividad LAN

---

## 1. Resumen Ejecutivo
Durante la sesión de la fecha se completaron hitos críticos para la operatividad del negocio, enfocándose en la higiene de datos (Data Hygiene) y la escalabilidad operativa (Multi-usuario). El sistema ha evolucionado de una instancia monolítica local a una arquitectura cliente-servidor habilitada para LAN.

## 2. Modificaciones Estructurales

### A. Arquitectura de Red (Modo LAN)
Se implementó el soporte para acceso concurrente dentro de la red local.
*   **Binding de IP:** Se modificó la configuración de `Uvicorn` (Backend) y `Vite` (Frontend) para escuchar en `0.0.0.0` en lugar de `localhost`.
*   **Firewall:** Se automatizó la apertura de los puertos TCP `8000` (API) y `5173` (SPA) en el host servidor.
*   **Resolución de Nombres:** Para mitigar problemas de DNS local y variables de entorno en Windows, se forzó la inyección de la IP del servidor (`192.168.0.34`) en el cliente, garantizando conectividad inmediata.

### B. Gestión de Integridad de Datos
Se desarrollaron mecanismos de seguridad para permitir la depuración masiva sin comprometer la consistencia relacional.
*   **Hard Delete Controlado:** 
    *   Implementación de endpoint `DELETE .../hard` con validación de integridad referencial (`SQLAlchemy IntegrityError`).
    *   **Política:** El sistema bloquea físicamente la eliminación de cualquier entidad (Producto/Cliente) que posea historial transaccional (Ventas/Pedidos), previniendo orfandad de registros.
*   **Sanitización de Inputs:**
    *   Se reforzaron los esquemas Pydantic (`schemas.py`) para normalizar identificadores tributarios (CUIT).
    *   El sistema ahora acepta entradas "sucias" (con guiones/espacios) y las almacena canónicamente (solo dígitos), mejorando la calidad de los datos para futuras integraciones (AFIP/ARBA).

## 3. Entregables Operativos

1.  **Script de Lanzamiento (`run_lan.ps1`):** Automatización _One-Click_ que detecta el entorno, configura las variables de entorno y despliega la pila tecnológica completa (Backend + Frontend).
2.  **Protocolo de Depuración:** Se definió y documentó el flujo de trabajo para la limpieza de la base de datos:
    *   *Fase 1:* Desactivación Lógica (Bulk Soft-Delete).
    *   *Fase 2:* Eliminación Física (Bulk Hard-Delete en inactivos).

## 4. Estado del Código
El repositorio `ventasliquid-png/Sonido_Liquido_V5` en GitHub (Branch `main`) se encuentra actualizado y sincronizado con el entorno de producción local.
*   **Hash:** (Último commit del día).
*   **Status:** Stable / Deployment Ready.

---
**Firma:**
Antigravity Agent (Google Deepmind)
*Asistente Técnico Principal*
