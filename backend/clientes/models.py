# Archivo: backend/clientes/models.py
# Módulo Clientes (V5) - Implementación Jerárquica (Nike S)

import uuid
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text, DateTime, Integer, Sequence, JSON
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.core.database import Base, GUID
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Provincia
# Nota: Importamos Usuario como string o condicionalmente si hay riesgo de ciclo, 
# pero Maestros son seguros.
from sqlalchemy.orm import foreign, remote

class Cliente(Base):
    """
    Tabla 'clientes' (La Cuenta).
    Representa la entidad comercial principal.
    """
    __tablename__ = "clientes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    razon_social = Column(String, nullable=False, index=True)
    nombre_fantasia = Column(String, nullable=True)
    cuit = Column(String, unique=False, nullable=False, index=True)
    
    # Identificadores
    # [FIX PILOT] Removed Sequence for SQLite compatibility
    codigo_interno = Column(Integer, nullable=True)
    legacy_id_bas = Column(String, nullable=True) # ID del sistema BAS anterior

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
    
    # Motor de Precios V5
    estrategia_precio = Column(String, default='MAYORISTA_FISCAL') # 'Sabor' del Cliente
    
    # Datos financieros
    saldo_actual = Column(Numeric(18, 2), default=0.00)
    
    # Protocolo Lázaro
    activo = Column(Boolean, default=True, nullable=False)
    requiere_auditoria = Column(Boolean, default=False)
    
    # Ranking de Uso (V5.2)
    contador_uso = Column(Integer, default=0)
    
    # Vector de Historial (V5.3 - Cache Denormalizado)
    # Guarda [{id, fecha, total, estado}, ...] (Max 5)
    historial_cache = Column(JSON, nullable=True, default=list)

    # Auditoría
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    domicilios = relationship("Domicilio", back_populates="cliente", cascade="all, delete-orphan")
    # [GY-FIX V6] Removed legacy VinculoComercial relationship
    # vinculos = relationship("VinculoComercial", back_populates="cliente", cascade="all, delete-orphan")
    condicion_iva = relationship(CondicionIva)
    lista_precios = relationship(ListaPrecios)
    segmento = relationship(Segmento)
    # [FIX] Importación diferida o string directo si el modelo está en Base
    vendedor = relationship("Usuario")
    # [FIX] Usar nombre corto 'Pedido' ya que está registrado en Base
    pedidos = relationship("Pedido", back_populates="cliente")
    # [NUEVO V6 Multiplex] Relación Polimórfica Inversa
    # [NUEVO V6 Multiplex] Relación Polimórfica Inversa
    # Renombrado de vinculos_rel a vinculos para mantener compatibilidad de nombre
    vinculos = relationship(
        "Vinculo",
        primaryjoin="and_(foreign(Vinculo.entidad_id)==Cliente.id, Vinculo.entidad_tipo=='CLIENTE')",
        viewonly=True,
        foreign_keys="[Vinculo.entidad_id]"
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
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=False)
    
    alias = Column(String, nullable=True) # "Depósito Norte"
    calle = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    piso = Column(String, nullable=True) # [V7]
    depto = Column(String, nullable=True) # [V7]
    maps_link = Column(String, nullable=True) # [V7] Link GMaps or LatLong
    notas_logistica = Column(Text, nullable=True) # [V7] Instrucciones chofer
    contacto_id = Column(Integer, nullable=True) # [V7] Referencia a contacto logístico
    cp = Column(String, nullable=True)
    localidad = Column(String, nullable=True)
    provincia_id = Column(String(5), ForeignKey("provincias.id"), nullable=True)
    
    # Flags de uso
    activo = Column(Boolean, default=True, nullable=False)
    es_fiscal = Column(Boolean, default=False)
    es_entrega = Column(Boolean, default=False)
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
    cliente = relationship("Cliente", back_populates="domicilios")
    provincia = relationship(Provincia, foreign_keys=[provincia_id])
    provincia_entrega = relationship(Provincia, foreign_keys=[provincia_entrega_id])
    transporte_habitual_nodo = relationship("NodoTransporte")
    transporte = relationship("EmpresaTransporte", foreign_keys=[transporte_id])
    intermediario = relationship("EmpresaTransporte", foreign_keys=[intermediario_id])

    def __repr__(self):
        return f"<Domicilio(alias='{self.alias}', calle='{self.calle}')>"
