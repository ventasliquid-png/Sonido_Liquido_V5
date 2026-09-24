# backend/remitos/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base, GUID

class Remito(Base):
    """
    Cabeza de Remito (Viaje Físico).
    Desacopla la entrega de la facturación.
    """
    __tablename__ = "remitos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Vínculo Comercial
    # [Revertido, migrate_043_revertir_huerfano_pedido_id.py] Vuelve a NOT NULL -- el diseño
    # "Remito sin Pedido" para huérfanos (Etapa 1, DISENO_CIRCUITO_17_S870.md §3) fue
    # reemplazado por decisión de Carlos + Nike: un huérfano es un Pedido normal con
    # PedidoFlags.ES_NO_COMERCIAL, no un Remito sin pedido_id. Ver
    # DISENO_PEDIDO_NO_COMERCIAL_S873_2026-09-24.md.
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)

    # [Vestigial tras el revert de arriba] Columna que quedó en la base (migrate_041 la agregó,
    # migrate_043 no la saca) pero sin lectores en código -- "por qué existe un movimiento sin
    # pedido" ya no aplica porque todo Remito tiene pedido_id.
    motivo = Column(String, nullable=True)

    # Destino Físico (Sobrescribe al Pedido si es split)
    domicilio_entrega_id = Column(GUID(), ForeignKey("domicilios.id"), nullable=False)
    
    # Ejecutor Logístico
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=False)
    
    # Datos Operativos
    fecha_salida = Column(DateTime, nullable=True) # Cuándo sale efectivamente
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Estado del Viaje
    # BORRADOR: Preparando
    # PREPARACION: En depósito armando cajas
    # EN_CAMINO: Salió
    # ENTREGADO: Confirmado por cliente
    # ANULADO: Cancelado
    estado = Column(String, default="BORRADOR") 
    
    # Identificación Legal / Tracking
    numero_legal = Column(String, nullable=True) # X-0001-000000...
    cae = Column(String, nullable=True)
    vto_cae = Column(DateTime, nullable=True)
    
    # GATEKEEPER FINANCIERO (Logic Gate)
    # Hereda del Pedido o se setea manual.
    # Si False, Depósito ve el remito pero NO puede cambiar estado a EN_CAMINO.
    aprobado_para_despacho = Column(Boolean, default=False)

    # Datos Logísticos (V15.1.4)
    bultos = Column(Integer, nullable=True)
    valor_declarado = Column(Float, nullable=True)

    # Genoma 64-bit (Nike S836)
    flags_estado = Column(Integer, default=0)

    # Relaciones
    pedido = relationship("Pedido", backref="remitos")
    domicilio_entrega = relationship("Domicilio")
    transporte = relationship("EmpresaTransporte")
    
    items = relationship("RemitoItem", back_populates="remito", cascade="all, delete-orphan")
    vinculos_facturas = relationship("FacturaRemito", back_populates="remito", cascade="all, delete-orphan")

    @property
    def cliente_id(self):
        return self.pedido.cliente_id if self.pedido else None

    @property
    def razon_social(self):
        return self.pedido.cliente.razon_social if self.pedido and self.pedido.cliente else "Desconocido"

    def _factura_de_referencia(self):
        """La factura que ampara este remito, leída del vínculo facturas_remitos.

        [S868, regla de Carlos 17/09] El remito no tiene CAE propio ni se le escribe uno: lo
        único que muestra es la referencia a una factura que existe y está vinculada (la de la
        ingesta), con el CAE de esa factura. Sin factura, nada. Facturas anuladas o sin número
        no cuentan. Sin accesos que puedan tirar AttributeError (Card #119: Pydantic los
        enmascara).
        """
        for vinculo in self.vinculos_facturas or []:
            factura = vinculo.factura
            if factura is None or factura.punto_venta is None or factura.numero_comprobante is None:
                continue
            if str(factura.estado or "").upper().startswith("ANULAD"):
                continue
            return factura
        return None

    @property
    def factura_vinculada(self):
        """Número de la factura de referencia ("0001-00002533") o None."""
        factura = self._factura_de_referencia()
        return factura.numero_completo if factura else None

    @property
    def factura_vinculada_cae(self):
        """CAE de la factura de referencia, leído de la factura (nunca de remitos.cae) o None."""
        factura = self._factura_de_referencia()
        return (factura.cae or None) if factura else None

    def __repr__(self):
        return f"<Remito(id={self.id}, estado='{self.estado}')>"


