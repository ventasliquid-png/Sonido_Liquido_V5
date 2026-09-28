// [S875] Descarga de archivos exportados del módulo Informes -- CSV/Excel/PDF/TXT.
// Un solo composable para los cinco informes de Nivel 1 (y los de Nivel 2): la lógica de
// pedir el blob y disparar la descarga es siempre la misma, solo cambian el endpoint,
// los filtros y el nombre de archivo.
import { ref } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const EXTENSIONES = { csv: 'csv', excel: 'xlsx', pdf: 'pdf', txt: 'txt' }

export function useInformeExport(endpoint, nombreArchivoBase) {
  const notification = useNotificationStore()
  const exportando = ref(false)

  const exportar = async (formato, params = {}) => {
    exportando.value = true
    try {
      const response = await api.get(endpoint, {
        params: { ...params, formato },
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${nombreArchivoBase}.${EXTENSIONES[formato]}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
      notification.add('Error exportando el informe: ' + (e.response?.data?.detail || e.message), 'error')
    } finally {
      exportando.value = false
    }
  }

  return { exportar, exportando }
}
