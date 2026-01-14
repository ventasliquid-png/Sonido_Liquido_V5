# Informe Forense: Auditoría IOWA (Cloud SQL)
**Fecha:** 11 de Diciembre de 2025
**Objetivo:** Evaluar estado y contenido de la instancia `v5-crisol-micro`.
**Endpoint:** `104.197.57.226` (PostgreSQL)

## 1. Estado de Conexión
*   **Status:** ✅ ONLINE y Accesible.
*   **Latencia:** Aceptable para operaciones administrativas.
*   **Seguridad:** Accesible con credenciales hardcodeadas de desarrollo.

## 2. Inventario de Datos (Snapshot)
La base de datos contiene una estructura de tablas completa (V5 Schema) pero con **datos de desarrollo/test**.

| Tabla Principal | Cantidad | Observación |
| :--- | :--- | :--- |
| `clientes` | 11 | Datos de prueba (Seguramente "Cliente Uno", etc.) |
| `productos` | 60 | Base de productos inicial o de prueba. |
| `rubros` | 22 | Estructura de categorías básica. |
| `domicilios` | 16 | Vinculados a los clientes de prueba. |
| `usuarios` | 1 | Probablemente `admin`. |

**Tablas Maestras (Infraestructura):**
*   `provincias`: 24 (Completo)
*   `condiciones_iva`: 4 (Básico)
*   `unidades`: 10 (Kg, Lt, Un, etc.)
*   `tasas_iva`: 8

**Vectores de IA:**
*   `langchain_pg_embedding`: 14 registros. (La "memoria" de la IA en la nube es incipiente).

## 3. Diagnóstico de Compatibilidad
*   **Schema:** Coincide con la arquitectura V5 actual (vemos tablas nuevas como `productos_costos`, `nodos_transporte`).
*   **Conclusión:** La base está "sembrada" pero no operativa comercialmente. Es el destino perfecto para una **migración limpia**.

## 4. Recomendación Estratégica
Dado que el **Piloto (SQLite)** ahora tiene los datos "Limpios y Reales" y **IOWA (Cloud)** tiene datos "Viejos y de Juguete":

1.  **Tabula Rasa:** Truncar (limpiar) las tablas transaccionales de IOWA (`clientes`, `productos`, `pedidos`).
2.  **La Gran Migración:** Desarrollar un script `migrate_pilot_to_cloud.py` que lea de `produccion.db` e inserte en `104.197.57.226`.
3.  **Deploy:** Cambiar la configuración de V5 para que `DATABASE_URL` apunte a la nube.

> [!WARNING]
> **Precaución:** Los 14 recuerdos de IA en la nube podrían perderse si no se backupean, aunque parecen ser de pruebas de desarrollo.
