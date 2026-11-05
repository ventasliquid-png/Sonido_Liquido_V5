"""[S900, Card #215; Nike, Sello de Oro 05/11/2026] Registro de TODO cambio de estado de un pedido.

Por qué existe: un pedido Cumplido limpio se reabría (y se re-cerraba) sin dejar rastro en el pedido: el aviso «salió de Cumplido» solo se escribía si ya tenía la marca de ajuste
(bit 46), y las notas no llevaban usuario. Caso real, pedido #98 (04-05/11/2026): el cierre dio por salidos 60 paquetes que no salieron, se reabrió, se corrigió y se re-cerró; en el
pedido quedó una sola línea. Y `pedido.nota` es un texto libre que el operador guarda ENTERO desde la ficha, así que puede borrar las líneas [SISTEMA].

Dictamen de Nike (CONSULTA_NIKE_reapertura_cumplido_2026-11-05.md):
  - Toda transición de estado escribe en la nota: «[SISTEMA] Cambio de estado: {anterior} ➔ {nuevo} por {usuario} a las {HH:MM DD/MM/AAAA}.»
  - Bit 50, FUE_REABIERTO: cicatriz que se prende al SALIR de CUMPLIDO hacia cualquier estado (Pendiente, Presupuesto o Anulado), en el instante de reabrir (no al re-cerrar), una sola
    vez y para siempre. Anulado → Pendiente NO lo prende. Lo escribe el servidor; ninguna pantalla lo toca.

Uso: cambiar el estado del pedido (pedido.flags_estado) y llamar `registrar_cambio_de_estado(pedido, flags_de_antes, usuario)`. Si el estado no cambió no hace nada.
"""
from datetime import datetime
from typing import Optional

from backend.pedidos.constants import PedidoFlags as PF, STATE_MASK

_NOMBRES = {
    int(PF.ES_PRESUPUESTO): "PRESUPUESTO",
    int(PF.ES_FIRME): "PENDIENTE",
    int(PF.ES_CUMPLIDO): "CUMPLIDO",
    int(PF.ES_ANULADO): "ANULADO",
}
SIN_SESION = "(sin sesión)"


def estado_de_flags(flags) -> int:
    """El bit de estado (uno de los cuatro excluyentes de STATE_MASK) de unos flags; 0 si no tiene."""
    return int(flags or 0) & int(STATE_MASK)


def nombre_de_estado(flags) -> str:
    return _NOMBRES.get(estado_de_flags(flags), "SIN ESTADO")


def registrar_cambio_de_estado(pedido, flags_antes, usuario: Optional[str] = None, ahora: Optional[datetime] = None) -> Optional[str]:
    """Llamar DESPUÉS de poner el estado nuevo en `pedido.flags_estado`, pasando los flags de ANTES. Si el estado cambió: agrega la línea [SISTEMA] a la nota del pedido
    (con quién y cuándo) y, si venía de CUMPLIDO, prende FUE_REABIERTO. Devuelve la línea escrita, o None si no hubo cambio de estado."""
    antes, despues = estado_de_flags(flags_antes), estado_de_flags(pedido.flags_estado)
    if antes == despues:
        return None
    ahora = ahora or datetime.now()
    linea = (f"[SISTEMA] Cambio de estado: {_NOMBRES.get(antes, 'SIN ESTADO')} ➔ {_NOMBRES.get(despues, 'SIN ESTADO')} "
             f"por {usuario or SIN_SESION} a las {ahora.strftime('%H:%M %d/%m/%Y')}.")
    pedido.nota = (pedido.nota or "") + "\n" + linea
    if antes == int(PF.ES_CUMPLIDO):
        pedido.flags_estado = int(pedido.flags_estado or 0) | int(PF.FUE_REABIERTO)
    return linea
