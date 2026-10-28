// [S894, Carlos 28/10] Cómo se muestra un domicilio de ENTREGA en pantalla: el mismo criterio que el papel del remito
// (backend/remitos/service.py, RemitosService._texto_domicilio). Si el domicilio tiene una dirección de entrega propia
// (calle_entrega/numero_entrega/localidad_entrega, «separada de la fiscal») y es OTRA calle, se muestra esa; si no, la del
// domicilio. Antes el pedido mostraba siempre el lado fiscal: Genesis Bag cargó la entrega en Pilar y la pantalla seguía
// diciendo Gutenberg (CABA), aunque el remito iba a imprimir Pilar.
export function textoEntrega(dom) {
  if (!dom) return ''
  const calleEnt = String(dom.calle_entrega || '').trim()
  if (calleEnt && calleEnt.toUpperCase() !== String(dom.calle || '').trim().toUpperCase()) {
    const loc = dom.localidad_entrega || ''
    return `${calleEnt} ${dom.numero_entrega || ''}`.trim() + (loc ? ` (${loc})` : '')
  }
  const base = `${dom.calle || ''} ${dom.numero || ''}`.trim()
  return base + (dom.localidad ? ` (${dom.localidad})` : '')
}
