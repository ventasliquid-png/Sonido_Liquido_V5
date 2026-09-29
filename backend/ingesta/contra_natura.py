# backend/ingesta/contra_natura.py
"""
[Etapa 7c, DISENO_CIRCUITO_PR_S869.md §5.1] Facturas "contra natura": emitidas directamente en ARCA,
sin PR previo (ya pasó: la auditoría de Lácteos encontró 2530, 2566 y 2586). Tratamiento decidido
por Carlos:

  - Cliente y mercadería existentes, hecha de corrida -> RETROACTIVO: se reconstruyen pedido y PR
    desde el PDF y la factura se concilia contra ese PR, todo en una sola transacción.
  - Desmadre grande (cliente o mercadería que no están en el sistema) -> no se crea nada: nota de
    crédito por el total y rehacer el circuito como corresponde. Se puede marcar el PDF para que
    quede el rastro de que falta esa NC.

Regla de diseño: el circuito excepcional se permite, pero queda MARCADO Y CONTABLE, nunca en
silencio. Marcas: Pedido con PedidoFlags.ORIGEN_FACTURA (38) + ORIGEN_RETROACTIVO (39) --los dos ya
canonizados en el genoma--, origen "CONTRA_NATURA", nota "[SISTEMA] Pedido reconstruido desde
factura ..." (categoría "Contra natura" del Informe D), factura con notas_auditoria de contra
natura y FacturasProcesadas.estado = "CONTRA_NATURA".

Nunca se autocrean productos (§5: muere la autocreación de VS). Nunca se elige un transporte al
azar: el de la sede, el último del cliente, o lo elige el operador.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.ingesta.conciliador import (
    ConciliadorService, _parsear, _norm_nombre, _fecha, EPS,
)

PREFIJO_NOTA = "[SISTEMA] Pedido reconstruido desde factura"


def _uuid(valor):
    import uuid
    if valor is None or valor == "":
        return None
    try:
        return uuid.UUID(str(valor))
    except ValueError:
        return None


class ContraNaturaService:

    @staticmethod
    def _domicilios(cliente) -> List:
        return [d for d in (cliente.domicilios or []) if d.activo]

    @staticmethod
    def _domicilio_sugerido(cliente):
        # Entrega antes que fiscal: el remito acompaña mercadería (DISENO_CIRCUITO_PR_S869.md §9.2).
        doms = ContraNaturaService._domicilios(cliente)
        return (next((d for d in doms if d.es_entrega), None)
                or next((d for d in doms if d.es_fiscal), None)
                or (doms[0] if doms else None))

    @staticmethod
    def _transporte_sugerido(db: Session, cliente, domicilio):
        if domicilio is not None and domicilio.transporte_id:
            return domicilio.transporte_id
        from backend.pedidos.models import Pedido
        ultimo = (db.query(Pedido)
                  .filter(Pedido.cliente_id == cliente.id, Pedido.transporte_id.isnot(None))
                  .order_by(Pedido.fecha.desc(), Pedido.id.desc()).first())
        return ultimo.transporte_id if ultimo else None

    # ------------------------------------------------------------------ evaluar

    @staticmethod
    def evaluar(db: Session, raw_id, cliente_id=None, productos: Optional[List[dict]] = None,
                domicilio_entrega_id=None, transporte_id=None) -> dict:
        """`productos`: [{"item_pdf": i, "producto_id": id | None}] -- si no viene, se sugiere
        por nombre normalizado (solo coincidencia única). Devuelve el veredicto RETROACTIVO o
        DESMADRE con sus motivos, y los bloqueos que impiden cualquier registro."""
        from backend.productos.models import Producto
        from backend.logistica.models import EmpresaTransporte
        from backend.clientes.constants import ClientFlags
        from backend.remitos.service import RemitosService

        raw = ConciliadorService._raw(db, raw_id)
        parsed = _parsear(raw)
        pv, nc = RemitosService._partes_numero_factura(parsed.get("factura", {}).get("numero"))
        enc = ConciliadorService._encabezado(parsed, pv, nc)
        items_pdf = enc["items"]

        bloqueos = ConciliadorService._bloqueos_de_comprobante(db, enc)
        avisos, motivos_desmadre = [], []
        if not items_pdf:
            bloqueos.append("SIN_RENGLONES: el PDF no trae renglones legibles -- no hay qué reconstruir.")

        # --- Cliente: por CUIT, nunca por razón social ---
        clientes = ConciliadorService._clientes_del_cuit(db, enc["cuit"])
        cliente = None
        if not clientes:
            motivos_desmadre.append(f"El CUIT {enc['cuit'] or '(ilegible)'} no es de ningún cliente del sistema.")
        elif cliente_id is not None:
            cliente = next((c for c in clientes if str(c.id).replace("-", "") == str(cliente_id).replace("-", "")), None)
            if cliente is None:
                bloqueos.append("CLIENTE_INVALIDO: el cliente elegido no tiene el CUIT de la factura.")
        elif len(clientes) == 1:
            cliente = clientes[0]
        else:
            bloqueos.append(f"CLIENTE_A_ELEGIR: {len(clientes)} clientes comparten el CUIT -- elegí cuál.")

        if cliente is not None and (cliente.flags_estado or 0) & int(ClientFlags.OPERATOR_OK):
            bloqueos.append(
                "CLIENTE_ROSA: el cliente es Rosa y la factura es un comprobante fiscal. Pasalo a Blanco "
                "(datos fiscales completos) antes de registrarla -- mismo criterio que el alta de pedidos."
            )

        # Si el cliente tiene PR esperando factura, lo normal es conciliar contra ellos (7b).
        if cliente is not None:
            from backend.remitos.models import Remito
            from backend.pedidos.models import Pedido
            pendientes = [r for r in db.query(Remito).join(Pedido, Remito.pedido_id == Pedido.id)
                          .filter(Pedido.cliente_id == cliente.id, Remito.estado != "ANULADO").all()
                          if ConciliadorService._renglones_pendientes(r)]
            if pendientes:
                avisos.append(
                    f"HAY_PR_PENDIENTES: el cliente tiene {len(pendientes)} PR esperando factura. Si esta "
                    f"factura corresponde a alguno, conciliá contra él en vez de reconstruir uno nuevo."
                )

        # --- Mercadería: cada renglón tiene que ser un producto existente ---
        catalogo = db.query(Producto).filter(Producto.activo == True).order_by(Producto.nombre).all()  # noqa: E712
        por_id = {p.id: p for p in catalogo}
        por_nombre: Dict[str, List] = {}
        for p in catalogo:
            por_nombre.setdefault(_norm_nombre(p.nombre), []).append(p)

        elegidos = {e.get("item_pdf"): e.get("producto_id") for e in (productos or [])}
        renglones = []
        for i, it in enumerate(items_pdf):
            if productos is not None:
                pid = elegidos.get(i)
                como = "operador" if pid else None
            else:
                cands = por_nombre.get(_norm_nombre(it.get("descripcion")), [])
                pid = cands[0].id if len(cands) == 1 else None
                como = "nombre" if pid else None
            prod = por_id.get(pid) if pid is not None else None
            if pid is not None and prod is None:
                bloqueos.append(f"PRODUCTO_INVALIDO: renglón {i + 1} apunta a un producto inexistente o inactivo.")
            if prod is None:
                motivos_desmadre.append(f"'{it.get('descripcion')}' no es ningún producto del catálogo.")
            renglones.append({
                "item_pdf": i,
                "descripcion": it.get("descripcion"),
                "cantidad": it.get("cantidad"),
                "precio_unitario": it.get("precio_unitario"),
                "subtotal": it.get("subtotal"),
                "producto_id": prod.id if prod else None,
                "producto": prod.nombre if prod else None,
                "como": como if prod else None,
            })
            if (it.get("cantidad") or 0) <= EPS:
                bloqueos.append(f"CANTIDAD_INVALIDA: renglón {i + 1} sin cantidad positiva.")

        # --- Logística del PR: sede y transporte, sin elegir al azar ---
        domicilio = transporte = None
        domicilios_out, transportes_out = [], []
        if cliente is not None:
            doms = ContraNaturaService._domicilios(cliente)
            domicilios_out = [{"id": str(d.id), "texto": d.resumen if hasattr(d, "resumen") else d.calle,
                               "es_entrega": bool(d.es_entrega), "es_fiscal": bool(d.es_fiscal)} for d in doms]
            dom_id = _uuid(domicilio_entrega_id)
            domicilio = (next((d for d in doms if d.id == dom_id), None) if dom_id
                         else ContraNaturaService._domicilio_sugerido(cliente))
            if dom_id and domicilio is None:
                bloqueos.append("DOMICILIO_INVALIDO: la sede elegida no es del cliente.")
            trans_id = _uuid(transporte_id) or ContraNaturaService._transporte_sugerido(db, cliente, domicilio)
            transporte = db.query(EmpresaTransporte).filter(EmpresaTransporte.id == trans_id).first() if trans_id else None
            transportes_out = [{"id": str(t.id), "nombre": t.nombre}
                               for t in db.query(EmpresaTransporte).order_by(EmpresaTransporte.nombre).all()]
            if domicilio is None:
                bloqueos.append("DOMICILIO_REQUERIDO: el cliente no tiene ninguna sede activa.")
            if transporte is None:
                bloqueos.append("TRANSPORTE_REQUERIDO: no hay transporte habitual de la sede ni del cliente -- elegilo.")

        veredicto = "DESMADRE" if motivos_desmadre else "RETROACTIVO"
        return {
            "raw_id": str(raw.id),
            "factura": enc,
            "veredicto": veredicto,
            "motivos_desmadre": motivos_desmadre,
            "bloqueos": bloqueos,
            "avisos": avisos,
            "clientes": [{"id": str(c.id), "razon_social": c.razon_social} for c in clientes],
            "cliente_id": str(cliente.id) if cliente else None,
            "renglones": renglones,
            "catalogo": [{"id": p.id, "nombre": p.nombre} for p in catalogo],
            "domicilios": domicilios_out,
            "domicilio_entrega_id": str(domicilio.id) if domicilio else None,
            "transportes": transportes_out,
            "transporte_id": str(transporte.id) if transporte else None,
            "_cliente": cliente,
            "_domicilio": domicilio,
            "_transporte": transporte,
            "_raw": raw,
        }

    # ------------------------------------------------------------------ confirmar

    @staticmethod
    def confirmar(db: Session, raw_id, cliente_id, productos: List[dict], domicilio_entrega_id,
                  transporte_id, usuario) -> dict:
        from backend.pedidos.models import Pedido, PedidoItem
        from backend.pedidos.constants import PedidoFlags, STATE_MASK
        from backend.productos.models import Producto
        from backend.remitos.service import RemitosService
        from backend.remitos import schemas as remito_schemas

        ev = ContraNaturaService.evaluar(db, raw_id, cliente_id, productos, domicilio_entrega_id, transporte_id)
        if ev["bloqueos"]:
            raise HTTPException(status_code=409, detail="; ".join(ev["bloqueos"]))
        if ev["veredicto"] != "RETROACTIVO":
            raise HTTPException(
                status_code=409,
                detail="DESMADRE: " + " ".join(ev["motivos_desmadre"]) +
                       " Corresponde nota de crédito por el total y rehacer el circuito.")

        enc, cliente = ev["factura"], ev["_cliente"]
        ts = datetime.now().strftime("%d/%m/%Y %H:%M")
        flags = (int(PedidoFlags.EXISTENCE) | int(PedidoFlags.ORIGEN_FACTURA) | int(PedidoFlags.ORIGEN_RETROACTIVO))
        flags = (flags & ~int(STATE_MASK)) | int(PedidoFlags.ES_FIRME)

        try:
            fecha_emision = _fecha(enc["fecha_emision"])
            pedido = Pedido(
                cliente_id=cliente.id,
                fecha=datetime.combine(fecha_emision, datetime.min.time()) if fecha_emision else datetime.now(),
                nota=(f"{PREFIJO_NOTA} {enc['tipo_comprobante']} {enc['numero']}, emitida en ARCA sin PR "
                      f"previo (contra natura). {ts}"),
                oc=enc.get("oc"),
                estado="PENDIENTE",
                tipo_facturacion=(enc["tipo_comprobante"] or "X").split("_")[-1],
                origen="CONTRA_NATURA",
                domicilio_entrega_id=ev["_domicilio"].id,
                transporte_id=ev["_transporte"].id,
                flags_estado=flags,
                total=0.0,
            )
            db.add(pedido)
            db.flush()

            neto = 0.0
            items_pedido = []
            for r in ev["renglones"]:
                cant = r["cantidad"] or 0.0
                precio = r["precio_unitario"] or 0.0
                subtotal = r["subtotal"] if r["subtotal"] is not None else round(cant * precio, 2)
                pi = PedidoItem(pedido_id=pedido.id, producto_id=r["producto_id"], cantidad=cant,
                                precio_unitario=precio, subtotal=subtotal, nota="")
                db.add(pi)
                items_pedido.append(pi)
                neto += subtotal
                # Misma reserva que el alta de pedidos -- si no, borrar o editar este pedido después
                # dejaría stock_reservado negativo.
                prod = db.query(Producto).get(r["producto_id"])
                if prod and prod.tipo_producto != "SERVICIO":
                    prod.stock_reservado = (prod.stock_reservado or Decimal("0")) + Decimal(str(cant))
            pedido.total = round(neto * 1.21, 2)  # blanco: siempre con IVA (_aplica_iva, pedidos/router.py)
            db.flush()

            remito = RemitosService.armar_remito(db, remito_schemas.ArmarRemitoPayload(
                pedido_id=pedido.id,
                domicilio_entrega_id=ev["_domicilio"].id,
                transporte_id=ev["_transporte"].id,
                items=[{"pedido_item_id": pi.id, "cantidad": pi.cantidad} for pi in items_pedido],
            ), commit=False)
            from backend.remitos.models import RemitoItem
            ri_por_pi = {ri.pedido_item_id: ri.id
                         for ri in db.query(RemitoItem).filter(RemitoItem.remito_id == remito.id).all()}
            emparejamiento = [{"item_pdf": r["item_pdf"], "remito_item_id": ri_por_pi[pi.id]}
                              for r, pi in zip(ev["renglones"], items_pedido)]

            resultado = ConciliadorService.confirmar(
                db, raw_id, [str(remito.id)], emparejamiento, usuario, contra_natura=True)
        except Exception:
            db.rollback()
            raise

        return {**resultado, "pedido_id": pedido.id, "remito_id": str(remito.id)}

    # ------------------------------------------------------------------ desmadre

    @staticmethod
    def marcar_desmadre(db: Session, raw_id, usuario, cliente_id=None, productos=None) -> dict:
        """No registra la factura: deja el rastro en el PDF de que falta una NC por el total y
        rehacer el circuito -- "nunca en silencio". Evalúa con el emparejamiento de productos que
        eligió el operador: si con eso la mercadería existe, no es desmadre."""
        ev = ContraNaturaService.evaluar(db, raw_id, cliente_id, productos)
        if ev["veredicto"] != "DESMADRE":
            raise HTTPException(status_code=409, detail="NO_ES_DESMADRE: esta factura se puede reconstruir retroactiva.")
        raw = ev["_raw"]
        raw.audit_status = "DESMADRE"
        raw.audit_warning = (
            f"Factura {enc_num(ev)} contra natura sin cliente o mercadería en el sistema: pendiente NC por el "
            f"total y rehacer el circuito. Motivos: {' '.join(ev['motivos_desmadre'])} "
            f"Marcado por {getattr(usuario, 'username', '?')} el {datetime.now().strftime('%d/%m/%Y %H:%M')}."
        )
        raw.processed_at = datetime.now(timezone.utc)
        db.add(raw)
        db.commit()
        return {"raw_id": str(raw.id), "audit_status": raw.audit_status, "audit_warning": raw.audit_warning}


def enc_num(ev: dict) -> str:
    f = ev["factura"]
    return f"{f.get('tipo_comprobante') or ''} {f.get('numero') or ''}".strip()
