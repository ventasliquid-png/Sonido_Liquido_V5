// [S876] Un informe recuerda sus filtros y su orden mientras dure la pestaña: al salir a otra pantalla y volver, o al
// recargar la página, queda como lo dejó el operador (pedido de Carlos, 01/10: "cuando se vuelve, no guarda la elección de
// orden"). La primera vez que se entra, y en una pestaña nueva, sale con los valores por defecto de siempre.
//
// Guarda en sessionStorage (por pestaña: no se mezcla entre pestañas ni sobrevive al cerrarla). `filtros` es un reactive: lo
// que se guardó se aplica UNA vez al crear la pantalla, antes de la primera carga de datos, y después cada cambio se guarda.
import { watch } from 'vue'

export function usePersistirFiltros(clave, filtros) {
  const k = `v5-informe-${clave}`
  try {
    const guardado = JSON.parse(sessionStorage.getItem(k) || 'null')
    if (guardado && typeof guardado === 'object') {
      for (const campo of Object.keys(filtros)) {
        if (campo in guardado) filtros[campo] = guardado[campo]
      }
    }
  } catch {
    // Sin sessionStorage o contenido ilegible: se usan los valores por defecto.
  }
  watch(filtros, () => {
    try { sessionStorage.setItem(k, JSON.stringify(filtros)) } catch { /* sin almacenamiento: no se recuerda */ }
  }, { deep: true })
}
