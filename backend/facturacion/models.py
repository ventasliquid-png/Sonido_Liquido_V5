# backend/facturacion/models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Integer, Date, Enum, Numeric, DateTime, Table, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

class FacturaRemito(Base):
    """
    Tabla puente N:M entre Facturas y Remitos.
    Soporta relaciones complejas: split de pedidos, consolidaciones, re-facturación.
    Cada vínculo tiene identidad propia (GUID), fecha de creación y flags de estado.
    """
    __tablename__ = "facturas_remitos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    factura_id = Column(GUID(), ForeignKey("facturas.id"), nullable=False, index=True)
    remito_id = Column(GUID(), ForeignKey("remitos.id"), nullable=False, index=True)
    fecha_vinculo = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    flags_estado = Column(BigInteger, nullable=False, default=1)

    # Strings para evitar deadlock circular (Regla CLAUDE.md anti-deadlock)
    factura = relationship("Factura", back_populates="vinculos_remitos")
    remito = relationship("Remito", back_populates="vinculos_facturas")

    __table_args__ = (
        UniqueConstraint('factura_id', 'remito_id', name='uq_factura_remito'),
    )

    def __repr__(self):
        return f"<FacturaRemito(factura={self.factura_id}, remito={self.remito_id})>"

class Factura(Base):
    """
    Motor de Facturación (Soberanía Fiscal V5).
    Entidad que representa el comprobante final.
    """
    __tablename__ = "facturas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=False, index=True)
    
    # Origen primario (opcional, una factura puede no venir de un pedido)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True, index=True) 
    
    # Clasificación Fiscal
    # FACTURA_A, FACTURA_B, PRESUPUESTO_X, NOTA_CREDITO_A, etc.
    tipo_comprobante = Column(String, default="PRESUPUESTO_X") 
    
    # Estado Operativo
    # BORRADOR: Calculando, modificable.
    # LIQUIDADA_MANUAL: Transición por bloqueo de ARCA, usuario copió datos.
    # AUTORIZADA_AFIP: Cierre definitivo, CAE obtenido.
    # ANULADA: Descartada.
    estado = Column(String, default="BORRADOR") 
    
    punto_venta = Column(Integer, nullable=True) # Ej: 3
    numero_comprobante = Column(Integer, nullable=True)
    fecha_emision = Column(Date, default=lambda: datetime.now(timezone.utc).date())
    
    # Data Financiera (Neto / Impuestos)
    # Se usa Float para consistencia con el core de Pedidos V5 anterior, 
    # aunque Numeric es preferido para sistemas puramente financieros.
    neto_gravado = Column(Float, default=0.0)
    iva_21 = Column(Float, default=0.0)
    iva_105 = Column(Float, default=0.0)
    exento = Column(Float, default=0.0)
    percepciones = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Sincronización ARCA
    cae = Column(String, nullable=True)
    cae_vencimiento = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Datos fiscales históricos (sin FK para soportar CUIT nulo y Sello Azul)
    cuit_comprador = Column(String, nullable=True)

    # Archivo original PDF
    pdf_path = Column(String, nullable=True)
    notas_auditoria = Column(String, nullable=True)

    # Genoma 64 bits (Nike Arq 5.5 - Nivel GOLD)
    flags_estado = Column(BigInteger, nullable=False, default=3)

    # Relaciones
    cliente = relationship("Cliente")
    pedido = relationship("Pedido")
    items = relationship("FacturaItem", back_populates="factura", cascade="all, delete-orphan")
    vinculos_remitos = relationship("FacturaRemito", back_populates="factura", cascade="all, delete-orphan")

    # [Etapa 7d] Ajustes: una NC/ND (esta fila) ajusta 0..n facturas; una factura recibe 0..n ajustes.
    ajustes_emitidos = relationship(
        "FacturaAjuste", foreign_keys="FacturaAjuste.factura_nc_nd_id",
        back_populates="nc_nd", cascade="all, delete-orphan")
    ajustes_recibidos = relationship(
        "FacturaAjuste", foreign_keys="FacturaAjuste.factura_ajustada_id", back_populates="ajustada")

    __table_args__ = (
        UniqueConstraint(
            'tipo_comprobante', 'punto_venta', 'numero_comprobante',
            name='uq_factura_identificador_afip'
        ),
    )

    @property
    def comprobantes_ajustados(self):
        """[Etapa 7d, dictamen Nike] Listado completo de las facturas que esta NC/ND ajusta (una NC
        de ARCA puede ajustar varias a la vez). Vacío para una factura común o una ND suelta."""
        return [a.ajustada for a in self.ajustes_emitidos if a.ajustada is not None]

    @property
    def comprobante_ajustado_principal(self):
        """El caso normal (~95%, 1:1): la primera factura ajustada, o None."""
        ajustados = self.comprobantes_ajustados
        return ajustados[0] if ajustados else None

    @property
    def numero_completo(self):
        """Devuelve el número legal formateado (XXXX-YYYYYYYY)"""
        return f"{str(self.punto_venta).zfill(4)}-{str(self.numero_comprobante).zfill(8)}"

    def __repr__(self):
        return f"<Factura(id={self.id}, tipo='{self.tipo_comprobante}', estado='{self.estado}')>"


