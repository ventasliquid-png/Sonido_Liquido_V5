# [IDENTIDAD] - backend/ingesta/facturas_panorama.py
# [S899, Card #212; Carlos 04/11: «Tomy no sabe si ya ingestó, por ejemplo, la 2612; no sabemos qué factura está ingresada a V5»]
# ------------------------------------------
"""Panorama de las facturas de ARCA en V5: qué está CARGADO, qué se SUBIÓ SIN TERMINAR y qué FALTA.

Solo lectura (salvo las marcas «no se carga a propósito»). Cada número de comprobante aparece en UN solo lugar:
  - cargadas:      hay una fila en `facturas` con ese número (tipo + punto de venta + número).
  - sin_terminar:  hay al menos un PDF subido (`ingesta_facturas_raw`) pero no hay factura con ese número. El PDF subido
                   de nuevo (el mismo número varias veces) cuenta como UNA, con «subida N veces»; los PDF repetidos de un número
                   que ya está cargado no cuentan (se informan como `repetidas_ignoradas`).
  - faltan:        números que no están ni cargados ni subidos, aunque hay otros posteriores en la misma serie (la numeración de
                   ARCA es correlativa: el hueco delata la que falta). V5 no ve ARCA: lo emitido DESPUÉS de lo último cargado o subido no se nota.
  - no_se_cargan:  números que se decidió no cargar (tabla `facturas_no_se_cargan`); no cuentan como hueco.

Los huecos se cuentan desde un CORTE por serie (Carlos 04/11: «desde la 2600»); lo anterior queda como histórico y no se muestra.
"""
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from backend.facturacion.models import Factura
from backend.ingesta.models import FacturaNoSeCarga, FacturasRaw

# Fecha de emisión de la 2600 (Carlos 04/11: los huecos se cuentan desde la 2600).
CORTE_FECHA = date(2026, 9, 8)
# Corte explícito por serie (tipo, punto de venta). Las series que no figuran acá arrancan en el primer número cargado desde CORTE_FECHA.
CORTE_NUMERO: Dict[Tuple[str, int], int] = {("FACTURA_A", 1): 2600}

# Código de comprobante de ARCA en el nombre del PDF («CUIT_001_00001_00002612 ...»).
_COD_ARCA = {"001": "FACTURA_A", "006": "FACTURA_B", "011": "FACTURA_C",
             "002": "NOTA_DEBITO_A", "003": "NOTA_CREDITO_A", "007": "NOTA_DEBITO_B", "008": "NOTA_CREDITO_B"}
_NOMBRE_ARCHIVO = re.compile(r"^\d{11}_(\d{3})_\d{5}_\d{8}")

_TEXTO_TIPO = {"FACTURA_A": "Factura A", "FACTURA_B": "Factura B", "FACTURA_C": "Factura C",
               "NOTA_CREDITO_A": "Nota de crédito A", "NOTA_CREDITO_B": "Nota de crédito B",
               "NOTA_DEBITO_A": "Nota de débito A", "NOTA_DEBITO_B": "Nota de débito B"}

_TEXTO_ESTADO_RAW = {
    "RECIBIDO": "Subida, falta conciliar",
    "PROCESANDO": "Quedó a medio camino",
    "ERROR": "Con error al leerla",
    "CUARENTENA": "En cuarentena",
    "PROCESADO": "Procesada, pero no figura la factura",
}


def texto_tipo(tipo: Optional[str]) -> str:
    return _TEXTO_TIPO.get(tipo or "", (tipo or "¿?").replace("_", " ").capitalize())


def numero_legal(pv: Optional[int], numero: Optional[int]) -> str:
    return f"{int(pv or 0):04d}-{int(numero or 0):08d}"


