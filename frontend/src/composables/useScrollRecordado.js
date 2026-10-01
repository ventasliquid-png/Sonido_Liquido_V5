// [S876] Un informe recuerda hasta dónde estaba desplazado mientras dure la pestaña: al abrir un pedido desde una fila y volver,
// la lista queda en el mismo lugar (junto con sus filtros y su orden, ver usePersistirFiltros). Se guarda al salir de la pantalla y se
// restaura una sola vez, cuando termina la primera carga de datos.
import { watch, nextTick, onBeforeUnmount } from 'vue'

export function useScrollRecordado(clave, elemento, cargando) {
  const k = `v5-informe-scroll-${clave}`
  let restaurado = false

  onBeforeUnmount(() => {
    try { sessionStorage.setItem(k, String(elemento.value?.scrollTop || 0)) } catch { /* sin almacenamiento: no se recuerda */ }
  })

  watch(cargando, async (sigueCargando) => {
    if (sigueCargando || restaurado) return
    restaurado = true
    await nextTick()
    try {
      const y = Number(sessionStorage.getItem(k) || 0)
      if (elemento.value && y > 0) elemento.value.scrollTop = y
    } catch { /* nada que restaurar */ }
  })
}
