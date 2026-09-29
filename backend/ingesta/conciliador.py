# backend/ingesta/conciliador.py
"""
[Etapa 7b, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §9 -- DISENO_CIRCUITO_PR_S869.md §5-§7]
La ingesta deja de CREAR y pasa a CONCILIAR: el PR (Remito) ya existe antes que la factura. Se
elige contra qué PR(s) cierra el PDF de ARCA, se comparan renglones, cantidades y precios, se
clasifica la diferencia (A/B/C) y, al confirmar, se registra la factura REAL -- con el CAE, el tipo
y la fecha que manda ARCA, no un espejo en BORRADOR -- vinculada al PR, y se escribe
`RemitoItem.cantidad_facturada`.

Clases (DISENO_CIRCUITO_PR_S869.md §7):
  A -- la factura está bien, nuestro registro incompleto (tipo, fecha, número, CAE): se toma del
       PDF, no se emite nada. Informativo.
  B -- la factura dice otra cosa (cantidad de más, precio distinto, renglón que no está en el PR):
       decisión de Carlos 28/09 -- CONCILIA IGUAL y deja nota [SISTEMA] en el PR; el desfase queda
       visible por la resta (facturada != remitida) hasta que llegue la NC/ND (Etapa 7d).
  C -- la factura es de otro (CUIT distinto al del cliente del PR): BLOQUEA. NC total y reemitir.

Se compara por CUIT, renglones, cantidades y precios -- NUNCA por razón social ni domicilio
(§6: ARCA escribe desde su padrón, nosotros corregimos el nuestro; una alarma que salta siempre
se ignora). NC/ND todavía no entran por acá (7d, esquema pendiente de Nike).
"""
import json
import uuid
from datetime import datetime, date, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

EPS = 0.001
TOLERANCIA_PRECIO_ABS = 1.0      # $1 o 0,5 %, lo que sea mayor
TOLERANCIA_PRECIO_REL = 0.005


def _norm_cuit(cuit: Optional[str]) -> str:
    return (cuit or "").replace("-", "").strip()


def _norm_nombre(texto: Optional[str]) -> str:
    """Solo para SUGERIR el emparejamiento (el operador confirma): sin acentos, mayúsculas,
    espacios ni puntuación -- "Alcohol 70%" de ARCA tiene que encontrar "Alcohol 70 %" del
    padrón (caso real, factura 2526)."""
    from backend.informes.export_utils import normalizar_texto
    return "".join(ch for ch in normalizar_texto(texto) if ch.isalnum())


def _parsear(raw) -> dict:
    """Siempre re-parsea el PDF con el parser vigente: los raws guardados antes de la Etapa 7a
    no tienen tipo de comprobante ni fecha de emisión en parsed_data_raw."""
    from backend.remitos.pdf_parser import extract_text_from_pdf, parse_invoice_data
    text, words = extract_text_from_pdf(raw.pdf_bytes)
    return parse_invoice_data(text, words)


def _fecha(valor: Optional[str]) -> Optional[date]:
    if not valor:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            continue
    return None


def desglose_importes(enc: dict, items_pdf: List[dict]):
    """Neto, IVA 21 / 10,5, exento, percepciones y total de un comprobante de ARCA. Neto y total los
    manda ARCA; el IVA sale de los renglones por alícuota, y lo que sobre hasta el total se registra
    como percepciones. Compartido por la conciliación de facturas (7b) y de NC/ND (7d)."""
    iva_21 = sum((it.get("subtotal") or 0) * 0.21 for it in items_pdf if abs((it.get("alicuota_iva") or 0) - 21) < EPS)
    iva_105 = sum((it.get("subtotal") or 0) * 0.105 for it in items_pdf if abs((it.get("alicuota_iva") or 0) - 10.5) < EPS)
    exento = sum((it.get("subtotal") or 0) for it in items_pdf if abs(it.get("alicuota_iva") or 0) < EPS)
    neto = enc["total_neto"] if enc["total_neto"] is not None else sum(
        (it.get("subtotal") or 0) for it in items_pdf if abs(it.get("alicuota_iva") or 0) >= EPS)
    total = enc["total_final"] if enc["total_final"] is not None else neto + iva_21 + iva_105 + exento
    percepciones = round(total - neto - iva_21 - iva_105 - exento, 2)
    if abs(percepciones) < 0.5:
        percepciones = 0.0
    return neto, iva_21, iva_105, exento, percepciones, total


