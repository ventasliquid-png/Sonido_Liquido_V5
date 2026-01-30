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
