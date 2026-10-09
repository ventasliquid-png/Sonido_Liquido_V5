# [IDENTIDAD] - backend\logistica\service.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

# backend/logistica/service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from backend.logistica import models, schemas
from backend.contactos.models import Vinculo, Persona # [V6 Multiplex]

class LogisticaService:
    # --- EmpresaTransporte ---
    @staticmethod
    def create_empresa(db: Session, empresa_in: schemas.EmpresaTransporteCreate) -> models.EmpresaTransporte:
        # Check for existing empresa with same name (case insensitive)
        existing = db.query(models.EmpresaTransporte).filter(
            models.EmpresaTransporte.nombre.ilike(empresa_in.nombre)
        ).first()
        
        if existing:
            # Bit 1 (Value 2): ACTIVE
            is_active = (existing.flags_estado & 2) == 2
            status_msg = "activa" if is_active else "inactiva"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una empresa de transporte con el nombre '{existing.nombre}' ({status_msg})."
            )

        db_empresa = models.EmpresaTransporte(**empresa_in.model_dump())
        db.add(db_empresa)
        db.commit()
        db.refresh(db_empresa)
        
        return db_empresa

    @staticmethod
    def get_empresas(db: Session, status: str = "active") -> List[models.EmpresaTransporte]:
        query = db.query(models.EmpresaTransporte)
        if status == "active":
            # Usar bitwise para ACTIVE (Bit 1 = 2)
            query = query.filter(models.EmpresaTransporte.flags_estado.op('&')(2) == 2)
        elif status == "inactive":
            query = query.filter(models.EmpresaTransporte.flags_estado.op('&')(2) == 0)
        # If "all", no filter applied
        return query.all()

    @staticmethod
    def get_empresa(db: Session, empresa_id: UUID) -> Optional[models.EmpresaTransporte]:
        empresa = db.query(models.EmpresaTransporte).options(
            joinedload(models.EmpresaTransporte.vinculos).joinedload(Vinculo.persona)
        ).filter(models.EmpresaTransporte.id == empresa_id).first()

        if empresa:
            # Flatten contacts for the response
            empresa.vinculos_detalles = []
            for v in empresa.vinculos:
                # Find labor email/phone in canales_laborales
                email = next((c['valor'] for c in (v.canales_laborales or []) if c.get('tipo') == 'EMAIL'), None)
                tel = next((c['valor'] for c in (v.canales_laborales or []) if c.get('tipo') == 'TEL_ESCRITORIO' or c.get('tipo') == 'TELEFONO'), None)
                
                empresa.vinculos_detalles.append({
                    "id": v.id,
                    "persona_id": v.persona_id,
                    "nombre": f"{v.persona.nombre} {v.persona.apellido}".strip() if v.persona else "Sin Nombre",
                    "email": email,
                    "telefono": tel,
                    "es_principal": False, # TODO: Add principal flag in V6 if needed
                    "tipo_contacto_id": v.tipo_contacto_id,
                    "rol": v.rol
                })
            
            # Use a different attribute name to avoid overwriting the ORM relationship
            empresa.vinculos_multiplex = empresa.vinculos_detalles 

        return empresa

    @staticmethod
    def update_empresa(db: Session, empresa_id: UUID, empresa_in: schemas.EmpresaTransporteUpdate) -> Optional[models.EmpresaTransporte]:
        db_empresa = LogisticaService.get_empresa(db, empresa_id)
        if not db_empresa:
            return None
        
        update_data = empresa_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_empresa, key, value)
        
        db.add(db_empresa)
        db.commit()
        db.refresh(db_empresa)
        
        # [V5] El vínculo con el Address Hub es gestionado directamente 
        # desde la UI a través de VinculoGeografico. El servicio ya no 
        # realiza sincronización manual de campos legacy.
        
        return db_empresa

    # --- Domicilios de la empresa (Address Hub: Domicilio + VinculoGeografico 'TRANSPORTE') [S883, Card #170] ---
    _CAMPOS_DOMICILIO = ("alias", "calle", "numero", "piso", "depto", "cp", "localidad", "provincia_id", "calle_entrega", "numero_entrega", "piso_entrega",
                         "depto_entrega", "cp_entrega", "localidad_entrega", "provincia_entrega_id", "maps_link", "notas_logistica", "observaciones")

    @staticmethod
    def _chequear_provincias(db: Session, datos: dict):
        from sqlalchemy import text
        for campo in ("provincia_id", "provincia_entrega_id"):
            v = datos.get(campo)
            if v and not db.execute(text("SELECT 1 FROM provincias WHERE id = :i"), {"i": v}).first():
                raise HTTPException(status_code=400, detail=f"PROVINCIA_INEXISTENTE: no existe la provincia '{v}'.")

    @staticmethod
    def _vinculo_domicilio(db: Session, empresa_id: UUID, domicilio_id: UUID):
        from backend.contactos.models import VinculoGeografico
        return db.query(VinculoGeografico).filter(
            VinculoGeografico.entidad_tipo == 'TRANSPORTE', VinculoGeografico.entidad_id == empresa_id,
            VinculoGeografico.domicilio_id == domicilio_id).first()

    @staticmethod
    def _un_solo_fiscal(db: Session, empresa_id: UUID, excepto_domicilio_id):
        """Un solo domicilio fiscal por empresa: los otros pierden el bit FISCAL (1) del vínculo y la marca es_fiscal del domicilio."""
        from backend.contactos.models import VinculoGeografico
        from backend.clientes.models import Domicilio
        for vg in db.query(VinculoGeografico).filter(VinculoGeografico.entidad_tipo == 'TRANSPORTE', VinculoGeografico.entidad_id == empresa_id,
                                                      VinculoGeografico.domicilio_id != excepto_domicilio_id).all():
            if vg.flags_relacion & 1:
                vg.flags_relacion = vg.flags_relacion & ~1
                dom = db.query(Domicilio).filter(Domicilio.id == vg.domicilio_id).first()
                if dom is not None:
                    dom.es_fiscal = False

    @staticmethod
    def create_domicilio_empresa(db: Session, empresa_id: UUID, data: schemas.DomicilioEmpresaWrite):
        from backend.contactos.models import VinculoGeografico
        from backend.clientes.models import Domicilio
        if not LogisticaService.get_empresa(db, empresa_id):
            raise HTTPException(status_code=404, detail="Empresa de transporte no encontrada")
        datos = data.model_dump(exclude_unset=True)
        if not (datos.get("calle") or "").strip():
            raise HTTPException(status_code=400, detail="CALLE_REQUERIDA: cargá al menos la calle del domicilio.")
        LogisticaService._chequear_provincias(db, datos)
        es_fiscal, es_entrega = bool(datos.get("es_fiscal")), datos.get("es_entrega")
        if not es_fiscal and es_entrega is None:
            es_entrega = True                       # sin indicación: sede de entrega, como los nodos
        activo = datos.get("activo") is not False
        try:
            dom = Domicilio(activo=activo, is_active=activo, es_fiscal=es_fiscal, es_entrega=bool(es_entrega),
                            **{c: datos[c] for c in LogisticaService._CAMPOS_DOMICILIO if c in datos})
            db.add(dom)
            db.flush()
            if es_fiscal:
                LogisticaService._un_solo_fiscal(db, empresa_id, dom.id)
            vg = VinculoGeografico(entidad_tipo='TRANSPORTE', entidad_id=empresa_id, domicilio_id=dom.id, alias=datos.get("alias"),
                                   flags_relacion=(1 if es_fiscal else 0) | (2 if es_entrega else 0), activo=activo)
            db.add(vg)
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(vg)
        return vg

    @staticmethod
    def update_domicilio_empresa(db: Session, empresa_id: UUID, domicilio_id: UUID, data: schemas.DomicilioEmpresaWrite):
        from backend.clientes.models import Domicilio
        vg = LogisticaService._vinculo_domicilio(db, empresa_id, domicilio_id)
        dom = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first() if vg else None
        if vg is None or dom is None:
            raise HTTPException(status_code=404, detail="Domicilio no encontrado para esta empresa de transporte")
        datos = data.model_dump(exclude_unset=True)
        if "calle" in datos and not (datos["calle"] or "").strip():
            raise HTTPException(status_code=400, detail="CALLE_REQUERIDA: el domicilio no puede quedar sin calle.")
        LogisticaService._chequear_provincias(db, datos)
        try:
            for c in LogisticaService._CAMPOS_DOMICILIO:
                if c in datos:
                    setattr(dom, c, datos[c])
            if "alias" in datos:
                vg.alias = datos["alias"]
            flags = vg.flags_relacion or 0
            if datos.get("es_fiscal") is True:
                LogisticaService._un_solo_fiscal(db, empresa_id, dom.id)
            if datos.get("es_fiscal") is not None:
                flags = (flags | 1) if datos["es_fiscal"] else (flags & ~1)
                dom.es_fiscal = bool(datos["es_fiscal"])
            if datos.get("es_entrega") is not None:
                flags = (flags | 2) if datos["es_entrega"] else (flags & ~2)
                dom.es_entrega = bool(datos["es_entrega"])
            vg.flags_relacion = flags
            if datos.get("activo") is not None:
                vg.activo = dom.activo = dom.is_active = bool(datos["activo"])
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(vg)
        return vg

    @staticmethod
    def delete_domicilio_empresa(db: Session, empresa_id: UUID, domicilio_id: UUID):
        """Baja LÓGICA (se puede volver atrás con PUT activo=true): ni el domicilio ni el vínculo se borran."""
        from backend.clientes.models import Domicilio
        vg = LogisticaService._vinculo_domicilio(db, empresa_id, domicilio_id)
        dom = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first() if vg else None
        if vg is None or dom is None:
            raise HTTPException(status_code=404, detail="Domicilio no encontrado para esta empresa de transporte")
        vg.activo = False
        dom.activo = False
        dom.is_active = False
        db.commit()
        db.refresh(vg)
        return vg

    @staticmethod
    def hard_delete_empresa(db: Session, empresa_id: UUID) -> Optional[models.EmpresaTransporte]:
        """Hard delete. Raises IntegrityError if it has related records."""
        from sqlalchemy.exc import IntegrityError
        db_empresa = LogisticaService.get_empresa(db, empresa_id)
        if not db_empresa:
            return None
        
        try:
            db.delete(db_empresa)
            db.commit()
            return db_empresa
        except IntegrityError as e:
            db.rollback()
            raise e

    # --- NodoTransporte ---
    @staticmethod
    def create_nodo(db: Session, nodo_in: schemas.NodoTransporteCreate) -> models.NodoTransporte:
        # Validar que la empresa exista
        empresa = LogisticaService.get_empresa(db, nodo_in.empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa de transporte no encontrada")

        db_nodo = models.NodoTransporte(**nodo_in.model_dump())
        db.add(db_nodo)
        db.commit()
        db.refresh(db_nodo)
        
        # [VAULT SYNC] Register Nodo Address
        from backend.clientes.models import Domicilio
        from backend.contactos.models import VinculoGeografico
        
        if db_nodo.direccion_completa:
            dom = Domicilio(calle=db_nodo.direccion_completa, localidad=db_nodo.localidad or 'S/D', provincia_id=db_nodo.provincia_id, activo=True)
            db.add(dom)
            db.flush()
            vg = VinculoGeografico(entidad_tipo='NODO_TRANSPORTE', entidad_id=db_nodo.id, domicilio_id=dom.id, alias=db_nodo.nombre_nodo, flags_relacion=2, activo=True)
            db.add(vg)
            db.commit()
            
        return db_nodo

    @staticmethod
    def get_nodos(db: Session, empresa_id: Optional[UUID] = None) -> List[models.NodoTransporte]:
        query = db.query(models.NodoTransporte)
        if empresa_id:
            query = query.filter(models.NodoTransporte.empresa_id == empresa_id)
        return query.all()

    @staticmethod
    def get_nodo(db: Session, nodo_id: UUID) -> Optional[models.NodoTransporte]:
        return db.query(models.NodoTransporte).filter(models.NodoTransporte.id == nodo_id).first()

    @staticmethod
    def update_nodo(db: Session, nodo_id: UUID, nodo_in: schemas.NodoTransporteUpdate) -> Optional[models.NodoTransporte]:
        db_nodo = LogisticaService.get_nodo(db, nodo_id)
        if not db_nodo:
            return None
        
        update_data = nodo_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_nodo, key, value)
        
        db.add(db_nodo)
        db.commit()
        db.refresh(db_nodo)
        
        # [VAULT SYNC] Sync changes
        from backend.contactos.models import VinculoGeografico
        from backend.clientes.models import Domicilio
        
        if 'direccion_completa' in update_data:
            vg = db.query(VinculoGeografico).filter(VinculoGeografico.entidad_tipo == 'NODO_TRANSPORTE', VinculoGeografico.entidad_id == db_nodo.id).first()
            if vg and vg.domicilio:
                vg.domicilio.calle = db_nodo.direccion_completa
                db.add(vg.domicilio)
            elif db_nodo.direccion_completa:
                dom = Domicilio(calle=db_nodo.direccion_completa, localidad=db_nodo.localidad or 'S/D', provincia_id=db_nodo.provincia_id, activo=True)
                db.add(dom)
                db.flush()
                vg = VinculoGeografico(entidad_tipo='NODO_TRANSPORTE', entidad_id=db_nodo.id, domicilio_id=dom.id, alias=db_nodo.nombre_nodo, flags_relacion=2, activo=True)
                db.add(vg)
                
        db.commit()
        return db_nodo

    @staticmethod
    def hard_delete_nodo(db: Session, nodo_id: UUID) -> Optional[models.NodoTransporte]:
        """Hard delete. Raises IntegrityError if it has related records."""
        from sqlalchemy.exc import IntegrityError
        db_nodo = LogisticaService.get_nodo(db, nodo_id)
        if not db_nodo:
            return None
        
        try:
            db.delete(db_nodo)
            db.commit()
            return db_nodo
        except IntegrityError as e:
            db.rollback()
            raise e
