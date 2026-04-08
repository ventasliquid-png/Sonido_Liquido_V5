# 🏛️ INFORME DE TRANSICIÓN DE ARQUITECTURA: PROYECTO SONIDO LÍQUIDO V5

**PARA:** ARQUITECTA "NIKE P"
**DE:** AGENTE "ANTIGRAVITY" (SALIENTE)
**FECHA:** 30 de Enero, 2026
**ASUNTO:** ESTADO SITUACIONAL, DOCTRINA Y ARQUITECTURA DE DATOS (MULTIPLEX)

---

## 1. Misión y Contexto Operativo
El sistema **Sonido Líquido V5** es una plataforma ERP/CRM integral diseñada para la gestión logística y comercial de alta performance. Actualmente se encuentra en fase de **"Sea Trials" (Pruebas de Mar)**, operando con datos reales y en constante evolución.

**Estado Actual:** 🔥 **OPERATIVO / EN TRANSICIÓN N:M**
Acabamos de completar el **Protocolo Multiplex**, una refactorización nuclear del módulo de identidad para soportar relaciones N:M ("La Paradoja de Pedro"). El sistema es estable, pero requiere mano firme para cerrar la transición.

---

## 2. Doctrina Operativa (V5.5)
Para asegurar la supervivencia del sistema, debes adherirte estrictamente a los siguientes principios extraídos de la `DOCTRINA.md`:

1.  **Protocolo GIT (Seguridad):**
    *   Rama `main` **BLOQUEADA**. Prohibido commit directo.
    *   Todo cambio nace en `feature/...` o `fix/...`.
    *   Merge solo tras validación funcional (F5 Test).

2.  **Portabilidad (Logs e Idioma):**
    *   **ZERO EMOJIS** en logs de consola (Evitar crash CP1252 en Windows).
    *   Usar tags textuales: `[INFO]`, `[DB]`, `[ERROR]`.

3.  **Resiliencia (UX):**
    *   **Data-Race:** El Frontend debe manejar `null` en cargas asíncronas siempre.
    *   **Navaja de Occam:** Soluciones simples primero. "Wow Effect" es obligatorio, pero la estabilidad es reina.

---

## 3. Estado Situacional y Bitácora Reciente
Resumen de las últimas intervenciones críticas registradas en `BITACORA_DEV.md`:

*   **[2026-01-29] Fix Backend & Contact Canvas:** Se resolvió un Error 500 crítico en `/api/clientes` causado por propiedades computadas sin `joinedload`. Se repararon dropdowns invisibles en modo oscuro.
*   **[2026-01-28] Agenda Global:** Módulo de contactos 100% funcional. Se implementó la simetría ORM entre Clientes y Transportes.
*   **[2026-01-26] Protocolo Multiplex:** Se migró de un modelo 1:1 a N:M, permitiendo que una `Persona` tenga múltiples `Vinculos` con diferentes entidades (`Cliente`, `Transporte`).

---

## 4. Arquitectura de Datos (Los Registros)

Aquí reside la verdad del sistema. Conoce tus modelos:

### A. NÚCLEO CONTACTOS (V6 Multiplex) - `backend/contactos`
*El nuevo corazón del sistema de identidad.*

*   **`Persona`**: El ser humano único.
    *   `id`: UUID
    *   `nombre`, `apellido`: String
    *   `canales_personales`: JSON (Whatsapp personal, email personal).
    *   `notas_globales`: Text (Gustos, preferencias).
    
*   **`Vinculo`**: La relación comercial (La tarjeta de presentación).
    *   `id`: UUID
    *   `persona_id`: FK -> Persona
    *   `entidad_tipo`: ENUM ('CLIENTE', 'TRANSPORTE')
    *   `entidad_id`: UUID (Polimórfico)
    *   `rol`: String (Ej: "Jefe de Compras")
    *   `roles`: JSON (Tags: ["DECISOR", "COBRANZAS"])
    *   `canales_laborales`: JSON (Email corporativo, interno).
    *   `activo`: Bool (Switch de estado).

### B. COMERCIAL (V5) - `backend/clientes`
*   **`Cliente`**: La entidad legal/empresa.
    *   `razon_social`, `cuit`: Identidad fiscal.
    *   `estrategia_precio`: String (Motor de precios).
    *   `saldo_actual`: Numeric.
    *   `vinculos_rel`: Relación inversa polimórfica hacia `Vinculo`.
    *   `domicilios`: Relación 1:N con `Domicilio` (Fiscal/Entrega).

### C. LOGÍSTICA (V5) - `backend/logistica`
*   **`EmpresaTransporte`**: Proveedor logístico.
    *   `nombre`, `cuit`.
    *   `servicio_retiro_domicilio`: Bool.
    *   `vinculos_rel`: Relación inversa polimórfica hacia `Vinculo`.

### D. TRANSACCIONAL (V5) - `backend/pedidos`
*   **`Pedido`**: Orden de venta.
    *   `cliente_id`, `transporte_id`, `domicilio_entrega_id`.
    *   `estado`: String (PENDIENTE, CUMPLIDO...).
    *   `total`, `descuento_global_importe`.
*   **`PedidoItem`**: Línea de detalle.
    *   `producto_id`, `cantidad`, `precio_unitario`.

---

## 5. Mapa del Territorio (File Tree Escencial)

```text
c:\dev\Sonido_Liquido_V5\
├── backend/
│   ├── contactos/      # [NUCLEO V6] Service, Models, Router.
│   ├── clientes/       # Gestión de Empresas.
│   ├── logistica/      # Gestión de Transportes.
│   ├── core/           # Configuración DB (database.py).
│   └── ...
├── frontend/src/
│   ├── views/Agenda/components/ContactCanvas.vue # [UI CRITICA] Editor visual de contactos.
│   ├── stores/contactos.js # Store Pinia actualizado.
│   └── ...
├── scripts/
│   ├── test_qa_pedro.py        # [TEST] Validación Integración N:M.
│   ├── test_qa_edge_cases.py   # [TEST] Validación Robustez (Duplicados).
│   └── push_session_to_iowa.py # [SYNC] Respaldo a Nube.
├── NIKE_P_ONBOARDING.md # ESTE DOCUMENTO.
└── task.md             # Bitácora de tareas activas.
```

---

## 6. Instrucciones Finales para Nike P

1.  **Mantén la Estabilidad:** El sistema viene de una serie de *hotfixes*. No rompas lo que funciona ("Si no está roto, no lo arregles, pero hazlo bonito").
2.  **Vigila la "Paradoja de Pedro":** Los scripts de QA (`scripts/test_qa_*.py`) son tus amigos. Úsalos antes de cualquier cambio en el módulo de contactos.
3.  **Protocolo Omega:** Al finalizar tu sesión, debes ejecutar el cierre formal (Documentar, Commitear, Backup).

**CONFÍO EN TI. EL SISTEMA ES TUYO.**

*Fin del Informe.*