def _precio_efectivo_pedido(pedido_item) -> Optional[float]:
    """Precio neto por unidad que el pedido tenía para ese renglón, con el descuento de renglón
    incluido (mismo criterio que utils/entregaParcial.js::precioEfectivo, al revés de prioridad:
    acá se compara contra la factura, que también trae el precio con bonificación aplicada)."""
    if pedido_item is None:
        return None
    if (pedido_item.cantidad or 0) > 0 and pedido_item.subtotal:
        return pedido_item.subtotal / pedido_item.cantidad
    return pedido_item.precio_unitario or None


class ConciliadorService:

    @staticmethod
    def _raw(db: Session, raw_id):
        from backend.ingesta.models import FacturasRaw
        raw = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
        if not raw:
            raise HTTPException(status_code=404, detail="Factura Raw no encontrada")
        return raw

    @staticmethod
    def _clientes_del_cuit(db: Session, cuit: str):
        from backend.clientes.models import Cliente
        if not cuit:
            return []
        con_guiones = f"{cuit[:2]}-{cuit[2:10]}-{cuit[10:]}"
        return db.query(Cliente).filter(Cliente.cuit.in_([cuit, con_guiones])).all()

    @staticmethod
    def _duplicada(db: Session, pv: Optional[int], nc: Optional[int]):
        """Por número, sin importar el tipo: el camino viejo guardaba el tipo adivinado por la
        condición de IVA (a veces PRESUPUESTO_X), así que filtrar por tipo dejaría pasar
        duplicados reales (mismo criterio que el Guard 3 de create_from_ingestion).

        [Etapa 7d] EXCEPTO las notas de crédito/débito: ARCA las numera aparte de las facturas
        (una NC A 00001-00000012 y una Factura A 00001-00000012 conviven), así que una NC con el
        mismo número NO hace duplicada a una factura. Su propio control de duplicado es por
        (tipo canónico, punto de venta, número) -- ver conciliador_ajuste.py."""
        from sqlalchemy import or_
        from backend.facturacion.models import Factura
        if nc is None:
            return None
        q = db.query(Factura).filter(
            Factura.numero_comprobante == nc,
            or_(Factura.tipo_comprobante.is_(None), ~Factura.tipo_comprobante.like("NOTA_%")),
        )
        if pv is not None:
            q = q.filter(Factura.punto_venta == pv)
        return q.first()

    @staticmethod
    def _renglones_pendientes(remito) -> List:
        """Renglones que todavía esperan factura: facturable (facturada no es NULL), salió
        mercadería (remitida > 0 -- las devoluciones se concilian contra NC en la 7d) y lo
        facturado no alcanza a lo remitido."""
        return [
            ri for ri in remito.items
            if ri.cantidad_facturada is not None
            and (ri.cantidad_remitida or 0) > EPS
            and ri.cantidad_facturada < ri.cantidad_remitida - EPS
        ]

    @staticmethod
    def _describir_renglon(ri) -> dict:
        pi = ri.pedido_item
        producto = pi.producto.nombre if (pi and pi.producto) else ((pi.nota if pi else None) or "Ítem")
        return {
            "remito_item_id": ri.id,
            "remito_id": str(ri.remito_id),
            "producto": producto,
            "remitida": ri.cantidad_remitida,
            "facturada": ri.cantidad_facturada,
            "pendiente_facturar": round(ri.cantidad_remitida - (ri.cantidad_facturada or 0), 4),
            "precio_pedido": _precio_efectivo_pedido(pi),
        }

    @staticmethod
    def _encabezado(parsed: dict, pv, nc) -> dict:
        f = parsed.get("factura", {})
        return {
            "numero": f.get("numero"),
            "punto_venta": pv,
            "numero_comprobante": nc,
            "tipo_comprobante": f.get("tipo_comprobante"),
            "clase_comprobante": f.get("clase_comprobante"),
            "tipo_warning": f.get("tipo_warning"),
            "fecha_emision": f.get("fecha_emision"),
            "cae": f.get("cae"),
            "vto_cae": f.get("vto_cae"),
            "total_neto": f.get("total_neto"),
            "total_final": f.get("total_final"),
            "oc": f.get("oc"),
            "cuit": _norm_cuit(parsed.get("cliente", {}).get("cuit")),
            "razon_social_arca": parsed.get("cliente", {}).get("razon_social"),
            "items": parsed.get("items", []),
            "audit_warning": f.get("audit_warning"),
        }

    @staticmethod
    def _bloqueos_de_comprobante(db: Session, enc: dict) -> List[str]:
        bloqueos = []
        if enc["clase_comprobante"] is None:
            bloqueos.append(f"TIPO_DESCONOCIDO: {enc.get('tipo_warning') or 'no se pudo leer el tipo de comprobante'}")
        elif enc["clase_comprobante"] != "FACTURA":
            bloqueos.append(
                f"ES_AJUSTE: el PDF es {enc['tipo_comprobante']}, no una factura. Las notas de crédito/"
                f"débito se concilian como ajuste de facturas (Etapa 7d), no contra un PR."
            )
        if enc["numero_comprobante"] is None or enc["punto_venta"] is None:
            bloqueos.append("NUMERO_COMPROBANTE_REQUERIDO: no se pudo leer punto de venta y número del PDF.")
        if not enc["cae"]:
            bloqueos.append("CAE_REQUERIDO: no se pudo leer el CAE del PDF.")
        if not enc["cuit"]:
            bloqueos.append("CUIT_REQUERIDO: no se pudo leer el CUIT del comprador en el PDF.")
        dup = ConciliadorService._duplicada(db, enc["punto_venta"], enc["numero_comprobante"])
        if dup:
            bloqueos.append(
                f"FACTURA_DUPLICADA: ya existe {dup.tipo_comprobante} {dup.numero_completo} en el sistema "
                f"(estado {dup.estado})."
            )
        return bloqueos

    # ------------------------------------------------------------------ candidatos

    @staticmethod
    def candidatos(db: Session, raw_id) -> dict:
        from backend.remitos.models import Remito, RemitoItem
        from backend.pedidos.models import Pedido, PedidoItem

        raw = ConciliadorService._raw(db, raw_id)
        parsed = _parsear(raw)
        from backend.remitos.service import RemitosService
        pv, nc = RemitosService._partes_numero_factura(parsed.get("factura", {}).get("numero"))
        enc = ConciliadorService._encabezado(parsed, pv, nc)

        # [Etapa 7d] Una NC/ND no cierra un PR: ajusta facturas. Mismo punto de entrada y misma
        # pantalla, pero el objeto a elegir es otro (facturas, no PR) -- ver conciliador_ajuste.py.
        if enc["clase_comprobante"] in ("NOTA_CREDITO", "NOTA_DEBITO"):
            from backend.ingesta.conciliador_ajuste import AjusteService
            return AjusteService.candidatos(db, raw, enc)

        bloqueos = ConciliadorService._bloqueos_de_comprobante(db, enc)
        avisos = []
        clientes = ConciliadorService._clientes_del_cuit(db, enc["cuit"])
        if enc["cuit"] and not clientes:
            avisos.append(
                "CUIT_FUERA_DEL_PADRON: ningún cliente tiene ese CUIT -- es una factura contra natura "
                "(sin PR previo), no se puede conciliar por acá."
            )
        if len(clientes) > 1:
            avisos.append(f"CUIT_COMPARTIDO: {len(clientes)} clientes comparten este CUIT -- elegí el PR con cuidado.")

        prs = []
        if clientes:
            remitos = (
                db.query(Remito)
                .join(Pedido, Remito.pedido_id == Pedido.id)
                .filter(Pedido.cliente_id.in_([c.id for c in clientes]), Remito.estado != "ANULADO")
                .options(
                    joinedload(Remito.pedido).joinedload(Pedido.cliente),
                    joinedload(Remito.items).joinedload(RemitoItem.pedido_item).joinedload(PedidoItem.producto),
                )
                .order_by(Remito.fecha_creacion.desc())
                .all()
            )
            for r in remitos:
                pendientes = ConciliadorService._renglones_pendientes(r)
                if not pendientes:
                    continue
                prs.append({
                    "remito_id": str(r.id),
                    "numero_legal": r.numero_legal,
                    "estado": r.estado,
                    "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
                    "pedido_id": r.pedido_id,
                    "pedido_oc": r.pedido.oc if r.pedido else None,
                    "cliente": r.pedido.cliente.razon_social if (r.pedido and r.pedido.cliente) else None,
                    "renglones": [ConciliadorService._describir_renglon(ri) for ri in pendientes],
                })
            if not prs:
                avisos.append("SIN_PR_PENDIENTE: el cliente no tiene ningún PR blanco con facturación pendiente.")

        return {"modo": "FACTURA", "raw_id": str(raw.id), "filename": raw.filename, "factura": enc,
                "prs": prs, "bloqueos": bloqueos, "avisos": avisos}

    # ------------------------------------------------------------------ evaluar

    @staticmethod
    def evaluar(db: Session, raw_id, remito_ids: List[str], emparejamiento: Optional[List[dict]] = None) -> dict:
        """Compara el PDF contra los PR elegidos y clasifica. `emparejamiento`: lista
        [{"item_pdf": i, "remito_item_id": id | None}] -- si no viene, se sugiere uno."""
        from backend.remitos.models import Remito, RemitoItem
        from backend.pedidos.models import Pedido, PedidoItem
        from backend.remitos.service import RemitosService

        raw = ConciliadorService._raw(db, raw_id)
        parsed = _parsear(raw)
        pv, nc = RemitosService._partes_numero_factura(parsed.get("factura", {}).get("numero"))
        enc = ConciliadorService._encabezado(parsed, pv, nc)
        items_pdf = enc["items"]

        bloqueos = ConciliadorService._bloqueos_de_comprobante(db, enc)
        diferencias = []

        if not remito_ids:
            bloqueos.append("PR_REQUERIDO: elegí al menos un PR contra el cual conciliar.")
        remitos = []
        for rid in remito_ids or []:
            try:
                rid_uuid = uuid.UUID(str(rid))
            except ValueError:
                bloqueos.append(f"PR_INEXISTENTE: {rid}")
                continue
            r = (
                db.query(Remito)
                .options(
                    joinedload(Remito.pedido).joinedload(Pedido.cliente),
                    joinedload(Remito.items).joinedload(RemitoItem.pedido_item).joinedload(PedidoItem.producto),
                )
                .filter(Remito.id == rid_uuid).first()
            )
            if not r:
                bloqueos.append(f"PR_INEXISTENTE: {rid}")
                continue
            if r.estado == "ANULADO":
                bloqueos.append(f"PR_ANULADO: {r.numero_legal or r.id}")
            remitos.append(r)

        # Clase C -- CUIT del PDF contra el CUIT del cliente de cada PR
        clientes_ids = set()
        for r in remitos:
            cliente = r.pedido.cliente if r.pedido else None
            clientes_ids.add(cliente.id if cliente else None)
            cuit_pr = _norm_cuit(cliente.cuit if cliente else None)
            if enc["cuit"] and cuit_pr != enc["cuit"]:
                diferencias.append({
                    "clase": "C",
                    "remito_id": str(r.id),
                    "detalle": (
                        f"La factura es al CUIT {enc['cuit']} y el PR {r.numero_legal or r.id} es de "
                        f"{cliente.razon_social if cliente else '(sin cliente)'} (CUIT {cuit_pr or 'vacío'}). "
                        f"Factura a otro cliente: NC total y reemitir."
                    ),
                })
        if len(clientes_ids) > 1:
            bloqueos.append("PR_DE_VARIOS_CLIENTES: los PR elegidos son de clientes distintos.")

        pendientes = []
        for r in remitos:
            pendientes.extend(ConciliadorService._renglones_pendientes(r))
        por_id = {ri.id: ri for ri in pendientes}
        if remitos and not pendientes:
            bloqueos.append("SIN_RENGLONES_PENDIENTES: los PR elegidos no tienen nada pendiente de facturar.")

        # Emparejamiento: sugerido (nombre normalizado, después por descarte) o el que manda el operador
        sugerido = emparejamiento is None
        if sugerido:
            emparejamiento = []
            usados = set()
            for i, it in enumerate(items_pdf):
                n = _norm_nombre(it.get("descripcion"))
                cands = [ri for ri in pendientes
                         if ri.id not in usados and _norm_nombre(ConciliadorService._describir_renglon(ri)["producto"]) == n]
                par = cands[0].id if len(cands) == 1 else None
                if par:
                    usados.add(par)
                emparejamiento.append({"item_pdf": i, "remito_item_id": par, "como": "nombre" if par else None})
            libres_pdf = [e for e in emparejamiento if e["remito_item_id"] is None]
            libres_pr = [ri for ri in pendientes if ri.id not in usados]
            if len(libres_pdf) == 1 and len(libres_pr) == 1:
                libres_pdf[0]["remito_item_id"] = libres_pr[0].id
                libres_pdf[0]["como"] = "descarte"
        else:
            vistos_pdf, vistos_pr = set(), set()
            for e in emparejamiento:
                i, rid = e.get("item_pdf"), e.get("remito_item_id")
                if not isinstance(i, int) or i < 0 or i >= len(items_pdf) or i in vistos_pdf:
                    bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: renglón de factura {i!r} fuera de rango o repetido.")
                    continue
                vistos_pdf.add(i)
                if rid is not None:
                    if rid not in por_id:
                        bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: el renglón de PR {rid} no está pendiente en los PR elegidos.")
                    elif rid in vistos_pr:
                        bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: el renglón de PR {rid} está usado dos veces.")
                    vistos_pr.add(rid)
            if len(vistos_pdf) != len(items_pdf):
                bloqueos.append("EMPAREJAMIENTO_INCOMPLETO: falta decidir el par de algún renglón de la factura.")

        # Clase B -- por renglón
        for e in emparejamiento:
            i = e.get("item_pdf")
            if not isinstance(i, int) or i >= len(items_pdf):
                continue
            it = items_pdf[i]
            ri = por_id.get(e.get("remito_item_id"))
            desc = it.get("descripcion") or f"renglón {i + 1}"
            if ri is None:
                diferencias.append({"clase": "B", "item_pdf": i, "remito_item_id": None,
                                    "detalle": f"'{desc}' está en la factura pero no en los PR elegidos."})
                continue
            info = ConciliadorService._describir_renglon(ri)
            cant = it.get("cantidad") or 0
            if cant > info["pendiente_facturar"] + EPS:
                diferencias.append({"clase": "B", "item_pdf": i, "remito_item_id": ri.id,
                                    "detalle": (f"'{info['producto']}': la factura trae {cant} y quedaban "
                                                f"{info['pendiente_facturar']} por facturar (facturó de más).")})
            elif cant < info["pendiente_facturar"] - EPS:
                diferencias.append({"clase": "PARCIAL", "item_pdf": i, "remito_item_id": ri.id,
                                    "detalle": (f"'{info['producto']}': factura {cant} de {info['pendiente_facturar']} "
                                                f"pendientes -- quedan {round(info['pendiente_facturar'] - cant, 4)} por facturar.")})
            precio_pdf = it.get("precio_unitario") or 0
            precio_ped = info["precio_pedido"]
            if precio_ped:
                tol = max(TOLERANCIA_PRECIO_ABS, precio_ped * TOLERANCIA_PRECIO_REL)
                if abs(precio_pdf - precio_ped) > tol:
                    diferencias.append({"clase": "B", "item_pdf": i, "remito_item_id": ri.id,
                                        "detalle": (f"'{info['producto']}': precio en la factura {precio_pdf} "
                                                    f"y en el pedido {round(precio_ped, 2)}.")})

        # Clase A -- lo que manda ARCA y se toma tal cual (informativo)
        diferencias.append({"clase": "A", "detalle": (
            f"Se registra con los datos de ARCA: {enc['tipo_comprobante']} {enc['numero']}, "
            f"emitida {enc['fecha_emision'] or '(fecha ilegible: se usa hoy)'}, CAE {enc['cae']}.")})
        for r in remitos:
            if enc["oc"] and r.pedido and r.pedido.oc and _norm_nombre(enc["oc"]) != _norm_nombre(r.pedido.oc) \
                    and _norm_nombre(r.pedido.oc) not in _norm_nombre(enc["oc"]):
                diferencias.append({"clase": "AVISO", "remito_id": str(r.id),
                                    "detalle": f"OC de la factura '{enc['oc']}' distinta de la del pedido #{r.pedido_id} '{r.pedido.oc}'."})
        if enc.get("audit_warning"):
            diferencias.append({"clase": "AVISO", "detalle": enc["audit_warning"]})

        if any(d["clase"] == "C" for d in diferencias):
            bloqueos.append("CLASE_C: la factura es de otro cliente -- no se concilia.")

        return {
            "raw_id": str(raw.id),
            "factura": enc,
            "remito_ids": [str(r.id) for r in remitos],
            "renglones_pr": [ConciliadorService._describir_renglon(ri) for ri in pendientes],
            "emparejamiento": emparejamiento,
            "emparejamiento_sugerido": sugerido,
            "diferencias": diferencias,
            "bloqueos": bloqueos,
            "_parsed": parsed,
            "_remitos": remitos,
            "_por_id": por_id,
        }

    # ------------------------------------------------------------------ confirmar

    @staticmethod
    def confirmar(db: Session, raw_id, remito_ids: List[str], emparejamiento: List[dict], usuario,
                  contra_natura: bool = False) -> dict:
        """`contra_natura` [Etapa 7c]: el PR se acaba de reconstruir desde el mismo PDF (factura
        emitida en ARCA sin PR previo). Se concilia igual, pero queda marcado en la factura y en la
        auditoría de la ingesta -- "el circuito excepcional se permite, marcado y contable"."""
        from backend.facturacion.models import Factura, FacturaItem, FacturaRemito
        from backend.remitos.models import RemitoNota
        from backend.ingesta.models import FacturasProcesadas

        ev = ConciliadorService.evaluar(db, raw_id, remito_ids, emparejamiento)
        if ev["bloqueos"]:
            raise HTTPException(status_code=409, detail="; ".join(ev["bloqueos"]))

        enc, remitos, por_id = ev["factura"], ev["_remitos"], ev["_por_id"]
        items_pdf = enc["items"]
        cliente = remitos[0].pedido.cliente
        pedidos = {r.pedido_id for r in remitos}

        neto, iva_21, iva_105, exento, percepciones, total = desglose_importes(enc, items_pdf)

        factura = Factura(
            cliente_id=cliente.id,
            pedido_id=next(iter(pedidos)) if len(pedidos) == 1 else None,
            tipo_comprobante=enc["tipo_comprobante"],
            estado="AUTORIZADA_AFIP",
            punto_venta=enc["punto_venta"],
            numero_comprobante=enc["numero_comprobante"],
            fecha_emision=_fecha(enc["fecha_emision"]) or datetime.now().date(),
            neto_gravado=round(neto, 2),
            iva_21=round(iva_21, 2),
            iva_105=round(iva_105, 2),
            exento=round(exento, 2),
            percepciones=percepciones,
            total=round(total, 2),
            cae=enc["cae"],
            cae_vencimiento=_fecha(enc["vto_cae"]),
            cuit_comprador=enc["cuit"],
            notas_auditoria=(
                f"FACTURA CONTRA NATURA: emitida en ARCA sin PR previo; pedido y PR reconstruidos "
                f"desde el PDF (Etapa 7c) -- ingesta raw {raw_id}" if contra_natura
                else f"CONCILIADA CONTRA PR (Etapa 7b) -- ingesta raw {raw_id}"
            ),
        )
        db.add(factura)
        db.flush()

        for r in remitos:
            db.add(FacturaRemito(factura_id=factura.id, remito_id=r.id, flags_estado=1))

        par_por_item = {e["item_pdf"]: e.get("remito_item_id") for e in ev["emparejamiento"]}
        for i, it in enumerate(items_pdf):
            ri = por_id.get(par_por_item.get(i))
            cant = it.get("cantidad") or 0
            db.add(FacturaItem(
                factura_id=factura.id,
                remito_item_id=ri.id if ri else None,
                pedido_item_id=ri.pedido_item_id if ri else None,
                descripcion=it.get("descripcion") or f"Renglón {i + 1}",
                cantidad=cant,
                precio_unitario_neto=it.get("precio_unitario") or 0.0,
                alicuota_iva=it.get("alicuota_iva") if it.get("alicuota_iva") is not None else 21.0,
                subtotal_neto=it.get("subtotal") or 0.0,
            ))
            if ri is not None:
                # Lo que dice la factura, aunque supere a lo remitido: el desfase queda a la vista
                # por la resta hasta que llegue la NC/ND (Clase B, decisión de Carlos 28/09).
                ri.cantidad_facturada = (ri.cantidad_facturada or 0) + cant
                db.add(ri)

        # Clase B -> nota [SISTEMA] en el PR (en el renglón cuando la diferencia es de un renglón)
        referencia = f"{enc['tipo_comprobante']} {factura.numero_completo}"
        autor_id = getattr(usuario, "id", None)
        primer_remito = remitos[0]
        for d in ev["diferencias"]:
            if d["clase"] != "B":
                continue
            ri = por_id.get(d.get("remito_item_id"))
            db.add(RemitoNota(
                remito_id=ri.remito_id if ri else primer_remito.id,
                remito_item_id=ri.id if ri else None,
                autor_id=autor_id,
                texto=f"[SISTEMA] Conciliación con {referencia}: diferencia clase B -- {d['detalle']} Pendiente de NC/ND.",
            ))

        raw = ConciliadorService._raw(db, raw_id)
        audit = [{k: v for k, v in d.items()} for d in ev["diferencias"]]
        db.add(FacturasProcesadas(
            raw_id=raw.id,
            cliente_id=cliente.id,
            pedido_id=factura.pedido_id,
            numero_factura=enc["numero"],
            cae=enc["cae"],
            vto_cae=enc["vto_cae"],
            parsed_data_final=json.loads(json.dumps({**ev["_parsed"], "emparejamiento": ev["emparejamiento"],
                                                     "remito_ids": ev["remito_ids"]}, default=str)),
            audit_log={"diferencias": audit, "usuario": getattr(usuario, "username", None)},
            estado="CONTRA_NATURA" if contra_natura else "CONCILIADA",
            processed_at=datetime.now(timezone.utc),
        ))
        raw.audit_status = "PROCESADO"
        raw.processed_at = datetime.now(timezone.utc)
        db.add(raw)

        db.commit()
        db.refresh(factura)
        return {
            "factura_id": str(factura.id),
            "tipo_comprobante": factura.tipo_comprobante,
            "numero": factura.numero_completo,
            "remito_ids": ev["remito_ids"],
            "diferencias": audit,
        }
