
# Archivo: backend/contactos/service.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from backend.contactos import models, schemas
from backend.contactos.models import Persona, Vinculo

def get_contactos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    cliente_id: Optional[UUID] = None, 
    transporte_id: Optional[UUID] = None,
    q: Optional[str] = None
) -> List[Persona]:
    
    query = db.query(Persona).options(joinedload(Persona.vinculos))

    # Filtros por Entidad (A través de Vinculo)
    if cliente_id:
        query = query.join(Vinculo).filter(
            Vinculo.entidad_tipo == 'CLIENTE',
            Vinculo.entidad_id == cliente_id,
            Vinculo.activo == True 
        )
    elif transporte_id:
        query = query.join(Vinculo).filter(
            Vinculo.entidad_tipo == 'TRANSPORTE',
            Vinculo.entidad_id == transporte_id,
            Vinculo.activo == True
        )
    
    # Buscador texto (Global)
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Persona.nombre.ilike(search),
                Persona.apellido.ilike(search),
                Persona.canales_personales.cast(models.String).ilike(search)
            )
        )
        
    # Ordenar por nombre
    query = query.order_by(Persona.nombre.asc())
    
    return query.offset(skip).limit(limit).all()

def get_contacto(db: Session, contacto_id: UUID) -> Optional[Persona]:
    return db.query(Persona).filter(Persona.id == contacto_id).options(joinedload(Persona.vinculos)).first()

def create_contacto(db: Session, contacto_in: schemas.ContactoCreate) -> Persona:
    # 1. Crear Persona
    canales_data = [c.model_dump() for c in contacto_in.canales] if contacto_in.canales else []

    persona = Persona(
        nombre=contacto_in.nombre,
        apellido=contacto_in.apellido,
        domicilio_personal=contacto_in.domicilio_personal,
        notas_globales=contacto_in.notas, 
        canales_personales=[]
    )
    db.add(persona)
    db.flush() 

    # 2. Determinar Entidad y Crear Vinculo
    entidad_tipo = None
    entidad_id = None
    
    if contacto_in.cliente_id:
        entidad_tipo = 'CLIENTE'
        entidad_id = contacto_in.cliente_id
    elif contacto_in.transporte_id:
        entidad_tipo = 'TRANSPORTE'
        entidad_id = contacto_in.transporte_id
        
    if entidad_tipo:
        vinculo = Vinculo(
            persona_id=persona.id,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            tipo_contacto_id=contacto_in.tipo_contacto_id, 
            rol=contacto_in.puesto, 
            roles=contacto_in.roles, 
            canales_laborales=canales_data, 
            notas_vinculo=f"Origen: {contacto_in.referencia_origen}" if contacto_in.referencia_origen else None,
            activo=contacto_in.estado
        )
        db.add(vinculo)
    
    db.commit()
    db.refresh(persona)
    return persona

def update_contacto(db: Session, contacto_id: UUID, contacto_in: schemas.ContactoUpdate) -> Optional[Persona]:
    persona = get_contacto(db, contacto_id)
    if not persona:
        return None
        
    # Update Fields Persona
    if contacto_in.nombre is not None: persona.nombre = contacto_in.nombre
    if contacto_in.apellido is not None: persona.apellido = contacto_in.apellido
    if contacto_in.domicilio_personal is not None: persona.domicilio_personal = contacto_in.domicilio_personal
    if contacto_in.notas is not None: persona.notas_globales = contacto_in.notas
    
    # Update Vinculo Principal
    target_vinculo = None
    target_tipo = None
    target_id = None
    
    if contacto_in.cliente_id:
        target_tipo = 'CLIENTE'
        target_id = contacto_in.cliente_id
    elif contacto_in.transporte_id:
        target_tipo = 'TRANSPORTE'
        target_id = contacto_in.transporte_id
        
    if target_tipo and target_id:
        target_vinculo = next((v for v in persona.vinculos if v.entidad_tipo == target_tipo and str(v.entidad_id) == str(target_id)), None)
        
        if target_vinculo:
            if contacto_in.puesto is not None: target_vinculo.rol = contacto_in.puesto
            if contacto_in.tipo_contacto_id is not None: target_vinculo.tipo_contacto_id = contacto_in.tipo_contacto_id 
            if contacto_in.roles is not None: target_vinculo.roles = contacto_in.roles
            if contacto_in.canales is not None: 
                target_vinculo.canales_laborales = [c.model_dump() for c in contacto_in.canales]
            if contacto_in.estado is not None: target_vinculo.activo = contacto_in.estado
    elif contacto_in.canales is not None:
        persona.canales_personales = [c.model_dump() for c in contacto_in.canales]
    
    db.commit()
    db.refresh(persona)
    return persona

def add_vinculo(db: Session, contacto_id: UUID, vinculo_in: schemas.ContactoCreate) -> Optional[Vinculo]:
    persona = get_contacto(db, contacto_id)
    if not persona:
        return None
        
    entidad_tipo = None
    entidad_id = None
    
    if vinculo_in.cliente_id:
        entidad_tipo = 'CLIENTE'
        entidad_id = vinculo_in.cliente_id
    elif vinculo_in.transporte_id:
        entidad_tipo = 'TRANSPORTE'
        entidad_id = vinculo_in.transporte_id
        
    if not entidad_tipo:
        return None 
        
    existe = db.query(Vinculo).filter(
        Vinculo.persona_id == persona.id,
        Vinculo.entidad_tipo == entidad_tipo,
        Vinculo.entidad_id == entidad_id,
        Vinculo.activo == True
    ).first()
    
    if existe:
        return existe
    
    canales_data = [c.model_dump() for c in vinculo_in.canales] if vinculo_in.canales else []

    vinculo = Vinculo(
        persona_id=persona.id,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        tipo_contacto_id=vinculo_in.tipo_contacto_id, 
        rol=vinculo_in.puesto, # Use puesto payload
        roles=vinculo_in.roles,
        canales_laborales=canales_data,
        notas_vinculo=vinculo_in.referencia_origen,
        activo=True
    )
    db.add(vinculo)
    db.commit()
    db.refresh(persona) 
    return vinculo

def delete_vinculo(db: Session, contacto_id: UUID, vinculo_id: UUID) -> bool:
    vinculo = db.query(Vinculo).filter(Vinculo.id == vinculo_id, Vinculo.persona_id == contacto_id).first()
    if not vinculo:
        return False
    
    db.delete(vinculo)
    db.commit()
    return True

def update_vinculo(db: Session, contacto_id: UUID, vinculo_id: UUID, vinculo_in: schemas.VinculoUpdate) -> Optional[Vinculo]:
    """
    Actualiza un vínculo específico (Rol, Activo, etc.)
    """
    vinculo = db.query(Vinculo).filter(Vinculo.id == vinculo_id, Vinculo.persona_id == contacto_id).first()
    if not vinculo:
        return None
        
    if vinculo_in.tipo_contacto_id is not None:
        vinculo.tipo_contacto_id = vinculo_in.tipo_contacto_id
        
    if vinculo_in.rol is not None:
        print(f"DEBUG: Updating Rol Text to '{vinculo_in.rol}' (ID: {vinculo_in.tipo_contacto_id})")
        vinculo.rol = vinculo_in.rol
    else:
        print(f"DEBUG: Rol Text received as None (ID: {vinculo_in.tipo_contacto_id})")
        
    if vinculo_in.activo is not None:
        vinculo.activo = vinculo_in.activo
        
    # TODO: Support updating canales_laborales here if needed
    
    db.commit()
    db.refresh(vinculo)
    return vinculo
