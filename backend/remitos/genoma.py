"""
[S891, Nike Sello de Oro 22/10] Genoma del remito: clase, estado, logística y calificadores (RemitoFlags, bits 29-45).

UNA sola función calcula los bits a partir de los hechos del remito (número, estado, fechas, color del pedido, renglones). La usan
el servidor (en cada guardado, por el evento before_flush de abajo) y la migración que los completa en los remitos que ya existen
(scripts/migrate_066_remitos_genoma_fecha_emision.py). Nadie prende estos bits a mano: así no pueden contradecir a los hechos
(la enfermedad de los Bits 20/21 de los pedidos). Este módulo no importa nada de la base para que la migración lo pueda usar suelto.

Reglas (CONSULTA_NIKE_genoma_remito_2026-10-22.md, DISENO_REMITOS_S889.md):
- CLASE: la numeración dice el color. Número «RI-» = INTERNO (Rosa); otro número (0015, 0016) = EGRESO, o EGRESO_AVIOS si el pedido
  es no comercial. Sin número, por el pedido: no comercial = EGRESO_AVIOS; Rosa = INTERNO (tomará número RI); si no, EGRESO.
  [S894, H15] Una vez numerado, la clase y el bit 46 quedan fijos en el guardado de todos los días (ver sincronizar).
- ESTADO: ANULADO (y la cicatriz FUE_ANULADO) si el estado es ANULADO; PERDIDO si es PERDIDO; si no, EMITIDO cuando tiene número.
  Sin número = indeterminado (ningún bit de estado).
- LOGÍSTICA (solo EMITIDO, ni anulado ni perdido): ENTREGADO -> RECIBIDO; EN_CAMINO -> RETIRADO; marcado EN_DEPOSITO y todavía sin
  fecha de salida -> EN_DEPOSITO; si no -> RETIRADO (Carlos: «si queda en blanco se asume», hasta que exista Stock).
- CALIFICADORES (irreversibles: nunca se apagan acá): FUE_ANULADO, IMPRESO (lo marca quien imprime), DIFERENCIA_RECEPCION (algún
  renglón con recibido distinto de remitido), SALIDA_DIFERIDA (la salida física es de un día posterior a la emisión).
- [S892, Nike 23/10] CIRCULACION_ROSA: un 0015 (número que no es RI-) de un pedido Rosa: EGRESO más este bit; no se factura.
  SALIDA_CONFIRMADA: una persona confirmó que salió: el remito pasó a EN_CAMINO (Despachar, «Retiró el transporte») o a ENTREGADO
  (mostrador, copia firmada), o el operador lo declaró («Salió sin papel»: lo prende el endpoint). Sin el bit, RETIRADO es la salida
  asumida al emitir; imprimir NO la confirma. Con RETIRADO sin SALIDA_CONFIRMADA se lee el desfase entre lo contable y el stock.
"""
from datetime import datetime
from typing import Optional

from backend.remitos.constants import RemitoFlags as F, MASCARA_CLASE, MASCARA_ESTADO, MASCARA_LOGISTICA

PEDIDO_ES_NO_COMERCIAL = 1 << 11   # PedidoFlags.ES_NO_COMERCIAL
PEDIDO_NO_FISCAL_FORCE = 1 << 12   # PedidoFlags.NO_FISCAL_FORCE (Rosa)
EPS = 1e-6


def _fecha(valor) -> Optional[datetime]:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor
    texto = str(valor).replace("T", " ")
    for formato in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto[:26], formato)
        except ValueError:
            continue
    return None


