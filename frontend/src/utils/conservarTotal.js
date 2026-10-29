// [S895, Carlos 29/10; caso Castro #145] Al cambiar el circuito de un pedido (Blanco <-> Rosa) los precios de los renglones son netos: el Blanco suma el IVA al total y el Rosa no, así
// que el total cambia solo. Esta pregunta deja elegir que el total cobrado NO cambie: el servidor multiplica los precios por 1,21 (a Rosa, IVA incluido) o los divide por 1,21 (a Blanco,
// IVA discriminado) y deja una nota. Mismo texto en la ficha del pedido, el Tablero y los informes. Devuelve true si el operador quiere conservar el total.
export function preguntarConservarTotal(aRosa, total) {
  const t = Number(total)
  const monto = t > 0 ? ` (${t.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })})` : ''
  const cuenta = aRosa
    ? 'los precios de los renglones se multiplican por 1,21 (el Rosa lleva el IVA incluido)'
    : 'los precios de los renglones se dividen por 1,21 (se discrimina el IVA)'
  return confirm(
    `¿Conservar el total del pedido${monto}?\n\n` +
    `ACEPTAR = ${cuenta} y el total no cambia.\n` +
    `CANCELAR = solo cambia el circuito: los precios quedan como están y el total se recalcula.`
  )
}