class RemitoItem(Base):
    """
    Detalle del Remito (Qué va en la caja).
    """
    __tablename__ = "remitos_items"

    id = Column(Integer, primary_key=True, index=True)
    
    remito_id = Column(GUID(), ForeignKey("remitos.id"), nullable=False)
    
    # Trazabilidad Absoluta: Qué renglón del pedido estoy entregando
    pedido_item_id = Column(Integer, ForeignKey("pedidos_items.id"), nullable=False)

    # [Etapa 1 -- INFORME_IMPLEMENTACION_PR_S869.md §4.1, dictamen Nike] Las cuatro cantidades
    # del PR. "cantidad_remitida" es la columna "cantidad" de siempre, renombrada -- admite
    # negativo (devolución, Etapa 6). "cantidad_declarada" es la foto del pedido al armar el PR
    # (Etapa 4 la empieza a poblar distinto de remitida; hasta entonces valen lo mismo).
    # "cantidad_recibida" NULL = "llegó lo que salió" (S868 §2.5). "cantidad_facturada" NULL =
    # no aplica/rosa/fuera de lo fiscal, 0 = aplica y pendiente -- nunca confundir los dos.
    cantidad_declarada = Column(Float, nullable=False, default=0.0)
    cantidad_remitida = Column(Float, default=0.0)
    cantidad_recibida = Column(Float, nullable=True)
    cantidad_facturada = Column(Float, nullable=True)

    # Relaciones
    remito = relationship("Remito", back_populates="items")
    pedido_item = relationship("PedidoItem", back_populates="remitos_items")
    notas = relationship("RemitoNota", back_populates="remito_item")

    @property
    def cantidad(self):
        """Alias de compatibilidad hacia atrás -- Etapa 1 no cambia el contrato de la API.

        RemitoItemResponse (schemas.py, from_attributes=True) todavía serializa "cantidad";
        este alias evita romper esa respuesta y cualquier consumidor del frontend mientras el
        contrato no se actualice a propósito (etapa futura, coordinada con el frontend).
        """
        return self.cantidad_remitida

    @property
    def descripcion_display(self):
        if not self.pedido_item: return "Ítem"
        return self.pedido_item.producto.nombre if self.pedido_item.producto else (self.pedido_item.nota or "Ítem")

    def __repr__(self):
        return f"<RemitoItem(cant_remitida={self.cantidad_remitida})>"


class RemitoNota(Base):
    """Novedad fechada sobre un remito o un renglón -- acumulativa, nunca editable.

    [Etapa 1 -- INFORME_IMPLEMENTACION_PR_S869.md §4.1, dictamen Nike Módulo 2] Un objeto cuya
    razón de ser es la responsabilidad de una persona (quién dijo qué, y cuándo) no es un bit:
    es una tabla hija relacional. Corregir no es sobrescribir (S869 §1.2): una nota nueva no
    pisa la anterior.
    """
    __tablename__ = "remitos_notas"

    id = Column(Integer, primary_key=True, index=True)
    remito_id = Column(GUID(), ForeignKey("remitos.id"), nullable=False)
    remito_item_id = Column(Integer, ForeignKey("remitos_items.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.now)
    # [Nota de tipo, verificado contra backend/auth/models.py] Usuario.id es Integer, no GUID
    # -- a diferencia de Cliente/Domicilio/Remito, auth quedó con PK numérica.
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    texto = Column(String, nullable=False)
    # [DISENO_CIRCUITO_17_S870.md §4.3] Foto del remito firmado, o de una guía de transporte
    # externa. Mismo patrón que Factura.pdf_path (facturacion/models.py) -- ruta/URL simple, sin
    # tabla de adjuntos aparte.
    foto_path = Column(String, nullable=True)

    remito = relationship("Remito")
    remito_item = relationship("RemitoItem", back_populates="notas")

    def __repr__(self):
        return f"<RemitoNota(remito_id={self.remito_id})>"

# [Revertido, migrate_043_revertir_huerfano_pedido_id.py] HuerfanoDestino existió acá (Etapa 1,
# DISENO_CIRCUITO_17_S870.md §5) para reconciliar un "Remito sin Pedido" -- diseño reemplazado
# por PedidoFlags.ES_NO_COMERCIAL (DISENO_PEDIDO_NO_COMERCIAL_S873_2026-09-24.md). Tabla nunca
# tuvo lectores ni escritores en código ni filas reales; DROP autorizado por Nike.
