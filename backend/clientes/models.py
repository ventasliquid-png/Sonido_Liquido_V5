# [IDENTIDAD] - backend\clientes\models.py
# Versión: V5.6 GOLD | Sincronización: 20260407130827
# ---------------------------------------------------------

# Archivo: backend/clientes/models.py
# Módulo Clientes (V5) - Implementación Jerárquica (Nike S)

import uuid
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text, DateTime, Integer, Sequence, JSON, BigInteger
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.core.database import Base, GUID
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Provincia
from backend.auth.models import Usuario # [GY-FIX-IMPORT] Explicit Import for Relationship
from backend.pedidos.models import Pedido # [AUDIT FIX] Resolve InvalidRequestError in Mapper initialization
from sqlalchemy.orm import foreign, remote

from sqlalchemy import Table

# --- [V5.2 GOLD] N:M Bridge ---
domicilios_clientes = Table(
    'domicilios_clientes',
    Base.metadata,
    Column('cliente_id', GUID(), ForeignKey('clientes.id'), primary_key=True),
    Column('domicilio_id', GUID(), ForeignKey('domicilios.id'), primary_key=True),
    Column('flags', BigInteger, default=2097152, nullable=False), # Default Bit 21 ON (Mirror)
    Column('alias', String, nullable=True),
    Column('es_predeterminado', Boolean, default=False),
    Column('created_at', DateTime, default=lambda: datetime.now(timezone.utc))
)

