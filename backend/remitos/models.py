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
    # [S876, migrate_047] Nullable: una entrega en MOSTRADOR (retiro en planta) o con transporte
    # propio no tiene empresa de transporte de terceros. FLETE_TERCERO sigue exigiéndolo (lo
    # valida RemitosService.armar_remito). domicilio_entrega_id NO se vuelve nullable: el mostrador
    # usa un domicilio real (la oficina, DOMICILIO_ROSETI_ID).
    transporte_id = Column(GUID(), ForeignKey("empresas_transporte.id"), nullable=True)

    # [S876, migrate_047] Cómo salió ESTA entrega (ver remitos/constants.py MetodoEntrega). Se fija
    # una sola vez al crear el Remito y nunca se relee en vivo de Domicilio/Pedido: es el hecho
    # fáctico de la entrega puntual, no la configuración habitual de la dirección
    # (Domicilio.metodo_entrega/origen_logistico, otra capa que no se toca). NULL = remito anterior.
    metodo_entrega = Column(String, nullable=True)

    # Datos Operativos
    fecha_salida = Column(DateTime, nullable=True) # Cuándo sale efectivamente
    fecha_creacion = Column(DateTime, default=datetime.now)
    # [S891, migrate_066, Carlos 22/10] Fecha de EMISIÓN: el día en que el remito toma número (es la fecha del papel, editable con
    # motivo). Distinta de fecha_salida (la salida física, sentido de la S869): un remito puede imprimirse y quedar en el depósito
    # esperando al transporte. Si nadie marca otra cosa, la salida se asume en la emisión.
    fecha_emision = Column(DateTime, nullable=True)
    
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

    # [S893, migrate_068, Carlos 25/10: «la OC se copia al remito»] La orden de compra del pedido, copiada al momento de crear el
    # remito (lo hace el evento before_flush de abajo, igual para cualquier alta). Así el remito se encuentra por OC y no depende
    # de lo que el pedido diga después. Modificable más adelante, con motivo y nota (A1 del MARCO_REMITOS).
    oc = Column(String, nullable=True)

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

    # [S876, migrate_047] Por qué este renglón salió sin ser venta firme (CONSIGNACION,
    # MUESTRA_SIN_CARGO, GARANTIA_REEMPLAZO; ver remitos/constants.py). NULL = facturable normal.
    # Es del renglón y no del remito ni del pedido: un mismo envío puede llevar cuatro renglones de
    # venta firme y uno en consignación. Mientras esté abierto, cantidad_facturada queda en NULL.
    motivo_no_facturable = Column(String, nullable=True)

    # [S893, migrate_069] Corrección de un renglón (Carlos 26/10): si este renglón es una CORRECCIÓN (cantidad negativa que descuenta lo que se perdió, no salió, se rechazó
    # o volvió), `corrige_item_id` es el renglón de remito que corrige y `causa` el porqué (CausaCorreccion). NULL = renglón común. Sin FK a propósito: la migración
    # agrega columnas planas y la relación se resuelve por consulta.
    corrige_item_id = Column(Integer, nullable=True, index=True)
    causa = Column(String, nullable=True)

    # Relaciones
    remito = relationship("Remito", back_populates="items")
    pedido_item = relationship("PedidoItem", back_populates="remitos_items")
    notas = relationship("RemitoNota", back_populates="remito_item")
    # [Etapa 7d] Renglones de factura (y de NC/ND) que apuntan a este renglón del PR.
    facturas_items = relationship("FacturaItem", back_populates="remito_item")

    @property
    def cantidad_acreditada(self):
        """[Etapa 7d, dictamen Nike 29/09] Σ cantidad de los renglones de NOTAS DE CRÉDITO (no
        anuladas) que apuntan a este renglón. Calculado, nunca persistido. Las ND no cuentan: ajustan
        importes, no cantidades. Una NC de solo-monto (renglón sin par) no apunta a ningún renglón de PR
        y por eso no aparece acá -- correcto, no movió cantidades."""
        from backend.facturacion.constants import es_nota_credito
        return sum(
            (fi.cantidad or 0.0)
            for fi in self.facturas_items
            if fi.factura is not None
            and es_nota_credito(fi.factura.tipo_comprobante)
            and fi.factura.estado != "ANULADA"
        )

    @property
    def cantidad_facturada_neta(self):
        """cantidad_facturada (bruto, inmutable: NUNCA se muta cuando llega una NC) menos lo acreditado
        por NC. None se preserva: NULL = no aplica (rosa / fuera de lo fiscal), y no se convierte en
        0 ni en un número negativo (dictamen Nike 23/09: NULL != 0)."""
        if self.cantidad_facturada is None:
            return None
        return self.cantidad_facturada - self.cantidad_acreditada

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
    # [Etapa 5] Mismo patrón que Cliente.vendedor (clientes/models.py) para referenciar
    # Usuario desde otro módulo.
    autor = relationship("Usuario")

    @property
    def autor_username(self):
        return self.autor.username if self.autor else None

    def __repr__(self):
        return f"<RemitoNota(remito_id={self.remito_id})>"

# [Revertido, migrate_043_revertir_huerfano_pedido_id.py] HuerfanoDestino existió acá (Etapa 1,
# DISENO_CIRCUITO_17_S870.md §5) para reconciliar un "Remito sin Pedido" -- diseño reemplazado
# por PedidoFlags.ES_NO_COMERCIAL (DISENO_PEDIDO_NO_COMERCIAL_S873_2026-09-24.md). Tabla nunca
# tuvo lectores ni escritores en código ni filas reales; DROP autorizado por Nike.


# [S891, Nike Sello de Oro 22/10] El genoma del remito (clase, estado, logística, calificadores: RemitoFlags 29-45) lo calcula una
# sola función (backend/remitos/genoma.py) en cada guardado, a partir de los hechos. Acá también se fijan las fechas del momento en
# que el remito TOMA NÚMERO, venga de donde venga el número (impresión, ingesta, remito manual): emisión = ahora; salida = emisión
# salvo que esté marcado EN_DEPOSITO (esperando retiro).
from sqlalchemy import event as _event, inspect as _sa_inspect
from sqlalchemy.orm import Session as _Session


@_event.listens_for(_Session, "before_flush")
def _genoma_de_remitos(session, flush_context, instances):
    tocados = []
    for obj in list(session.new) + list(session.dirty):
        if isinstance(obj, Remito):
            r = obj
        elif isinstance(obj, RemitoItem):
            r = obj.remito
        else:
            continue
        if r is not None and r not in tocados and r not in session.deleted:
            tocados.append(r)
    if not tocados:
        return
    from backend.remitos import genoma
    from backend.remitos.constants import RemitoFlags
    nuevos = set(session.new)
    with session.no_autoflush:
        for r in tocados:
            if r in nuevos and not (r.oc or "").strip():   # [S893] la OC del pedido, copiada al crear el remito
                ped = r.pedido
                if ped is None and r.pedido_id:
                    from backend.pedidos.models import Pedido as _Pedido
                    ped = session.get(_Pedido, r.pedido_id)
                if ped is not None and (ped.oc or "").strip():
                    r.oc = ped.oc.strip()
            if r.numero_legal and _sa_inspect(r).attrs.numero_legal.history.has_changes():
                if r.fecha_emision is None:
                    r.fecha_emision = datetime.now()
                if r.fecha_salida is None and not (int(r.flags_estado or 0) & int(RemitoFlags.EN_DEPOSITO)):
                    r.fecha_salida = r.fecha_emision
            genoma.sincronizar(r)