def calcular_flags(flags_actuales, numero_legal, estado, pedido_flags, fecha_emision=None, fecha_salida=None,
                   hay_diferencia_recepcion: bool = False, impreso: bool = False) -> int:
    """Devuelve el flags_estado del remito con clase, estado, logística y calificadores recalculados. Conserva los demás bits."""
    previos = int(flags_actuales or 0)
    f = previos & ~(MASCARA_CLASE | MASCARA_ESTADO | MASCARA_LOGISTICA)
    num = (numero_legal or "").strip().upper()
    pf = int(pedido_flags or 0)
    no_comercial = bool(pf & PEDIDO_ES_NO_COMERCIAL)
    rosa = bool(pf & PEDIDO_NO_FISCAL_FORCE)

    if num.startswith("RI-"):
        f |= int(F.INTERNO)
    elif num:
        f |= int(F.EGRESO_AVIOS if no_comercial else F.EGRESO)
    else:
        f |= int(F.EGRESO_AVIOS if no_comercial else (F.INTERNO if rosa else F.EGRESO))

    est = (estado or "").strip().upper()
    if est == "ANULADO":
        f |= int(F.ANULADO | F.FUE_ANULADO)
    elif est == "PERDIDO":
        f |= int(F.PERDIDO)
    elif num:
        f |= int(F.EMITIDO)

    if f & int(F.EMITIDO):
        if est == "ENTREGADO":
            f |= int(F.RECIBIDO)
        elif est == "EN_CAMINO":
            f |= int(F.RETIRADO)
        elif (previos & int(F.EN_DEPOSITO)) and fecha_salida is None:
            f |= int(F.EN_DEPOSITO)
        else:
            f |= int(F.RETIRADO)

    if num and not num.startswith("RI-") and rosa:
        f |= int(F.CIRCULACION_ROSA)
    if num and est in ("EN_CAMINO", "ENTREGADO"):
        f |= int(F.SALIDA_CONFIRMADA)
    if impreso:
        f |= int(F.IMPRESO)
    if hay_diferencia_recepcion:
        f |= int(F.DIFERENCIA_RECEPCION)
    fe, fs = _fecha(fecha_emision), _fecha(fecha_salida)
    if fe and fs and fs.date() > fe.date():
        f |= int(F.SALIDA_DIFERIDA)
    return f


def diferencia_recepcion(items) -> bool:
    """True si algún renglón tiene recibido cargado y distinto de lo remitido. `items`: [(remitida, recibida), ...]."""
    return any(rec is not None and abs(float(rec) - float(rem or 0)) > EPS for rem, rec in items)


def sincronizar(remito) -> None:
    """Recalcula el genoma de un Remito del ORM (lo llama el evento before_flush; también sirve suelto).

    [S894, hallazgo H15 de CA; Carlos 27/10] La clase y CIRCULACION_ROSA (bit 46) los fija el NÚMERO: un remito que ya estaba numerado
    (tiene un bit de estado) conserva la clase y el 46 con los que salió, aunque el pedido cambie después de color o de comercial (Carlos:
    «siempre es posible que un cliente pase a Rosa, incluso cuando haya firmado un 0015 y tenga una factura», y al revés). Sin el freno,
    un ida y vuelta Blanco -> Rosa -> Blanco dejaba prendido el 46 en un remito que nunca fue Rosa. La congelación va acá y no en
    calcular_flags porque las migraciones (066, 067) reconstruyen el genoma desde los hechos de hoy y tienen que poder recalcularlo."""
    pedido = getattr(remito, "pedido", None)
    pf = getattr(pedido, "flags_estado", 0) if pedido is not None else 0
    items = [(ri.cantidad_remitida, ri.cantidad_recibida) for ri in (getattr(remito, "items", None) or [])]
    previos = int(remito.flags_estado or 0)
    nuevos = calcular_flags(previos, remito.numero_legal, remito.estado, pf,
                            getattr(remito, "fecha_emision", None), remito.fecha_salida,
                            diferencia_recepcion(items))
    fijos = MASCARA_CLASE | int(F.CIRCULACION_ROSA)
    if (remito.numero_legal or "").strip() and previos & MASCARA_ESTADO and previos & MASCARA_CLASE:
        nuevos = (nuevos & ~fijos) | (previos & fijos)
    remito.flags_estado = nuevos


def describir(flags) -> dict:
    """Lectura humana del genoma (para pantallas, informes y pruebas)."""
    f = int(flags or 0)
    clase = next((n for n, b in (("EGRESO", F.EGRESO), ("EGRESO_AVIOS", F.EGRESO_AVIOS), ("INTERNO", F.INTERNO)) if f & int(b)), None)
    estado = next((n for n, b in (("EMITIDO", F.EMITIDO), ("ANULADO", F.ANULADO), ("PERDIDO", F.PERDIDO)) if f & int(b)), None)
    logistica = next((n for n, b in (("EN_DEPOSITO", F.EN_DEPOSITO), ("RETIRADO", F.RETIRADO), ("RECIBIDO", F.RECIBIDO)) if f & int(b)), None)
    marcas = [n for n, b in (("DIFERENCIA_RECEPCION", F.DIFERENCIA_RECEPCION), ("FUE_ANULADO", F.FUE_ANULADO),
                             ("IMPRESO", F.IMPRESO), ("SALIDA_DIFERIDA", F.SALIDA_DIFERIDA), ("CIRCULACION_ROSA", F.CIRCULACION_ROSA),
                             ("SALIDA_CONFIRMADA", F.SALIDA_CONFIRMADA)) if f & int(b)]
    return {"clase": clase, "estado": estado, "logistica": logistica, "marcas": marcas,
            "activo": bool(clase) and not (f & int(F.ANULADO | F.PERDIDO))}