class Cliente(Base):
    """
    Tabla 'clientes' (La Cuenta).
    Representa la entidad comercial principal.
    """
    __tablename__ = "clientes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    # Identidad e Identificadores
    razon_social = Column(String, nullable=False, index=True)
    razon_social_canon = Column(String, unique=True, index=True, nullable=True)
    nombre_fantasia = Column(String, nullable=True)
    
    # [V5-X] Hybrid Architecture: CUIT is now nullable
    cuit = Column(String, unique=False, nullable=True, index=True)
    
    # [V5-X] The Anchor: Codigo Interno is the true reliable ID
    # Removed Sequence for SQLite compatibility, handled by Service
    codigo_interno = Column(Integer, unique=True, index=True, nullable=True)
    
    legacy_id_bas = Column(String, nullable=True) # ID del sistema BAS anterior

    # [GENOMA 64-bit] The 64 Flags (Bitmask)
    # Replaces 'activo' and other booleans over time
    flags_estado = Column(BigInteger, default=0, nullable=False)

    # Comunicación y Pagos
    whatsapp_empresa = Column(String, nullable=True)
    web_portal_pagos = Column(String, nullable=True)
    datos_acceso_pagos = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Referencias a otras tablas
    condicion_iva_id = Column(GUID(), ForeignKey("condiciones_iva.id"), nullable=True)
    lista_precios_id = Column(GUID(), ForeignKey("listas_precios.id"), nullable=True)
    segmento_id = Column(GUID(), ForeignKey("segmentos.id"), nullable=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Account Manager
    
    # [NEW V5.8] Inheritance: Favorite Transport
    transporte_habitual_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True)
    
    # Motor de Precios V5
    estrategia_precio = Column(String, default='MAYORISTA_FISCAL') # 'Sabor' del Cliente
    
    # Datos financieros
    saldo_actual = Column(Numeric(18, 2), default=0.00)
    
    # Protocolo Lázaro (Legacy Booleans - Deprecated but kept for compatibility)
    activo = Column(Boolean, default=True, nullable=False)
    requiere_auditoria = Column(Boolean, default=False)
    
    # Ranking de Uso (V5.2)
    contador_uso = Column(Integer, default=0)
    
    # Vector de Historial (V5.3 - Cache Denormalizado)
    # Guarda [{id, fecha, total, estado}, ...] (Max 5)
    historial_cache = Column(JSON, nullable=True, default=list)

    # --- Master Data Management (Protocolo Puente RAR-V5) ---
    # estado_arca: 'PENDIENTE', 'VALIDADO', 'CONFLICTO'
    estado_arca = Column(String, default='PENDIENTE', nullable=False) 
    datos_arca_last_update = Column(DateTime, nullable=True)
    # -------------------------------------------------------

    # Auditoría
    fecha_alta = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # Fecha de alta para negocio
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    # [V5.2 GOLD] Transition from 1:N to N:M
    domicilios = relationship("Domicilio", secondary=domicilios_clientes, back_populates="clientes")
    # [GY-FIX V6] Removed legacy VinculoComercial relationship
    # vinculos = relationship("VinculoComercial", back_populates="cliente", cascade="all, delete-orphan")
    # [V5.2 GOLD] Legacy 1:N relationship for transition phase
    domicilios_legacy = relationship("Domicilio", back_populates="cliente", foreign_keys="[Domicilio.cliente_id]", cascade="all, delete-orphan")
    
    condicion_iva = relationship(CondicionIva)
    lista_precios = relationship(ListaPrecios)
    segmento = relationship(Segmento)
    # [FIX] Importación diferida o string directo si el modelo está en Base
    vendedor = relationship("Usuario")
    # [FIX] Usar nombre corto 'Pedido' ya que está registrado en Base
    pedidos = relationship("Pedido", back_populates="cliente")
    # [NUEVO V6 Multiplex] Relación Polimórfica Inversa
    # Renombrado de vinculos_rel a vinculos para mantener compatibilidad de nombre
    vinculos = relationship(
        "Vinculo",
        primaryjoin="and_(foreign(Vinculo.entidad_id)==Cliente.id, Vinculo.entidad_tipo=='CLIENTE')",
        viewonly=True,
        overlaps="vinculos" 
    )
    
    transporte_habitual = relationship("EmpresaTransporte")

    # [V5 UNIVERSAL VAULT]
    vinculos_geograficos = relationship(
        "VinculoGeografico",
        primaryjoin="and_(foreign(VinculoGeografico.entidad_id)==Cliente.id, VinculoGeografico.entidad_tipo=='CLIENTE')",
        viewonly=True,
    )

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
            provincia = ""
            if fiscal.provincia:
                provincia = f" ({fiscal.provincia.nombre})"
            elif fiscal.provincia_id:
                provincia = f" ({fiscal.provincia_id})"
                
            return f"{fiscal.calle}{numero}{localidad}{provincia}"
        return None

    @property
    def requiere_entrega(self):
        """Retorna True si tiene algun domicilio marcado para entrega (Fiscal o Sucursal)"""
        # Nueva logica simplificada por pedido del usuario (Orange Dot = Necesita Entrega, NO Retiro)
        # Se excluye explicitamente 'RETIRO_EN_PLANTA' aunque tenga flag envio=True (casos legacy)
        return any(d.es_entrega and d.activo and d.origen_logistico != 'RETIRO_EN_PLANTA' for d in self.domicilios)

    @property
    def contacto_principal_nombre(self):
        """Retorna nombre del contacto principal o primero disponible"""
        try:
             # Ensure vinculos is loaded / iterable
            if not self.vinculos:
                return None
                
            # [GY-FIX V6] Vinculo V6 no tiene 'es_principal'. Usamos el primero activo.
            # principal = next((v for v in self.vinculos if v.es_principal and v.activo), None)
            principal = next((v for v in self.vinculos if v.activo), None)
            if principal and principal.persona:
                return principal.persona.nombre_completo
            
            # Fallback: Primero activo
            primero = next((v for v in self.vinculos if v.activo), None)
            if primero and primero.persona:
                return primero.persona.nombre_completo
        except Exception as e:
            # Prevent crash on list view
            print(f"[ERROR] computing contacto_principal_nombre for {self.id}: {e}")
            return None
            
        return None


