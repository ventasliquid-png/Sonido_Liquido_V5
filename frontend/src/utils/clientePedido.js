// [S897, Carlos 02/11] Qué le falta a un cliente para poder armar un pedido. Una sola regla, probada en Node (tests/sesiones/test_cliente_pedido_cf_s897.py).
//
// Caso de producción (02/11): Tomy dio de alta desde el pedido a una cliente que retira en el depósito de Vía Cargo (Santa Rosa, La Pampa), la cargó con la
// condición «Consumidor Final» y sin CUIT, y el pedido no dejaba guardar: «Faltan: Domicilio, CUIT». Un Consumidor Final es Blanco a los efectos fiscales
// (Factura B, Nike S894) y por eso no es Rosa ni está validado por ARCA (Gold): caía en la regla de «sin clasificar», que lo exige todo. Pero ni el CUIT ni el
// domicilio son de un Consumidor Final: el CUIT comodín ya no se guarda en la ficha (S896) y la entrega no es un dato fiscal. Un Consumidor Final se opera con lo
// mismo que un Rosa: el segmento. El color del pedido lo decide el pedido, no la ficha.

export const GOLD_ARCA = 4        // Bit 2 — formal, validado ARCA
export const OPERATOR_OK = 16     // Bit 4 — sello Rosa, informal operativo

export const esConsumidorFinal = (nombreIva) => !!nombreIva && String(nombreIva).toUpperCase().includes('CONSUMIDOR FINAL')

// c: el cliente del pedido; nombreIva: nombre de su condición de IVA (puede faltar, p. ej. un Rosa sin condición)
export function validarClienteParaPedido(c, nombreIva) {
    if (!c) return { valid: true, missing: [] }
    const flags = c.flags_estado || 0
    const missing = []
    if (flags & GOLD_ARCA) {
        // Gold/Blanco con ARCA: siempre válido para operar
        return { valid: true, missing: [] }
    }
    if ((flags & OPERATOR_OK) || esConsumidorFinal(nombreIva)) {
        // Rosa o Consumidor Final: solo el segmento es obligatorio
        if (!c.segmento_id && !c.segmento?.id) missing.push('Segmento')
    } else {
        // Amarillo/sin clasificar: exigir todo
        if (!c.condicion_iva_id || c.condicion_iva_id === 'null') missing.push('Condición IVA')
        if (!c.segmento_id) missing.push('Segmento')
        if (!c.domicilios || c.domicilios.length === 0) missing.push('Domicilio')
        if (!c.cuit || c.cuit.length < 5) missing.push('CUIT')
    }
    return { valid: missing.length === 0, missing }
}
