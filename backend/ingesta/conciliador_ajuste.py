# backend/ingesta/conciliador_ajuste.py
"""
[Etapa 7d, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §9 -- dictamen Nike 29/09/2026 (Sello de Oro),
BIBLIOTECA_NIKE.md Módulo 2 "¿Cómo se modela NC/ND...?"] Conciliación de una NOTA DE CRÉDITO o DÉBITO
de ARCA. Comparte con 7b el punto de entrada (`candidatos`), la pantalla y los helpers, pero el objeto
que se elige es otro: una NC/ND no cierra un PR, AJUSTA una o varias facturas -- por eso tiene
endpoints propios de evaluar/confirmar en vez de un camino paralelo entero.

Reglas (todas salen del dictamen o de decisiones ya tomadas; ninguna es doctrina nueva):
  - NC y ND son filas de la misma tabla `facturas` (tipo NOTA_CREDITO_*/NOTA_DEBITO_*), con importes
    positivos como los manda ARCA: el signo lo da el tipo, no el número.
  - El vínculo va en la tabla puente `facturas_ajustes` (una NC puede ajustar varias facturas).
    Una NC exige al menos una factura; una ND puede ir suelta.
  - `RemitoItem.cantidad_facturada` NUNCA se muta: el renglón de la NC apunta al MISMO renglón de PR
    que la factura (FacturaItem.remito_item_id) y el neto se calcula (RemitoItem.cantidad_facturada_neta).
  - Una ND no mueve cantidades (ajusta importes): sus renglones no se emparejan con nada.
  - Un renglón de NC SIN par es un concepto de solo-monto (ej. "Bonificación por volumen"): no ajusta
    cantidades y no es una diferencia. Un renglón CON par sí acredita cantidad.
  - Clase C (CUIT distinto al de las facturas ajustadas) bloquea. Clase B (acreditó de más) concilia y
    deja nota [SISTEMA], mismo criterio que decidió Carlos el 28/09 para las facturas.
  - Se compara por CUIT, nunca por razón social.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from backend.ingesta.conciliador import (
    ConciliadorService, _parsear, _norm_nombre, _norm_cuit, _fecha, desglose_importes, EPS,
)

ES_NC = "NOTA_CREDITO"
ES_ND = "NOTA_DEBITO"


def _uuid(valor):
    if isinstance(valor, uuid.UUID):
        return valor
    try:
        return uuid.UUID(str(valor))
    except (ValueError, TypeError):
        return None


class AjusteService:

    # ------------------------------------------------------------------ comunes

    @staticmethod
    def _bloqueos_comprobante(db: Session, enc: dict) -> List[str]:
        from backend.facturacion.models import Factura
        bloqueos = []
        if enc["clase_comprobante"] not in (ES_NC, ES_ND):
            bloqueos.append(
                f"NO_ES_AJUSTE: el PDF es {enc['tipo_comprobante'] or 'de tipo desconocido'}, no una nota de "
                f"crédito ni de débito. Las facturas se concilian contra un PR.")
        if enc["numero_comprobante"] is None or enc["punto_venta"] is None:
            bloqueos.append("NUMERO_COMPROBANTE_REQUERIDO: no se pudo leer punto de venta y número del PDF.")
        if not enc["cae"]:
            bloqueos.append("CAE_REQUERIDO: no se pudo leer el CAE del PDF.")
        if not enc["cuit"]:
            bloqueos.append("CUIT_REQUERIDO: no se pudo leer el CUIT del comprador en el PDF.")
        if enc["tipo_comprobante"] and enc["numero_comprobante"] is not None and enc["punto_venta"] is not None:
            # Las NC/ND numeran aparte de las facturas: el duplicado es por (tipo, punto de venta, número).
            dup = db.query(Factura).filter(
                Factura.tipo_comprobante == enc["tipo_comprobante"],
                Factura.punto_venta == enc["punto_venta"],
                Factura.numero_comprobante == enc["numero_comprobante"],
            ).first()
            if dup:
                bloqueos.append(
                    f"AJUSTE_DUPLICADO: ya existe {dup.tipo_comprobante} {dup.numero_completo} en el sistema "
                    f"(estado {dup.estado}).")
        return bloqueos

    @staticmethod
    def _facturas_ajustables(db: Session, clientes) -> List:
        """Facturas reales (con CAE, AUTORIZADA_AFIP) de esos clientes que una nota puede ajustar. Una NC
        no ajusta otra NC; una ND sí puede ser ajustada por una NC."""
        from backend.facturacion.models import Factura
        if not clientes:
            return []
        return (
            db.query(Factura)
            .options(joinedload(Factura.items))
            .filter(
                Factura.cliente_id.in_([c.id for c in clientes]),
                Factura.estado == "AUTORIZADA_AFIP",
                or_(Factura.tipo_comprobante.is_(None), ~Factura.tipo_comprobante.like("NOTA_CREDITO%")),
            )
            .order_by(Factura.fecha_emision.desc(), Factura.numero_comprobante.desc())
            .all()
        )

    @staticmethod
    def _renglon_factura(fi) -> dict:
        """Un renglón de factura ofrecido para emparejar. `disponible`: cuánto se puede acreditar todavía
        de ese renglón -- solo se sabe si el renglón está atado a uno del PR (remito_item_id); en las
        facturas del camino viejo no hay trazabilidad y queda None (no se inventa)."""
        ri = fi.remito_item
        disponible = None
        if ri is not None and ri.cantidad_facturada_neta is not None:
            disponible = round(min(fi.cantidad or 0.0, ri.cantidad_facturada_neta), 4)
        return {
            "factura_item_id": fi.id,
            "descripcion": fi.descripcion,
            "cantidad": fi.cantidad,
            "precio_unitario": fi.precio_unitario_neto,
            "remito_item_id": fi.remito_item_id,
            "disponible": disponible,
            "trazable": ri is not None,
        }

    @staticmethod
    def _describir_factura(f) -> dict:
        return {
            "factura_id": str(f.id),
            "tipo_comprobante": f.tipo_comprobante,
            "numero": f.numero_completo if f.punto_venta is not None and f.numero_comprobante is not None else None,
            "fecha_emision": f.fecha_emision.isoformat() if f.fecha_emision else None,
            "total": f.total,
            "neto": (f.neto_gravado or 0.0) + (f.exento or 0.0),
            "cae": f.cae,
            "renglones": [AjusteService._renglon_factura(fi) for fi in f.items],
        }

    # ------------------------------------------------------------------ candidatos

    @staticmethod
    def candidatos(db: Session, raw, enc: dict) -> dict:
        bloqueos = AjusteService._bloqueos_comprobante(db, enc)
        avisos = []
        clientes = ConciliadorService._clientes_del_cuit(db, enc["cuit"])
        if enc["cuit"] and not clientes:
            bloqueos.append(
                "CLIENTE_INEXISTENTE: ningún cliente del sistema tiene ese CUIT -- no hay facturas que ajustar "
                "ni a quién atribuir la nota.")
        if len(clientes) > 1:
            avisos.append(f"CUIT_COMPARTIDO: {len(clientes)} clientes comparten este CUIT -- elegí las facturas con cuidado.")
        facturas = AjusteService._facturas_ajustables(db, clientes)
        if clientes and not facturas and enc["clase_comprobante"] == ES_NC:
            bloqueos.append("SIN_FACTURAS: el cliente no tiene ninguna factura con CAE registrada que esta nota pueda ajustar.")
        if enc["clase_comprobante"] == ES_ND:
            avisos.append("ND_PUEDE_IR_SUELTA: una nota de débito sin factura asociada (intereses, gastos) se registra "
                          "sin elegir ninguna factura.")
        return {
            "modo": "AJUSTE",
            "raw_id": str(raw.id),
            "filename": raw.filename,
            "factura": enc,
            "facturas": [AjusteService._describir_factura(f) for f in facturas],
            "clientes": [{"id": str(c.id), "razon_social": c.razon_social} for c in clientes],
            "bloqueos": bloqueos,
            "avisos": avisos,
        }

    # ------------------------------------------------------------------ evaluar

    @staticmethod
    def evaluar(db: Session, raw_id, factura_ids: List[str], emparejamiento: Optional[List[dict]] = None,
                cliente_id=None) -> dict:
        """`emparejamiento`: [{"item_pdf": i, "factura_item_id": id | None}] -- solo para NC. Si no viene,
        se sugiere por nombre normalizado (solo coincidencia única). Un renglón sin par es un concepto."""
        from backend.facturacion.models import Factura
        from backend.remitos.service import RemitosService

        raw = ConciliadorService._raw(db, raw_id)
        parsed = _parsear(raw)
        pv, nc = RemitosService._partes_numero_factura(parsed.get("factura", {}).get("numero"))
        enc = ConciliadorService._encabezado(parsed, pv, nc)
        items_pdf = enc["items"]
        es_nc = enc["clase_comprobante"] == ES_NC

        bloqueos = AjusteService._bloqueos_comprobante(db, enc)
        diferencias: List[dict] = []
        avisos: List[str] = []

        # --- Cliente: por CUIT, nunca por razón social ---
        clientes = ConciliadorService._clientes_del_cuit(db, enc["cuit"])
        cliente = None
        if not clientes:
            if enc["cuit"]:
                bloqueos.append("CLIENTE_INEXISTENTE: ningún cliente del sistema tiene el CUIT de la nota.")
        elif cliente_id is not None:
            cliente = next((c for c in clientes if str(c.id).replace("-", "") == str(cliente_id).replace("-", "")), None)
            if cliente is None:
                bloqueos.append("CLIENTE_INVALIDO: el cliente elegido no tiene el CUIT de la nota.")
        elif len(clientes) == 1:
            cliente = clientes[0]

        # --- Facturas ajustadas ---
        facturas = []
        for fid in factura_ids or []:
            u = _uuid(fid)
            f = (db.query(Factura).options(joinedload(Factura.items)).filter(Factura.id == u).first()) if u else None
            if f is None:
                bloqueos.append(f"FACTURA_INEXISTENTE: {fid}")
                continue
            facturas.append(f)
            cuit_f = _norm_cuit(f.cuit_comprador or (f.cliente.cuit if f.cliente else None))
            if enc["cuit"] and cuit_f != enc["cuit"]:
                diferencias.append({
                    "clase": "C", "factura_id": str(f.id),
                    "detalle": (f"La nota es al CUIT {enc['cuit']} y la factura {f.numero_completo} es al CUIT "
                                f"{cuit_f or 'vacío'}: nota a otro cliente."),
                })
        if es_nc and not facturas:
            bloqueos.append("NC_SIN_FACTURA: una nota de crédito tiene que ajustar al menos una factura.")
        if not es_nc and not facturas and cliente is None and clientes:
            bloqueos.append(f"CLIENTE_A_ELEGIR: {len(clientes)} clientes comparten el CUIT -- elegí a cuál atribuir la nota de débito suelta.")
        if facturas:
            clientes_f = {f.cliente_id for f in facturas}
            if len(clientes_f) > 1:
                bloqueos.append("FACTURAS_DE_VARIOS_CLIENTES: las facturas elegidas son de clientes distintos.")
            elif cliente is None or cliente.id not in clientes_f:
                cliente = facturas[0].cliente
        for f in facturas:
            if (f.tipo_comprobante or "").startswith("NOTA_CREDITO"):
                bloqueos.append(f"AJUSTADA_ES_NC: {f.numero_completo} es una nota de crédito.")

        # --- Emparejamiento de renglones (solo NC; una ND no mueve cantidades) ---
        candidatos_fi = [fi for f in facturas for fi in f.items]
        por_id = {fi.id: fi for fi in candidatos_fi}
        sugerido = False
        if not es_nc:
            emparejamiento = [{"item_pdf": i, "factura_item_id": None, "como": None} for i in range(len(items_pdf))]
        elif emparejamiento is None:
            sugerido = True
            emparejamiento, usados = [], set()
            for i, it in enumerate(items_pdf):
                n = _norm_nombre(it.get("descripcion"))
                cands = [fi for fi in candidatos_fi if fi.id not in usados and _norm_nombre(fi.descripcion) == n]
                par = cands[0].id if len(cands) == 1 else None
                if par:
                    usados.add(par)
                emparejamiento.append({"item_pdf": i, "factura_item_id": par, "como": "nombre" if par else None})
        else:
            vistos_pdf, vistos_fi = set(), set()
            for e in emparejamiento:
                i, fid_item = e.get("item_pdf"), e.get("factura_item_id")
                if not isinstance(i, int) or i < 0 or i >= len(items_pdf) or i in vistos_pdf:
                    bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: renglón de la nota {i!r} fuera de rango o repetido.")
                    continue
                vistos_pdf.add(i)
                if fid_item is not None:
                    if fid_item not in por_id:
                        bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: el renglón de factura {fid_item} no es de las facturas elegidas.")
                    elif fid_item in vistos_fi:
                        bloqueos.append(f"EMPAREJAMIENTO_INVALIDO: el renglón de factura {fid_item} está usado dos veces.")
                    vistos_fi.add(fid_item)
            if len(vistos_pdf) != len(items_pdf):
                bloqueos.append("EMPAREJAMIENTO_INCOMPLETO: falta decidir el par (o 'sin par') de algún renglón de la nota.")

        # --- Diferencias por renglón (NC) ---
        sin_traza = False
        for e in emparejamiento:
            i = e.get("item_pdf")
            if not isinstance(i, int) or i >= len(items_pdf):
                continue
            it = items_pdf[i]
            fi = por_id.get(e.get("factura_item_id"))
            desc = it.get("descripcion") or f"renglón {i + 1}"
            if not es_nc:
                continue
            if fi is None:
                diferencias.append({"clase": "INFO", "item_pdf": i, "factura_item_id": None,
                                    "detalle": f"'{desc}' queda como concepto de solo monto: no ajusta cantidades de ningún renglón."})
                continue
            info = AjusteService._renglon_factura(fi)
            cant = it.get("cantidad") or 0
            if not info["trazable"]:
                sin_traza = True
            if info["disponible"] is not None and cant > info["disponible"] + EPS:
                diferencias.append({
                    "clase": "B", "item_pdf": i, "factura_item_id": fi.id, "remito_item_id": fi.remito_item_id,
                    "detalle": (f"'{fi.descripcion}': la nota acredita {cant} y solo quedaban {info['disponible']} "
                                f"sin acreditar (acreditó de más)."),
                })
            elif info["disponible"] is None and cant > (fi.cantidad or 0) + EPS:
                diferencias.append({
                    "clase": "B", "item_pdf": i, "factura_item_id": fi.id, "remito_item_id": fi.remito_item_id,
                    "detalle": f"'{fi.descripcion}': la nota acredita {cant} y la factura decía {fi.cantidad}.",
                })
        if sin_traza:
            avisos.append(
                "SIN_TRAZABILIDAD: alguna factura elegida es del camino viejo y no está atada a un renglón de PR: "
                "no se puede verificar cuánto ya se acreditó ni reflejarlo en el neto facturado del PR.")

        if es_nc and facturas and enc["total_final"] is not None:
            suma = sum(f.total or 0.0 for f in facturas)
            if enc["total_final"] > suma + 0.5:
                diferencias.append({
                    "clase": "B", "detalle": (f"La nota es por {enc['total_final']:.2f} y las facturas ajustadas suman "
                                              f"{suma:.2f} (acreditó de más).")})
        if enc.get("audit_warning"):
            diferencias.append({"clase": "AVISO", "detalle": enc["audit_warning"]})
        diferencias.append({"clase": "A", "detalle": (
            f"Se registra con los datos de ARCA: {enc['tipo_comprobante']} {enc['numero']}, emitida "
            f"{enc['fecha_emision'] or '(fecha ilegible: se usa hoy)'}, CAE {enc['cae']}.")})

        if any(d["clase"] == "C" for d in diferencias):
            bloqueos.append("CLASE_C: la nota es de otro cliente -- no se concilia.")

        return {
            "modo": "AJUSTE",
            "raw_id": str(raw.id),
            "factura": enc,
            "factura_ids": [str(f.id) for f in facturas],
            "cliente_id": str(cliente.id) if cliente else None,
            "emparejamiento": emparejamiento,
            "emparejamiento_sugerido": sugerido,
            "diferencias": diferencias,
            "bloqueos": bloqueos,
            "avisos": avisos,
            "_parsed": parsed,
            "_facturas": facturas,
            "_cliente": cliente,
            "_por_id": por_id,
        }

    # ------------------------------------------------------------------ confirmar

    @staticmethod
    def confirmar(db: Session, raw_id, factura_ids: List[str], emparejamiento: List[dict], usuario,
                  cliente_id=None, montos: Optional[Dict[str, float]] = None) -> dict:
        from backend.facturacion.models import Factura, FacturaItem
        from backend.facturacion.service import FacturacionService
        from backend.remitos.models import RemitoNota
        from backend.ingesta.models import FacturasProcesadas

        ev = AjusteService.evaluar(db, raw_id, factura_ids, emparejamiento, cliente_id)
        if ev["bloqueos"]:
            raise HTTPException(status_code=409, detail="; ".join(ev["bloqueos"]))

        enc, facturas, cliente, por_id = ev["factura"], ev["_facturas"], ev["_cliente"], ev["_por_id"]
        items_pdf = enc["items"]
        es_nc = enc["clase_comprobante"] == ES_NC
        neto, iva_21, iva_105, exento, percepciones, total = desglose_importes(enc, items_pdf)
        pedidos = {f.pedido_id for f in facturas if f.pedido_id is not None}

        try:
            nota = Factura(
                cliente_id=cliente.id,
                pedido_id=next(iter(pedidos)) if len(pedidos) == 1 else None,
                tipo_comprobante=enc["tipo_comprobante"],
                estado="AUTORIZADA_AFIP",
                punto_venta=enc["punto_venta"],
                numero_comprobante=enc["numero_comprobante"],
                fecha_emision=_fecha(enc["fecha_emision"]) or datetime.now().date(),
                neto_gravado=round(neto, 2), iva_21=round(iva_21, 2), iva_105=round(iva_105, 2),
                exento=round(exento, 2), percepciones=percepciones, total=round(total, 2),
                cae=enc["cae"], cae_vencimiento=_fecha(enc["vto_cae"]), cuit_comprador=enc["cuit"],
                notas_auditoria=(f"{enc['tipo_comprobante']} CONCILIADA (Etapa 7d) -- ingesta raw {raw_id}"
                                 + ("" if facturas else " -- ND suelta, sin factura asociada")),
            )
            db.add(nota)
            db.flush()

            par_por_item = {e["item_pdf"]: e.get("factura_item_id") for e in ev["emparejamiento"]}
            for i, it in enumerate(items_pdf):
                fi = por_id.get(par_por_item.get(i)) if es_nc else None
                db.add(FacturaItem(
                    factura_id=nota.id,
                    # Mismo renglón de PR que la factura: de ahí sale el neto (RemitoItem.cantidad_acreditada)
                    remito_item_id=fi.remito_item_id if fi else None,
                    pedido_item_id=fi.pedido_item_id if fi else None,
                    descripcion=it.get("descripcion") or f"Renglón {i + 1}",
                    cantidad=it.get("cantidad") or 0.0,
                    precio_unitario_neto=it.get("precio_unitario") or 0.0,
                    alicuota_iva=it.get("alicuota_iva") if it.get("alicuota_iva") is not None else 21.0,
                    subtotal_neto=it.get("subtotal") or 0.0,
                ))
            db.flush()

            montos = montos or {}
            ajustadas = []
            for f in facturas:
                monto = montos.get(str(f.id))
                if monto is None and len(facturas) == 1:
                    monto = round(total, 2)
                ajustadas.append({"factura_id": f.id, "monto_aplicado": monto})
            FacturacionService.registrar_ajuste(db, nota, ajustadas)

            # Clase B -> nota [SISTEMA] en el PR del renglón acreditado (si el renglón es trazable)
            referencia = f"{enc['tipo_comprobante']} {nota.numero_completo}"
            for d in ev["diferencias"]:
                if d["clase"] != "B" or d.get("remito_item_id") is None:
                    continue
                from backend.remitos.models import RemitoItem
                ri = db.query(RemitoItem).filter(RemitoItem.id == d["remito_item_id"]).first()
                if ri is not None:
                    db.add(RemitoNota(
                        remito_id=ri.remito_id, remito_item_id=ri.id, autor_id=getattr(usuario, "id", None),
                        texto=f"[SISTEMA] Conciliación con {referencia}: diferencia clase B -- {d['detalle']}",
                    ))

            raw = ConciliadorService._raw(db, raw_id)
            db.add(FacturasProcesadas(
                raw_id=raw.id, cliente_id=cliente.id, pedido_id=nota.pedido_id,
                numero_factura=enc["numero"], cae=enc["cae"], vto_cae=enc["vto_cae"],
                parsed_data_final=json.loads(json.dumps({**ev["_parsed"], "emparejamiento": ev["emparejamiento"],
                                                         "factura_ids": ev["factura_ids"]}, default=str)),
                audit_log={"diferencias": [dict(d) for d in ev["diferencias"]],
                           "usuario": getattr(usuario, "username", None)},
                estado="CONCILIADA_AJUSTE", processed_at=datetime.now(timezone.utc),
            ))
            raw.audit_status = "PROCESADO"
            raw.processed_at = datetime.now(timezone.utc)
            db.add(raw)
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(nota)
        return {
            "factura_id": str(nota.id),
            "tipo_comprobante": nota.tipo_comprobante,
            "numero": nota.numero_completo,
            "facturas_ajustadas": [str(f.id) for f in facturas],
            "diferencias": [dict(d) for d in ev["diferencias"]],
        }
