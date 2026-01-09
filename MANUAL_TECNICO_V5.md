# 📘 MANUAL TÉCNICO V5: "CIMIENTOS DE ACERO"
**Versión:** 1.0 (Ene 2026)
**Estado:** VIVO

---

## 🔮 FUTURO: MIGRACIÓN A SQL SERVER (PROYECCIÓN TÉCNICA)

### Cambio de Paradigma de Despliegue
Cuando el sistema migre a una base de datos centralizada (SQL Server), el modelo de instalación cambiará radicalmente:

1.  **El "Instalador" adelgaza:**
    - Ya NO contendrá el archivo `pilot.db`.
    - Solo transportará el código fuente (Frontend/Backend).

2.  **Gestión de Credenciales (.env):**
    - La variable `DATABASE_URL` dejará de apuntar a `sqlite:///pilot.db`.
    - Pasará a apuntar al servidor: `postgresql://user:pass@192.168.1.X:5432/sonido_v5`.
    - **Implicación:** Al instalar en una nueva máquina, solo se requerirá configurar este string de conexión una vez.

3.  **Actualizaciones (Update Mode):**
    - Serán mucho más seguras. Al no haber base de datos local, se puede sobrescribir toda la carpeta del sistema sin riesgo de borrar datos, ya que los datos viven en el servidor central.

---
**Documento Generado:** 2026-01-09 | **Versión:** V5.0 (Steel Core)
**Estado:** VIVO

---

## 🗺️ 1. MAPA DE ARCHIVOS CRÍTICOS

### 🛠️ Scripts Tácticos (Admin & Ops)
| Script | Ubicación | Función | Cuándo usar |
| :--- | :--- | :--- | :--- |
| **Push Session** | `scripts/push_session_to_iowa.py` | Sincroniza `pilot.db` (Local) -> IOWA (Nube). | Al cerrar sesión o tras cambios masivos en local. |
| **Force Init** | `scripts/force_init_schema.py` | Borra y recrea el esquema en IOWA. **Destructivo**. | Solo ante Schema Drift irrecuperable. |
| **Audit Counts** | `scripts/audit_counts.py` | Cuenta registros en `pilot.db`. | Protocolo ALFA/OMEGA. |
| **Check API** | `scripts/check_api_pedidos.py` | Verifica salud del endpoint de Pedidos. | Debugging de conectividad. |

### 🧠 Backend Core
| Archivo | Ubicación | Función |
| :--- | :--- | :--- |
| **Database** | `backend/core/database.py` | Configuración de SQLAlchemy. Implementa **Ruta Absoluta Dinámica** para `pilot.db`. |
| **Main** | `backend/main.py` | Punto de entrada FastAPI. Configura CORS y Routers. |

---

## 📚 2. DICCIONARIO DE DATOS (Entidades Core)

### 👤 Cliente (`clientes`)
| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | GUID | Sí | PK. Generado automáticamente. |
| `razon_social` | String | Sí | Nombre Fiscal. |
| `cuit` | String | Sí | Clave Fiscal (Sin guiones idealmente). |
| `condicion_iva_id` | GUID | Sí | FK a `condiciones_iva`. |
| `lista_precios_id` | GUID | Sí | FK a `listas_precios`. |
| `activo` | Boolean | Sí | Flag Lázaro (Soft Delete). |

### 📦 Producto (`productos`)
| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `sku` | String | Sí | Identificador único de negocio. |
| `nombre` | String | Sí | Descripción corta comercial. |
| `costo_std` | Float | No | Costo base para cálculos. |
| `rubro_id` | Integer | Sí | FK a `rubros` (Jerarquía de catálogo). |

---

## 🛡️ 3. REGLAS DE CONSISTENCIA (Business Logic)

1.  **Integridad Referencial Estricta:** No se puede crear un Pedido para un cliente inexistente o que no tenga `condicion_iva` válida.
2.  **Booleans en Postgres:** Postgres exige `TRUE/FALSE` (Native Boolean). SQLite usa `1/0`. El script de sincronización **DEBE sanitizar** estos valores explícitamente.
3.  **Provincias Legacy:** Los códigos de provincia pueden ser largos (ej: "CABA", "BA"). El campo `id` debe soportar `String(5)`.
4.  **Rutas Absolutas:** El backend siempre debe buscar la base de datos `pilot.db` en la **RAÍZ** del proyecto para evitar la creación de bases fantasmas en subdirectorios.

---

## 🔌 4. API CONTRACTS (Ejemplos JSON)

### POST `/pedidos/`
```json
{
  "cliente_id": "uuid-cliente",
  "items": [
    {
      "producto_id": 123,
      "cantidad": 10
    }
  ],
  "nota": "Pedido Urgente"
}
```

### GET `/pedidos/{id}`
Respuesta Esperada:
```json
{
  "id": 1,
  "cliente": { "razon_social": "GELATO SA" },
  "total": 15000.00,
  "estado": "PENDIENTE"
}
```
