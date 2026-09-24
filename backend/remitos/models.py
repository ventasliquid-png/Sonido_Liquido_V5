# backend/remitos/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Float, DateTime
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
    # [Etapa 1, Circuito 17 -- DISENO_CIRCUITO_17_S870.md §3] nullable desde acá: presente =
    # PR comercializable (blanco o rosa); ausente = huérfano (prueba de movimiento sin pedido).
    # Ningún código de hoy crea un Remito sin pedido_id -- este cambio es inerte hasta que la
    # Etapa 4 construya el flujo que sí lo hace.
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True, index=True)

    # [Etapa 1, Circuito 17 -- DISENO_CIRCUITO_17_S870.md §6] Por qué existe un movimiento sin
    # pedido (feria, muestra, devolución a proveedor...). Solo tiene sentido cuando pedido_id es
    # NULL. Taxonomía deliberadamente abierta (texto libre, no enum) -- ver A2/A4 de ese diseño.
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
    
    # Trazabilidad Absoluta: Qué renglón del pedido estoy entregando.
    # [Etapa 4-bis, migrate_042_huerfano_producto_id.py] nullable desde acá -- un huérfano
    # (Circuito 17, Remito.pedido_id None) no tiene pedido del que sacar un pedido_item_id.
    pedido_item_id = Column(Integer, ForeignKey("pedidos_items.id"), nullable=True)

    # [Etapa 4-bis, decisión de Carlos 24/09] Solo tiene sentido cuando pedido_item_id es NULL
    # (huérfano). FK a un producto real del catálogo -- nunca texto libre, para no reabrir el
    # agujero "Ghost Style" que la guarda de Card #125 ya cerró en update_remito (addendum
    # Etapa 0): un huérfano sigue siendo mercadería real (HuerfanoDestino rastrea cantidades que
    # después reingresan o se comercializan), tiene que apuntar a un producto del catálogo.
    # Regla de aplicación (no CHECK de base): pedido_item_id XOR producto_id, nunca los dos,
    # nunca ninguno -- validada en RemitosService.armar_remito.
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True)

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
    producto = relationship("Producto")
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
        if self.pedido_item:
            return self.pedido_item.producto.nombre if self.pedido_item.producto else (self.pedido_item.nota or "Ítem")
        # [Etapa 4-bis] Huérfano: no hay pedido_item, el producto se lee directo de producto_id.
        if self.producto:
            return self.producto.nombre
        return "Ítem"

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


class HuerfanoDestino(Base):
    """Evento de reconciliación de un huérfano (Remito sin pedido, Circuito 17).

    [Etapa 1 -- DISENO_CIRCUITO_17_S870.md §5, dictamen Nike Módulo 2] Un huérfano no reconcilia
    contra una promesa (no hay "declarada"): reconcilia contra lo que salió, repartido en
    destinos. Cumplido = reingresó + se_perdio + se_comercializo == remitida. Tabla de eventos,
    igual que RemitoNota -- nunca se anula el huérfano para cerrarlo, se le cuelgan destinos.
    """
    __tablename__ = "huerfano_destinos"

    id = Column(Integer, primary_key=True, index=True)
    huerfano_item_id = Column(Integer, ForeignKey("remitos_items.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    # Enum cerrado (a diferencia de Remito.motivo, que es texto libre) -- DISENO_CIRCUITO_17_S870.md §5.
    tipo = Column(Enum("reingreso", "perdida", "comercializado", name="huerfano_destino_tipo"), nullable=False)
    cantidad = Column(Float, nullable=False)
    # id del pedido nuevo que absorbió la mercadería, solo si tipo == "comercializado".
    referencia = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    # Usuario.id es Integer (ver nota en RemitoNota).
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    huerfano_item = relationship("RemitoItem")

    def __repr__(self):
        return f"<HuerfanoDestino(tipo='{self.tipo}', cantidad={self.cantidad})>"
