from enum import IntFlag

class PedidoFlags(IntFlag):
    """
    Genoma 64-bit del Pedido V6 — canonizado por Nike Arq 5.5
    Banda baja reservada para bits universales y Motor Bipolar.
    Banda 32+ para ciclo de vida y auditoría forense del pedido.
    """
    NOTHING      = 0
    EXISTENCE    = 1 << 0   # Bit 0 — existencia lógica
    HAS_ACTIVITY = 1 << 1   # Bit 1 — Ley Universal: marca de actividad/virginidad. Bit 1 no está libre en ninguna entidad del sistema.

    # Bits bajos preexistentes — INTOCABLES
    PEDIDO_DUPLICATE_CONFIRMED = 1 << 6   # Bit 6
    INGESTA_CON_CORRECCION     = 1 << 9   # Bit 9
    ES_NO_COMERCIAL            = 1 << 11  # 2048 — Bypass comercial: muestras, uso interno
                                           # Banda de Excepciones junto a NO_FISCAL_FORCE (Bit 12)
                                           # Reversible con nota forense obligatoria (Nike S836)
    NO_FISCAL_FORCE            = 1 << 12  # Bit 12 — Motor Bipolar soberano
    # Bit 13 PROHIBIDO — colisión LAVIMAR
    # Bit 20 — Pedido tiene ítems con entrega parcial pendiente.
    # Se enciende automáticamente al crear remito que no cubre el total de algún ítem.
    # Se apaga cuando todos los ítems están cubiertos al 100%. Canonizado Nike S833.
    HAS_PARTIAL_DELIVERY = 1 << 20
    # Bit 21 — Entrega física completa. Se enciende cuando TODOS los ítems tienen
    # cantidad_entregada >= cantidad. Se apaga si se anula un remito y vuelve a haber pendiente.
    # Canonizado Nike S833.
    FULL_DELIVERED = 1 << 21
    HAS_PARTIAL_INVOICE  = 1 << 22  # 4194304  — Facturas parciales en curso (Nike S836)
    FULL_INVOICED        = 1 << 23  # 8388608  — Facturación completa / COMMERCIALLY_CLEARED
                                     #            Rosa: confirmado por operador
                                     #            Blanco: confirmado por Sabueso ARCA
    # Bit 40 PROHIBIDO — DISCRIMINA_IVA del cliente

    # BANDA 32+ — Estados mutuamente excluyentes
    # Patrón obligatorio en toda transición:
    # flags = (flags & ~STATE_MASK) | ES_NUEVO_ESTADO
    ES_PRESUPUESTO  = 1 << 32  # Cotización formal, sin color aún
    ES_FIRME        = 1 << 33  # Pedido confirmado (blanco o negro)
    ES_CUMPLIDO     = 1 << 34  # Entregado y cerrado
    ES_ANULADO      = 1 << 35  # Baja lógica del documento

    # BANDA 32+ — Flags ortogonales acumulables
    RESERVA_STOCK      = 1 << 36  # Stock comprometido desde presupuesto
    TUVO_CIRCUITO      = 1 << 37  # Forense: tuvo vida operativa real
    ORIGEN_FACTURA     = 1 << 38  # Nació desde ingesta ARCA
    ORIGEN_RETROACTIVO = 1 << 39  # Creado post-hecho
    # Bit 40 PROHIBIDO
    CAMBIO_A_NEGRO     = 1 << 41  # Cicatriz: nació blanco, operó negro
    CAMBIO_A_BLANCO    = 1 << 42  # Cicatriz: nació negro, operó blanco
    PEDIDO_GHOST       = 1 << 43  # Bit 43 — operado sin rastro (auditoría)
    # Bit 44 — RESERVADO por Nike (dictamen "Protocolo de Evolución del Genoma
    # V5-X - Bits 44 y 45", NIKE_BACKUP): ES_ENTREGADO, nuevo estado de
    # STATE_MASK (ES_PRESUPUESTO → ES_FIRME → ES_ENTREGADO → ES_CUMPLIDO).
    # NO IMPLEMENTADO — fuera de alcance de S863 (dictamen explícito: no tocar
    # UI de despacho/cobranzas en este sprint). No reutilizar este número.
    # Bit 45 — RESERVADO por Nike, mismo dictamen: COBRADO, evento financiero
    # ortogonal e irreversible. NO IMPLEMENTADO — mismo motivo que el 44.
    # Bit 46 — Cicatriz: se ajustó la cantidad de al menos un renglón después de
    # tener entrega real registrada (tolerancia de fabricación, cliente pidió
    # menos/más a mitad de entrega, etc.). "Pedido Soberano" pero lo fáctico es
    # regla cero: el operador ajusta el papel a lo que realmente pasó. Se prende
    # una sola vez y queda para siempre — marca de búsqueda/auditoría, no un
    # estado reversible. El detalle de qué renglón/cuánto queda en pedido.nota
    # (nota forense auto-generada, ver update_pedido_item() en router.py).
    # Canonizado por Nike (Sello de Oro) S863 (caso OC LPC, tolerancia 7%) —
    # asignado a 46 en vez de 44 por colisión con ES_ENTREGADO (ver arriba).
    CIERRE_CON_AJUSTE  = 1 << 46
    # Bit 47 — ES_KIT (140737488355328). Ratificado por Nike (Sello de Oro) el 16/10/2026 y rediseñado el 19/10/2026 (Card #177 v3): el PEDIDO tiene al menos un kit válido
    # (2 o más renglones con el mismo PedidoItem.kit_grupo). Calificador ortogonal de la banda 32+, fuera de STATE_MASK. Lo calcula el SERVIDOR (backend/pedidos/kits.py,
    # sincronizar_bit_kit) y nadie lo escribe a mano; reversible mientras el pedido no esté CUMPLIDO ni ANULADO (después queda congelado). Regla: ES_KIT exige al menos un kit
    # válido; el descuento del kit puede ser 0. NO confundir con ProductoFlags.IS_KIT (bit 6) ni ES_PACK (bit 11), que son del PRODUCTO.
    ES_KIT             = 1 << 47
    # Bit 48 — FLETE_A_CARGO_NUESTRO (281474976710656). Ratificado por Nike (Sello de Oro) el 26/10/2026 (consulta de Carlos + NS: CONSULTA_NIKE_flete_a_cargo_y_atencion_2026-10-26.md).
    # Quién carga con lo que se pierde en el camino: apagado (el normal, y el de todos los pedidos viejos) el flete es del cliente (retira, su transporte, su moto): lo entregado a su
    # transporte ya es suyo, se factura lo que salió y el pedido no vuelve a deber; prendido el flete es nuestro (vehículo o moto nuestros, o un transporte que pagamos nosotros): la
    # pérdida es nuestra, se factura lo que llegó y el pedido vuelve a deber. Lo prende y apaga una PERSONA (PATCH /pedidos/{id}/flete-a-cargo); ortogonal, fuera de STATE_MASK;
    # editable mientras el pedido no tenga remitos vigentes y CONGELADO después (un error propio —dimos O3 en vez de E2— se resuelve con un pedido NUEVO con el bit prendido).
    # El remito lo lee de su pedido: no lleva copia.
    FLETE_A_CARGO_NUESTRO = 1 << 48
    # Bit 49 — REQUIERE_ATENCION (562949953421312). Ratificado por Nike (Sello de Oro) el 26/10/2026: «hay que mirar las notas». Lo prende y lo apaga una PERSONA, siempre con una nota que
    # explica el motivo (al apagar: «[SISTEMA] Atención resuelta por X»); reversible; sin cicatriz «tuvo atención» (Nike: la nota ya lo certifica). Hoy solo está reservado el número:
    # su pantalla y su endpoint los define Carlos con CA.
    REQUIERE_ATENCION     = 1 << 49

# Máscara de estados excluyentes
STATE_MASK = (
    PedidoFlags.ES_PRESUPUESTO |
    PedidoFlags.ES_FIRME       |
    PedidoFlags.ES_CUMPLIDO    |
    PedidoFlags.ES_ANULADO
)

# [S894, Carlos 28/10] Compuerta financiera del despacho (S876, «Liberar despacho»; el remito nace con aprobado_para_despacho = pedido.liberado_despacho
# y «Despachar» frena si no está aprobado). Carlos: «es algo a prender cuando el sistema de crédito y la contabilidad esté armada; ahora es
# ponerle "Seguí" a todo». Apagada: el remito nace aprobado, «Despachar» no la mira y las pantallas no muestran el cartel. Se lee en el momento
# (pedidos_constants.COMPUERTA_DESPACHO_ACTIVA), así que prenderla es cambiar esta línea.
COMPUERTA_DESPACHO_ACTIVA = False
