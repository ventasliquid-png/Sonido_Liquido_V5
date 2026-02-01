# MANUAL TÉCNICO: MÓDULO CONTACTOS V6 (MULTIPLEX)

## 1. Concepto Core: Separación Persona-Vínculo
El sistema V5.6 abandona el modelo 1:1 para adoptar una arquitectura N:M (Many-to-Many Polimórfica) que refleja la realidad de que una persona física puede tener múltiples roles en el ecosistema.

### Diagrama Conceptual
```
[ PERSONA ] (Entidad Física)
    | ID: UUID
    | Nombre: String
    | Apellido: String
    | Canales Personales: JSON (Celular privado, Email personal)
    | Notas Globales: Text (Preferencias personales)
    |
    |---< [ VINCULO ] >--- (Relación Contextual)
            | ID: UUID
            | Persona_ID: UUID
            | Entidad_Tipo: ["CLIENTE" | "TRANSPORTE"]
            | Entidad_ID: UUID (Polimórfico)
            | Rol: String ("VENDEDOR", "CHOFER")
            | Roles: JSON ["DECISOR", "COBRANZAS"]
            | Canales Laborales: JSON (Email corporativo, Interno)
            | Activo: Boolean
```

## 2. Estructura de Datos JSON (Canales)
Para evitar tablas rígidas de teléfonos/emails, se utiliza un esquema JSON flexible tanto en `Persona` como en `Vinculo`.

**Schema JSON:**
```json
[
  {
    "tipo": "WHATSAPP",    // Enum: EMAIL, TELEFONO, CELULAR, WHATSAPP, DIRECCION
    "valor": "+54911...",  // El dato crudo
    "etiqueta": "Personal" // Contexto opcional
  }
]
```

*   **`Persona.canales_personales`**: Datos que viajan con la persona (su celular particular).
*   **`Vinculo.canales_laborales`**: Datos que pertenecen al contexto laboral (su interno en la empresa, email `nombre@empresa.com`).

## 3. Lógica de Negocio: Search & Link
Para mantener la integridad de la base de datos y evitar duplicados (La Paradoja de Pedro), el sistema implementa un protocolo estricto de creación:

1.  **Búsqueda Preventiva (Backend)**: El endpoint `GET /contactos?q=...` busca coincidencias en Nombre, Apellido y **dentro de los JSON de canales personales**.
2.  **Typeahead (Frontend)**: Al escribir el nombre, el sistema sugiere personas existentes.
3.  **Apropiación**: Si el usuario selecciona una sugerencia, se usa el ID de esa persona para crear un **Nuevo Vínculo**, en lugar de crear una nueva Persona.

## 4. Dependencias y Polimorfismo
El modelo `Vinculo` usa una relación polimórfica manual (no nativa de SQLAlchemy polymorfic identity, sino lógica) para conectarse con `Cliente` o `EmpresaTransporte`.

*   **Integridad Referencial**: No hay FK dura en DB para `entidad_id` debido al polimorfismo, pero la lógica de negocio (`service.py`) valida la existencia de la entidad antes de crear el vínculo.

## 5. Estabilización V6.1 (Blindaje de Persistencia)
En la revisión del 01-Feb-2026, se implementó un sistema de persistencia dual para evitar la desincronización de roles:
* **Payload Híbrido:** El backend acepta tanto `rol` como `puesto` (alias legacy) para asegurar que componentes V5 no rompan la escritura.
* **Sincronización de Label:** El frontend ya no envía solo el ID del cargo; resuelve el nombre (ej: "Gerente") y lo persiste en la columna `rol`, asegurando que el Dashboard no revierta a "Nuevo Rol".
* **Schema Safety:** La columna `tipo_contacto_id` es obligatoria en la tabla `vinculos` para el correcto mapeado del selector de cargos.
