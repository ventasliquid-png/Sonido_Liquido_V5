# [IDENTIDAD] - backend/ingesta/models.py
# Versión: V5.6 GOLD | Sincronización: 20260508191200
# ------------------------------------------
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, JSON, LargeBinary, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID


class FacturaNoSeCarga(Base):
    """
    [S899, Card #212; Carlos 04/11] Un número de comprobante de ARCA que se decidió NO cargar en V5 a propósito
    (p. ej. la factura 2586 y la NC 74: representan una OC que nunca se completó). La pantalla «Facturas» arma la lista
    de «Faltan» con los huecos de la numeración; lo que está acá no cuenta como hueco y se muestra aparte, con su motivo.
    """
    __tablename__ = "facturas_no_se_cargan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_comprobante = Column(String, nullable=False)       # FACTURA_A, NOTA_CREDITO_A, ...
    punto_venta = Column(Integer, nullable=False)
    numero_comprobante = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)
    decidido_por = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("tipo_comprobante", "punto_venta", "numero_comprobante", name="uq_factura_no_se_carga"),
    )

class FacturasRaw(Base):
    """
    Dominio de Ingesta - Capa 0 (Raw).
    Almacena el archivo físico y el resultado crudo del parser.
    """
    __tablename__ = "ingesta_facturas_raw"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    pdf_bytes = Column(LargeBinary, nullable=False) # El PDF original (BLOB)
    
    # Metadatos de Auditoría
    audit_status = Column(String, default="RECIBIDO") # RECIBIDO, PROCESADO, ERROR, CUARENTENA
    audit_warning = Column(String, nullable=True)
    
    # Genoma 64 bits (Nike Arq 5.5)
    # Bit 0 = EXISTENCE, Bit 2 = EN_CUARENTENA
    flags_estado = Column(BigInteger, nullable=False, default=1)
    
    # Data técnica
    parsed_data_raw = Column(JSON, nullable=True) # El JSON que escupe el parser directamente
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    # Relaciones
    procesadas = relationship("FacturasProcesadas", back_populates="raw", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FacturasRaw(id={self.id}, filename='{self.filename}', status='{self.audit_status}')>"

class FacturasProcesadas(Base):
    """
    Dominio de Ingesta - Capa 1 (Staging).
    Contiene la resolución humana/Conserje antes de impactar el sistema.
    """
    __tablename__ = "ingesta_facturas_procesadas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    raw_id = Column(GUID(), ForeignKey("ingesta_facturas_raw.id"), nullable=False, index=True)
    
    # Vínculos resueltos (pueden ser nulos en PREVIEW)
    cliente_id = Column(GUID(), ForeignKey("clientes.id"), nullable=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True, index=True)
    
    # Datos Normalizados (después de intervención humana o Conserje confianza alta)
    numero_factura = Column(String, nullable=True, index=True)
    cae = Column(String, nullable=True, index=True)
    vto_cae = Column(String, nullable=True)
    
    parsed_data_final = Column(JSON, nullable=True) # Lo que se usará para crear Remito/Factura
    audit_log = Column(JSON, nullable=True) # Historial de decisiones del Conserje
    
    # Estados del workflow: PREVIEW, APROBADA, REMITO_CREADO, DESCARTADA
    estado = Column(String, default="PREVIEW")
    
    # Genoma 64 bits (Nike Arq 5.5)
    # Bit 0 = EXISTENCE, Bit 1 = IS_VIRGIN, Bit 2 = TIENE_NC, Bit 6 = RAW_CON_PROBLEMAS...
    flags_estado = Column(BigInteger, nullable=False, default=1)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    # Relaciones
    raw = relationship("FacturasRaw", back_populates="procesadas")
    cliente = relationship("Cliente")
    pedido = relationship("Pedido")

    def __repr__(self):
        return f"<FacturasProcesadas(id={self.id}, factura='{self.numero_factura}', estado='{self.estado}')>"
