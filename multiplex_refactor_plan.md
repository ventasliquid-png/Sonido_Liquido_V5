# Protocolo Multiplex: Reingeniería de Contactos (N:M)

## 1. Diseño de Esquema Propuesto

### Clase `Persona` (El Individuo)
Representa al ser humano único, independiente de sus roles comerciales.
```python
class Persona(Base):
    __tablename__ = "personas" # Antes 'contactos'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    
    # Datos Personales (Globales)
    # Estos viajan con la persona independientemente de dónde trabaje
    domicilio_personal = Column(String, nullable=True) 
    fecha_nacimiento = Column(Date, nullable=True)
    
    # Contacto Directo (Privado)
    canales_personales = Column(JSON, default=list) # Ej: WhatsApp Personal, Email Personal
    
    notas_globales = Column(Text, nullable=True) # "Le gusta el café", "Cumpleaños"
    
    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    vinculos = relationship("Vinculo", back_populates="persona")
```

### Clase `Vinculo` (El Rol / Sombrero)
La tabla de unión que contextualiza la relación entre una Persona y una Entidad.  
Soporta historial ("Trabajó en..."), múltiples roles actuales, y notas específicas.

```python
class Vinculo(Base):
    __tablename__ = "vinculos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    persona_id = Column(GUID(), ForeignKey("personas.id"), nullable=False, index=True)
    
    # Definición Polimórfica de la Entidad
    entidad_tipo = Column(Enum('CLIENTE', 'TRANSPORTE', 'PROVEEDOR', 'VENDEDOR', name='entidad_tipo_enum'), nullable=False)
    entidad_id = Column(GUID(), nullable=False, index=True) # ID genérico (UUID)
    
    # Detalles del Rol
    puesto = Column(String, nullable=True) # Ej: "Jefe de Taller"
    area = Column(String, nullable=True) # Ej: "Logística"
    roles = Column(JSON, default=list) # Tags: ["COMPRAS", "FIRMA_CHEQUES"]
    
    # Canales Laborales (Contextuales)
    # Ej: El email corporativo @empresa.com o el interno
    canales_laborales = Column(JSON, default=list) 
    
    notas_vinculo = Column(Text, nullable=True) # "Llamar solo por la mañana", "Clave de acceso"
    
    # Estrategia Temporal (Historial)
    activo = Column(Boolean, default=True)
    fecha_inicio = Column(Date, default=datetime.utcnow)
    fecha_fin = Column(Date, nullable=True) # Si activo=False, esto debe tener valor
    
    # Relaciones
    persona = relationship("Persona", back_populates="vinculos")
```

---

## 2. Roadmap de Ejecución (3 Sesiones)

### 📌 Sesión 1: Cimientos (Modelos y Migración)
**Objetivo:** Establecer la estructura DB.
1.  **Refactor Models**: Crear `backend/contactos/models.py` con `Persona` y `Vinculo`.
2.  **Migration Script**: Script de conversión `contactos` -> `personas` + `vinculos`.
3.  **Sanity Check**: Verificar integridad referencial.

### 📌 Sesión 2: Lógica de Negocio (El Cerebro)
**Objetivo:** Adaptar API Service Layer.
1.  **Schemas**: `PersonaRead` con `vinculos` anidados.
2.  **Service Refactor**: 
    - `get_contactos`: Join implícito (Vinculo -> Persona).
    * `create_contacto`: Lógica "Upsert" (Crear persona si no existe, agregar vínculo).

### 📌 Sesión 3: Frontend (La Interfaz)
**Objetivo:** UI Gestor de Relaciones.
1.  **ContactCanvas**: Layout "Profile + Cards".
2.  **Multilink UI**: Permitir agregar múltiples cards de vínculo.
3.  **Smart Search**: Buscar persona existente antes de crear.

---

## Preguntas Clave
1.  ¿Separamos `canales_personales` (celular propio) de `canales_laborales`? (Recomendado: SÍ).
2.  ¿`entidad_id` como UUID genérico sin FK constraint dura? (Recomendado para polimorfismo simple).
