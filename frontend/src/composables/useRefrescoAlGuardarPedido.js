// [S876] Hace que un informe se actualice solo cuando se guarda un pedido en otra pestaña (ver utils/canalPedidos.js).
// `refrescar` tiene que recargar SIN el cartel de "Cargando" (para no perder el lugar del scroll). Junta avisos
// seguidos: varios guardados rápidos recargan una sola vez.
import { onMounted, onBeforeUnmount } from 'vue'
import { escucharPedidoActualizado } from '@/utils/canalPedidos'

export function useRefrescoAlGuardarPedido(refrescar) {
  let dejarDeEscuchar = null
  let temporizador = null

  onMounted(() => {
    dejarDeEscuchar = escucharPedidoActualizado(() => {
      clearTimeout(temporizador)
      temporizador = setTimeout(refrescar, 300)
    })
  })

  onBeforeUnmount(() => {
    clearTimeout(temporizador)
    dejarDeEscuchar?.()
  })
}