class FacturaItem(Base):
    """
    Renglones de Facturación. 
    Desacoplados del Pedido para asegurar inmutabilidad fiscal.
    """
    __tablename__ = "facturas_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    factura_id = Column(GUID(), ForeignKey("facturas.id"), nullable=False)
    
    # Trazabilidad Operativa (De dónde salió este renglón)
    pedido_item_id = Column(Integer, ForeignKey("pedidos_items.id"), nullable=True)
    remito_item_id = Column(Integer, ForeignKey("remitos_items.id"), nullable=True)
    
    # Copia dura del concepto al momento de facturar
    descripcion = Column(String, nullable=False) 
    
    cantidad = Column(Float, default=1.0)
    precio_unitario_neto = Column(Float, default=0.0) # Precio LIBRE de impuestos
    
    # Impuestos por renglón
    alicuota_iva = Column(Float, default=21.0) # 21.0, 10.5, 0.0
    subtotal_neto = Column(Float, default=0.0) # cantidad * precio_unitario_neto
    
    # Relaciones
    factura = relationship("Factura", back_populates="items")
    pedido_item = relationship("PedidoItem")
    # [Etapa 7d] back_populates: RemitoItem.cantidad_acreditada suma los renglones de NC que apuntan acá.
    remito_item = relationship("RemitoItem", back_populates="facturas_items")

    def __repr__(self):
        return f"<FacturaItem({self.cantidad}x '{self.descripcion}')>"


class FacturaAjuste(Base):
    """
    [Etapa 7d, dictamen Nike 29/09/2026 (Sello de Oro), BIBLIOTECA_NIKE.md Módulo 2 "¿Cómo se modela
    NC/ND...?"] Tabla puente entre una NC/ND y la(s) factura(s) que ajusta.

    NO es una FK simple en `facturas`: ARCA permite que una sola NC ajuste varias facturas a la vez
    (ej. NC global de fin de mes por bonificación de volumen). NC y ND son filas de la misma tabla
    `facturas`, distinguidas por tipo_comprobante -- esta tabla solo dice a qué ajustan.

    `factura_ajustada_id` es opcional: una ND puede existir "suelta" (intereses por mora, gastos
    bancarios) y en ese caso queda atribuida solo al cliente de la propia fila de facturas.
    `monto_aplicado` (nullable): desglose cuando una NC reparte su importe entre varias facturas.
    """
    __tablename__ = "facturas_ajustes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    factura_nc_nd_id = Column(GUID(), ForeignKey("facturas.id"), nullable=False, index=True)
    factura_ajustada_id = Column(GUID(), ForeignKey("facturas.id"), nullable=True, index=True)
    monto_aplicado = Column(Float, nullable=True)
    fecha_vinculo = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    nc_nd = relationship("Factura", foreign_keys=[factura_nc_nd_id], back_populates="ajustes_emitidos")
    ajustada = relationship("Factura", foreign_keys=[factura_ajustada_id], back_populates="ajustes_recibidos")

    __table_args__ = (
        UniqueConstraint('factura_nc_nd_id', 'factura_ajustada_id', name='uq_factura_ajuste'),
    )

    def __repr__(self):
        return f"<FacturaAjuste(nc_nd={self.factura_nc_nd_id}, ajustada={self.factura_ajustada_id})>"
