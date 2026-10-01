// [S876] Ordenar un listado de pantalla por cualquier columna, ascendente (A→Z, menor a mayor, más viejo primero) o
// descendente (Z→A, mayor a menor, más reciente primero). Pedido de Carlos (01/10): que todos los campos de ordenación
// tengan las dos direcciones. Clic en el encabezado: ascendente; otro clic: descendente; un tercero: vuelve al orden de
// siempre del informe. Solo en pantalla: los archivos exportados mantienen el orden del informe.
//
// El orden elegido se recuerda mientras dure la pestaña (usePersistirFiltros), junto con los filtros del informe.
import { computed, reactive } from 'vue'
import { usePersistirFiltros } from '@/composables/usePersistirFiltros'

const FECHA = /^(\d{2})\/(\d{2})\/(\d{4})/

// Compara dos valores de celda: vacíos siempre al final, números como números, fechas dd/mm/aaaa como fechas, y el resto
// como texto en castellano (sin distinguir mayúsculas ni tildes, y con "10" después de "9").
export const compararCeldas = (a, b) => {
  const vacio = (v) => v === null || v === undefined || v === ''
  if (vacio(a) && vacio(b)) return 0
  if (vacio(a)) return 1
  if (vacio(b)) return -1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  const fa = FECHA.exec(String(a)), fb = FECHA.exec(String(b))
  if (fa && fb) return `${fa[3]}${fa[2]}${fa[1]}`.localeCompare(`${fb[3]}${fb[2]}${fb[1]}`)
  return String(a).localeCompare(String(b), 'es', { numeric: true, sensitivity: 'base' })
}

export function useOrdenColumnas(filas, clave) {
  const orden = reactive({ campo: null, sentido: 'asc' })
  usePersistirFiltros(`${clave}-orden`, orden)

  const alternarOrden = (campo) => {
    if (orden.campo !== campo) { orden.campo = campo; orden.sentido = 'asc' }
    else if (orden.sentido === 'asc') orden.sentido = 'desc'
    else { orden.campo = null; orden.sentido = 'asc' } // tercer clic: orden de siempre
  }

  const ordenadas = computed(() => {
    if (!orden.campo) return filas.value
    const dir = orden.sentido === 'asc' ? 1 : -1
    const campo = orden.campo
    // Los vacíos van siempre al final, sea cual sea la dirección.
    return [...filas.value].sort((x, y) => {
      const a = x[campo], b = y[campo]
      const vacio = (v) => v === null || v === undefined || v === ''
      if (vacio(a) || vacio(b)) return compararCeldas(a, b)
      return dir * compararCeldas(a, b)
    })
  })

  const indicadorOrden = (campo) => (orden.campo !== campo ? '' : orden.sentido === 'asc' ? '▲' : '▼')
  const tituloOrden = (etiqueta) => `Ordenar por ${etiqueta}: clic = A→Z, otro clic = Z→A, otro = orden de siempre`

  return { orden, ordenadas, alternarOrden, indicadorOrden, tituloOrden }
}
