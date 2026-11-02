// [S897, Carlos 02/11] En el alta de un cliente, el CUIT decide la condición de IVA. Una sola regla, probada en Node (tests/sesiones/test_ficha_cuit_iva_s897.py).
//
// Origen: Tomy dio de alta desde el pedido a una cliente que retira en Vía Cargo. La ficha nueva nacía con «Consumidor Final» puesto de fábrica y con el CUIT vacío;
// esa combinación no es ni Rosa ni formal y el pedido no la dejaba guardar. Los datos de P ya decían la regla: todos los clientes sin CUIT son sin condición de IVA.
//   - CUIT vacío              -> sin condición de IVA (campo gris): el cliente es Rosa si tiene segmento.
//   - 11111111119 / 00000000000 -> Consumidor Final (campo gris): Blanco, Factura B.
//   - 11111111111             -> CUIT reservado Rosa (campo gris, sin condición).
//   - CUIT real               -> la condición la trae ARCA (la lupa); el campo queda habilitado por si ARCA no contesta.

export const CUIT_CF_GENERICO = '11111111119'
export const CUIT_MOSTRADOR = '00000000000'
export const CUIT_ROSA = '11111111111'
export const CUITS_GENERICOS = [CUIT_MOSTRADOR, CUIT_CF_GENERICO, CUIT_ROSA, '99999999999']

export const soloDigitos = (cuit) => String(cuit ?? '').replace(/[^0-9]/g, '')

// Dígito verificador de un CUIT/CUIL (módulo 11). Un número de 11 cifras que no lo cumple no vale la pena mandarlo a ARCA.
export function cuitVerificadorOk(cuit) {
    const d = soloDigitos(cuit)
    if (d.length !== 11) return false
    const pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    const suma = pesos.reduce((acc, p, i) => acc + p * Number(d[i]), 0)
    let dv = 11 - (suma % 11)
    if (dv === 11) dv = 0
    if (dv === 10) return false
    return dv === Number(d[10])
}

// 'vacio' | 'cf' | 'rosa' | 'generico' | 'parcial' | 'real'
export function claseDeCuit(cuit) {
    const d = soloDigitos(cuit)
    if (!d) return 'vacio'
    if (d === CUIT_CF_GENERICO || d === CUIT_MOSTRADOR) return 'cf'
    if (d === CUIT_ROSA) return 'rosa'
    if (CUITS_GENERICOS.includes(d)) return 'generico'
    if (d.length < 11) return 'parcial'
    return 'real'
}

// El campo «Condición IVA» de un cliente NUEVO se pone gris cuando el CUIT lo decide solo (vacío o genérico).
export const ivaLoDecideElCuit = (cuit) => ['vacio', 'cf', 'rosa', 'generico'].includes(claseDeCuit(cuit))

// ¿Hay que consultar a ARCA sola? Un CUIT real completo, con verificador correcto, que todavía no se consultó.
export const debeConsultarArca = (cuit, ultimoConsultado) =>
    claseDeCuit(cuit) === 'real' && cuitVerificadorOk(cuit) && soloDigitos(cuit) !== soloDigitos(ultimoConsultado)