class Domicilio(Base):
    """
    Tabla 'domicilios' (Logística).
    Soporte multi-sucursal.
    """
    __tablename__ = "domicilios"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # [DEPRECATED V5.2] We move to N:M, but keep nullable FK for legacy cleanup phase
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=True)
    
    alias = Column(String, nullable=True, index=True) # "Depósito Norte"
    calle = Column(String, nullable=True, index=True)
    numero = Column(String, nullable=True)
    piso = Column(String, nullable=True) # [V7]
    depto = Column(String, nullable=True) # [V7]
    maps_link = Column(String, nullable=True) # [V7] Link GMaps or LatLong
    notas_logistica = Column(Text, nullable=True) # [V7] Instrucciones chofer
    contacto_id = Column(Integer, nullable=True) # [V7] Referencia a contacto logístico
    cp = Column(String, nullable=True)
    localidad = Column(String, nullable=True, index=True)
    provincia_id = Column(String(5), ForeignKey("provincias.id"), nullable=True)
    
    # [GENOMA 64-bit] Sede Identity Parity
    # Asigna un bit único (2^0 a 2^63) para identificar esta sede en el CUIT único.
    bit_identidad = Column(BigInteger, default=0, nullable=False)
    flags_estado = Column(BigInteger, default=0, nullable=False) # [V5.8] Genoma Soberano

    # Flags de uso
    # [V5.2 GOLD] New Naming Convention
    is_active = Column(Boolean, default=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False) # Legacy compatibility
    es_fiscal = Column(Boolean, default=False) # [LEGACY] To be moved to Relation Genome
    es_entrega = Column(Boolean, default=False) # [LEGACY] To be moved to Relation Genome
    es_predeterminado = Column(Boolean, default=False) # [LEGACY]
    
    # [GENOMA INFRA V14]
    # Bit 0: RAMPA | Bit 1: DOCK_CARGA | Bit 2: ASCENSOR_CARGA
    flags_infra = Column(BigInteger, default=0, nullable=False)
    
    is_maps_manual = Column(Boolean, default=False, nullable=False) # [V15.2 GOLD] True if user edited/verified it
    
    observaciones = Column(Text, nullable=True) # [V7.1] Notas generales del domicilio
    
    # [V7.2] Dirección de Entrega (Separada de Fiscal)
    calle_entrega = Column(String, nullable=True)
    numero_entrega = Column(String, nullable=True)
    piso_entrega = Column(String, nullable=True)
    depto_entrega = Column(String, nullable=True)
    cp_entrega = Column(String, nullable=True)
    localidad_entrega = Column(String, nullable=True)
    provincia_entrega_id = Column(String(5), ForeignKey("provincias.id"), nullable=True)

    # Logística
    transporte_habitual_nodo_id = Column(GUID(), ForeignKey("nodos_transporte.id"), nullable=True)
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True)
    intermediario_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True)
    
    # Estrategia Logística (V5.2)
    metodo_entrega = Column(String, nullable=True) # RETIRO_LOCAL, TRANSPORTE, FLETE_MOTO, PLATAFORMA, DROPSHIPPING
    modalidad_envio = Column(String, nullable=True) # A_DOMICILIO, A_SUCURSAL
    origen_logistico = Column(String, nullable=True) # DESPACHO_NUESTRO, RETIRO_EN_PLANTA
    
    # Relaciones
    # [V5.2 GOLD] N:M Support
    clientes = relationship("Cliente", secondary=domicilios_clientes, back_populates="domicilios")
    
    # Legacy 1:N backward link
    cliente = relationship("Cliente", back_populates="domicilios_legacy", foreign_keys=[cliente_id])
    provincia = relationship(Provincia, foreign_keys=[provincia_id])
    provincia_entrega = relationship(Provincia, foreign_keys=[provincia_entrega_id])
    
    transporte_habitual_nodo = relationship("NodoTransporte")
    transporte = relationship("EmpresaTransporte", foreign_keys=[transporte_id])
    intermediario = relationship("EmpresaTransporte", foreign_keys=[intermediario_id])

    @property
    def resumen(self):
        """Retorna una cadena formateada con todos los datos del domicilio"""
        numero = f" {self.numero}" if self.numero else ""
        piso_depto = ""
        if self.piso or self.depto:
            piso_str = f"Piso {self.piso}" if self.piso else ""
            depto_str = f"Dto {self.depto}" if self.depto else ""
            piso_depto = f" ({piso_str} {depto_str})".replace("  ", " ")
        
        localidad = f", {self.localidad}" if self.localidad else ""
        provincia = ""
        if self.provincia:
            provincia = f" ({self.provincia.nombre})"
        elif self.provincia_id:
            provincia = f" ({self.provincia_id})"
            
        cp = f" [CP: {self.cp}]" if self.cp else ""
        
        return f"{self.calle or 'S/D'}{numero}{piso_depto}{localidad}{provincia}{cp}"

    def __repr__(self):
        return f"<Domicilio(alias='{self.alias}', calle='{self.calle}')>"
