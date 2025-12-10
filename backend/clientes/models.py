# Archivo: backend/clientes/models.py
# Módulo Clientes (V5) - Implementación Jerárquica (Nike S)

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text, DateTime, Integer, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.core.database import Base
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Provincia
# Nota: Importamos Usuario como string o condicionalmente si hay riesgo de ciclo, 
# pero Maestros son seguros.

class Cliente(Base):
    """
    Tabla 'clientes' (La Cuenta).
    Representa la entidad comercial principal.
    """
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    razon_social = Column(String, nullable=False, index=True)
    nombre_fantasia = Column(String, nullable=True)
    cuit = Column(String, unique=False, nullable=False, index=True)
    
    # Identificadores
    codigo_interno = Column(Integer, Sequence("clientes_codigo_interno_seq", start=1000), nullable=True)
    legacy_id_bas = Column(String, nullable=True) # ID del sistema BAS anterior

    # Comunicación y Pagos
    whatsapp_empresa = Column(String, nullable=True)
    web_portal_pagos = Column(String, nullable=True)
    datos_acceso_pagos = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Referencias a otras tablas
    condicion_iva_id = Column(UUID(as_uuid=True), ForeignKey("condiciones_iva.id"), nullable=True)
    lista_precios_id = Column(UUID(as_uuid=True), ForeignKey("listas_precios.id"), nullable=True)
    segmento_id = Column(UUID(as_uuid=True), ForeignKey("segmentos.id"), nullable=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Account Manager
    
    # Datos financieros
    saldo_actual = Column(Numeric(18, 2), default=0.00)
    
    # Protocolo Lázaro
    activo = Column(Boolean, default=True, nullable=False)
    requiere_auditoria = Column(Boolean, default=False)
    
    # Ranking de Uso (V5.2)
    contador_uso = Column(Integer, default=0)

    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    domicilios = relationship("Domicilio", back_populates="cliente", cascade="all, delete-orphan")
    vinculos = relationship("backend.agenda.models.VinculoComercial", back_populates="cliente")
    condicion_iva = relationship(CondicionIva)
    lista_precios = relationship(ListaPrecios)
    segmento = relationship(Segmento)
    vendedor = relationship("backend.auth.models.Usuario")

    def __repr__(self):
        return f"<Cliente(razon_social='{self.razon_social}', cuit='{self.cuit}')>"

    # --- Propiedades UI (V5.1) ---
    @property
    def domicilio_fiscal_resumen(self):
        """Retorna string direccion fiscal o None"""
        fiscal = next((d for d in self.domicilios if d.es_fiscal and d.activo), None)
        if fiscal:
            numero = f" {fiscal.numero}" if fiscal.numero else ""
            localidad = f", {fiscal.localidad}" if fiscal.localidad else ""
            return f"{fiscal.calle}{numero}{localidad}"
        return None

    @property
    def tiene_entrega_alternativa(self):
        """Retorna True si tiene algun domicilio de entrega que NO sea el fiscal"""
        entregas = [d for d in self.domicilios if d.es_entrega and d.activo]
        fiscal = next((d for d in self.domicilios if d.es_fiscal and d.activo), None)
        
        if not entregas:
            return False
        
        # Si tiene entregas, verificamos si alguna es distinta a la fiscal
        if fiscal:
             # Si hay fiscal, buscamos alguna entrega que NO sea el mismo objeto/ID 
             # (Asumiendo que un domicilio puede ser ambos, o separados)
             # Logica: Si hay un domicilio 'es_fiscal=True' y 'es_entrega=False', y Otro 'es_entrega=True', entonces True.
             # Si el fiscal tamiben es entrega (es_fiscal=T, es_entrega=T), y es el unico, entonces False.
             
             # Buscamos si existe algun domicilio de entrega que NO sea el fiscal
             for e in entregas:
                 if e.id != fiscal.id:
                     return True
             return False
        else:
             # Si no hay fiscal definido pero hay entregas, tecnicamente es "alternativa" a nada? 
             # O consideramos que si hay entregas, hay punto de entrega.
             # El usuario quiere "punto naranja indque domicilio entrega distinto".
             # Asumamos: Distinto a Fiscal.
             # Si no hay fiscal, y hay entrega -> True (es distinto a null).
             return True

    @property
    def contacto_principal_nombre(self):
        """Retorna nombre del contacto principal o primero disponible"""
        principal = next((v for v in self.vinculos if v.es_principal and v.activo), None)
        if principal and principal.persona:
            return principal.persona.nombre_completo
        
        # Fallback: Primero activo
        primero = next((v for v in self.vinculos if v.activo), None)
        if primero and primero.persona:
            return primero.persona.nombre_completo
            
        return None


class Domicilio(Base):
    """
    Tabla 'domicilios' (Logística).
    Soporte multi-sucursal.
    """
    __tablename__ = "domicilios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    
    alias = Column(String, nullable=True) # "Depósito Norte"
    calle = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    cp = Column(String, nullable=True)
    localidad = Column(String, nullable=True)
    provincia_id = Column(String(1), ForeignKey("provincias.id"), nullable=True)
    
    # Flags de uso
    activo = Column(Boolean, default=True, nullable=False)
    es_fiscal = Column(Boolean, default=False)
    es_entrega = Column(Boolean, default=False)
    
    # Logística
    transporte_habitual_nodo_id = Column(UUID(as_uuid=True), ForeignKey("nodos_transporte.id"), nullable=True)
    transporte_id = Column(UUID(as_uuid=True), ForeignKey("empresas_transporte.id"), nullable=True)
    intermediario_id = Column(UUID(as_uuid=True), ForeignKey("empresas_transporte.id"), nullable=True)
    
    # Estrategia Logística (V5.2)
    metodo_entrega = Column(String, nullable=True) # RETIRO_LOCAL, TRANSPORTE, FLETE_MOTO, PLATAFORMA, DROPSHIPPING
    modalidad_envio = Column(String, nullable=True) # A_DOMICILIO, A_SUCURSAL
    origen_logistico = Column(String, nullable=True) # DESPACHO_NUESTRO, RETIRO_EN_PLANTA
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="domicilios")
    provincia = relationship(Provincia)
    transporte_habitual_nodo = relationship("backend.logistica.models.NodoTransporte")
    transporte = relationship("backend.logistica.models.EmpresaTransporte", foreign_keys=[transporte_id])
    intermediario = relationship("backend.logistica.models.EmpresaTransporte", foreign_keys=[intermediario_id])

    def __repr__(self):
        return f"<Domicilio(alias='{self.alias}', calle='{self.calle}')>"