def _partes_numero(texto: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """(punto de venta, número) de «00001-00002612» / «0001-00002612» / «2612». (None, None) si no se entiende."""
    t = (texto or "").strip()
    partes = t.split("-") if "-" in t else t.split()
    try:
        if len(partes) >= 2:
            return int(partes[0]), int(partes[-1])
        if len(partes) == 1 and partes[0].isdigit():
            return None, int(partes[0])
    except ValueError:
        pass
    return None, None


def _tipo_de_raw(filename: Optional[str], parsed: dict) -> str:
    """El tipo con que V5 guarda la factura de este PDF: la NC/ND por lo que leyó el parser; si no, el código de ARCA del nombre del archivo;
    si no, la misma suposición de siempre por condición de IVA (como `upload_raw`)."""
    f = parsed.get("factura") or {}
    if f.get("clase_comprobante") in ("NOTA_CREDITO", "NOTA_DEBITO") and f.get("tipo_comprobante"):
        return f["tipo_comprobante"]
    m = _NOMBRE_ARCHIVO.match(filename or "")
    if m and m.group(1) in _COD_ARCA:
        return _COD_ARCA[m.group(1)]
    cond = ((parsed.get("cliente") or {}).get("condicion_iva") or "").upper()
    if "INSCRIPTO" in cond:
        return "FACTURA_A"
    if "MONOTRIBUTO" in cond:
        return "FACTURA_C"
    return "FACTURA_B"


def _fecha_texto(valor: Any) -> Optional[str]:
    if valor is None:
        return None
    if hasattr(valor, "isoformat"):
        return valor.isoformat()[:10]
    return str(valor)[:10]


def _lista_raws(db: Session) -> List[dict]:
    """Un dict liviano por PDF subido (sin traer los bytes del PDF)."""
    filas = db.query(FacturasRaw.id, FacturasRaw.filename, FacturasRaw.audit_status, FacturasRaw.audit_warning,
                     FacturasRaw.parsed_data_raw, FacturasRaw.created_at).all()
    out = []
    for rid, filename, estado, warning, parsed, creado in filas:
        parsed = parsed if isinstance(parsed, dict) else {}
        f = parsed.get("factura") or {}
        pv, nro = _partes_numero(f.get("numero"))
        if nro is None:  # sin número leído: probar con el nombre del archivo («CUIT_001_00001_00002612 ...»)
            m = re.match(r"^\d{11}_\d{3}_(\d{5})_(\d{8})", filename or "")
            if m:
                pv, nro = int(m.group(1)), int(m.group(2))
        tipo = _tipo_de_raw(filename, parsed) if nro is not None else None
        out.append({
            "raw_id": str(rid), "filename": filename, "estado": estado or "RECIBIDO", "warning": warning,
            "tipo": tipo, "punto_venta": pv, "numero": nro,
            "cliente": (parsed.get("cliente") or {}).get("razon_social"),
            "total": f.get("total_final"),
            "fecha_emision": f.get("fecha_emision"),
            "subida": creado, "creado_iso": creado.isoformat() if creado else None,
        })
    return out


def panorama(db: Session) -> Dict[str, Any]:
    # --- lo que V5 tiene cargado (solo comprobantes de ARCA: sin presupuestos X ni sin número) ---
    facturas = db.query(Factura).filter(
        Factura.tipo_comprobante != "PRESUPUESTO_X",
        Factura.numero_comprobante.isnot(None),
        Factura.punto_venta.isnot(None),
    ).all()
    cargadas_clave = {(f.tipo_comprobante, int(f.punto_venta), int(f.numero_comprobante)): f for f in facturas}

    marcas = db.query(FacturaNoSeCarga).order_by(FacturaNoSeCarga.tipo_comprobante, FacturaNoSeCarga.numero_comprobante).all()
    marcadas_clave = {(m.tipo_comprobante, m.punto_venta, m.numero_comprobante): m for m in marcas}

    raws = _lista_raws(db)
    raws_por_clave: Dict[Tuple[str, int, int], List[dict]] = {}
    sin_numero: List[dict] = []
    for r in raws:
        if r["numero"] is None:
            sin_numero.append(r)
            continue
        raws_por_clave.setdefault((r["tipo"], r["punto_venta"] if r["punto_venta"] is not None else 0, r["numero"]), []).append(r)

    # --- corte de cada serie ---
    series = {(t, pv) for (t, pv, _n) in cargadas_clave} | {(t, pv) for (t, pv, _n) in raws_por_clave}
    corte: Dict[Tuple[str, int], int] = {}
    for serie in series:
        if serie in CORTE_NUMERO:
            corte[serie] = CORTE_NUMERO[serie]
            continue
        desde = [n for (t, pv, n), f in cargadas_clave.items() if (t, pv) == serie and f.fecha_emision and f.fecha_emision >= CORTE_FECHA]
        desde += [n for (t, pv, n), lst in raws_por_clave.items() if (t, pv) == serie and any((x["subida"] and x["subida"].date() >= CORTE_FECHA) for x in lst)]
        if desde:
            corte[serie] = min(desde)

    def _visible(t, pv, n):
        c = corte.get((t, pv))
        return c is not None and n >= c

    # --- PDF de cada comprobante: el de una subida procesada si hay, si no el último ---
    def _raw_para_pdf(clave) -> Optional[str]:
        lst = raws_por_clave.get(clave) or []
        if not lst:
            return None
        procesadas = [x for x in lst if x["estado"] == "PROCESADO"]
        elegido = max(procesadas or lst, key=lambda x: x["creado_iso"] or "")
        return elegido["raw_id"]

    # --- 1. CARGADAS ---
    cargadas = []
    for (t, pv, n), f in cargadas_clave.items():
        if not _visible(t, pv, n):
            continue
        remitos = []
        for v in (f.vinculos_remitos or []):
            if v.remito is not None:
                remitos.append({"id": str(v.remito.id), "numero_legal": v.remito.numero_legal, "estado": v.remito.estado})
        cargadas.append({
            "factura_id": str(f.id), "tipo": t, "tipo_texto": texto_tipo(t), "punto_venta": pv, "numero": n,
            "numero_legal": numero_legal(pv, n), "fecha_emision": _fecha_texto(f.fecha_emision),
            "cliente": f.cliente.razon_social if f.cliente else None, "cliente_id": str(f.cliente_id) if f.cliente_id else None,
            "total": f.total, "estado": f.estado,
            "pedido_id": int(f.pedido_id) if f.pedido_id is not None else None,   # en P viene guardado como texto ('150'): se devuelve siempre número
            "remitos": remitos,
            "raw_id": _raw_para_pdf((t, pv, n)),
        })
    cargadas.sort(key=lambda x: (x["fecha_emision"] or "", x["numero"]), reverse=True)

    # --- 2. SUBIDAS SIN TERMINAR (y 'repetidas ignoradas': PDF de números que ya están cargados) ---
    sin_terminar = []
    repetidas_ignoradas = 0
    for clave, lst in raws_por_clave.items():
        t, pv, n = clave
        if clave in cargadas_clave:
            if _visible(t, pv, n):
                repetidas_ignoradas += sum(1 for x in lst if x["estado"] != "PROCESADO")
            continue
        if clave in marcadas_clave or not _visible(t, pv, n):
            continue
        ultima = max(lst, key=lambda x: x["creado_iso"] or "")
        sin_terminar.append({
            "raw_id": ultima["raw_id"], "tipo": t, "tipo_texto": texto_tipo(t), "punto_venta": pv, "numero": n,
            "numero_legal": numero_legal(pv, n), "cliente": ultima["cliente"], "total": ultima["total"],
            "fecha_emision": ultima["fecha_emision"], "subida": ultima["creado_iso"], "veces": len(lst),
            "estado": ultima["estado"], "estado_texto": _TEXTO_ESTADO_RAW.get(ultima["estado"], ultima["estado"]),
            "warning": ultima["warning"], "filename": ultima["filename"],
        })
    for r in sin_numero:  # un PDF que no se pudo leer: que no quede invisible
        if r["subida"] and r["subida"].date() >= CORTE_FECHA and r["estado"] != "PROCESADO":
            sin_terminar.append({
                "raw_id": r["raw_id"], "tipo": None, "tipo_texto": "¿Comprobante?", "punto_venta": None, "numero": None,
                "numero_legal": "sin número legible", "cliente": r["cliente"], "total": r["total"], "fecha_emision": r["fecha_emision"],
                "subida": r["creado_iso"], "veces": 1, "estado": r["estado"],
                "estado_texto": _TEXTO_ESTADO_RAW.get(r["estado"], r["estado"]), "warning": r["warning"], "filename": r["filename"],
            })
    sin_terminar.sort(key=lambda x: x["subida"] or "", reverse=True)

    # --- 3. FALTAN (huecos de la numeración) ---
    faltan = []
    for (t, pv) in sorted(corte, key=lambda s: (s[0], s[1])):
        desde = corte[(t, pv)]
        presentes = {n for (tt, pp, n) in cargadas_clave if (tt, pp) == (t, pv)} | {n for (tt, pp, n) in raws_por_clave if (tt, pp) == (t, pv)}
        tope = max((n for n in presentes if n >= desde), default=None)   # el tope lo marcan los cargados y los subidos, no las marcas «no se carga»
        if tope is None:
            continue
        presentes |= {n for (tt, pp, n) in marcadas_clave if (tt, pp) == (t, pv)}
        cargados_serie = sorted((n, f) for (tt, pp, n), f in cargadas_clave.items() if (tt, pp) == (t, pv))
        for n in range(desde, tope + 1):
            if n in presentes:
                continue
            ant = next(((x, f) for x, f in reversed(cargados_serie) if x < n), None)
            sig = next(((x, f) for x, f in cargados_serie if x > n), None)
            faltan.append({
                "tipo": t, "tipo_texto": texto_tipo(t), "punto_venta": pv, "numero": n, "numero_legal": numero_legal(pv, n),
                "anterior": {"numero": ant[0], "fecha": _fecha_texto(ant[1].fecha_emision)} if ant else None,
                "siguiente": {"numero": sig[0], "fecha": _fecha_texto(sig[1].fecha_emision)} if sig else None,
            })

    # --- 4. NO SE CARGAN (todas las marcas, para poder deshacerlas) ---
    no_se_cargan = [{
        "id": m.id, "tipo": m.tipo_comprobante, "tipo_texto": texto_tipo(m.tipo_comprobante), "punto_venta": m.punto_venta,
        "numero": m.numero_comprobante, "numero_legal": numero_legal(m.punto_venta, m.numero_comprobante),
        "motivo": m.motivo, "decidido_por": m.decidido_por, "fecha": _fecha_texto(m.created_at),
    } for m in marcas]

    return {
        "corte": [{"tipo": t, "tipo_texto": texto_tipo(t), "punto_venta": pv, "desde": d, "desde_legal": numero_legal(pv, d)}
                  for (t, pv), d in sorted(corte.items())],
        "resumen": {"cargadas": len(cargadas), "sin_terminar": len(sin_terminar), "faltan": len(faltan), "no_se_cargan": len(no_se_cargan),
                    "repetidas_ignoradas": repetidas_ignoradas},
        "cargadas": cargadas, "sin_terminar": sin_terminar, "faltan": faltan, "no_se_cargan": no_se_cargan,
    }


class MarcaError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def marcar_no_se_carga(db: Session, tipo: str, punto_venta: int, numero: int, motivo: str, quien: Optional[str]) -> FacturaNoSeCarga:
    motivo = (motivo or "").strip()
    if not motivo:
        raise MarcaError(400, "MOTIVO_REQUERIDO: escribí por qué no se carga (queda anotado).")
    if not tipo or not punto_venta or not numero:
        raise MarcaError(400, "COMPROBANTE_INCOMPLETO: falta el tipo, el punto de venta o el número.")
    if db.query(Factura).filter(Factura.tipo_comprobante == tipo, Factura.punto_venta == punto_venta,
                                Factura.numero_comprobante == numero).first():
        raise MarcaError(409, "YA_ESTA_CARGADA: esa factura ya está en V5; no se puede marcar como «no se carga».")
    if db.query(FacturaNoSeCarga).filter(FacturaNoSeCarga.tipo_comprobante == tipo, FacturaNoSeCarga.punto_venta == punto_venta,
                                         FacturaNoSeCarga.numero_comprobante == numero).first():
        raise MarcaError(409, "YA_ESTA_MARCADA: ese número ya figura como «no se carga».")
    m = FacturaNoSeCarga(tipo_comprobante=tipo, punto_venta=punto_venta, numero_comprobante=numero, motivo=motivo, decidido_por=quien)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def desmarcar_no_se_carga(db: Session, marca_id: int) -> None:
    m = db.query(FacturaNoSeCarga).filter(FacturaNoSeCarga.id == marca_id).first()
    if not m:
        raise MarcaError(404, "MARCA_NO_ENCONTRADA")
    db.delete(m)
    db.commit()
