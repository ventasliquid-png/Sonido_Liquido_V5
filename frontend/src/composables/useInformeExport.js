// [S875] Descarga de archivos exportados del módulo Informes -- CSV/Excel/PDF/TXT.
// Un solo composable para los cinco informes de Nivel 1 (y los de Nivel 2): la lógica de
// pedir el blob y disparar la descarga es siempre la misma, solo cambian el endpoint,
// los filtros y el nombre de archivo.
import { ref } from 'vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const EXTENSIONES = { csv: 'csv', excel: 'xlsx', pdf: 'pdf', txt: 'txt' }

// El archivo lleva fecha y hora en el nombre (remitos_por_fecha_cliente_2026-09-30_1545.pdf): cada
// descarga es un archivo distinto y se sabe de cuándo es, en vez de pisarse o quedar como "(1)", "(2)".
const sello = () => {
  const d = new Date()
  const dos = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}_${dos(d.getHours())}${dos(d.getMinutes())}`
}

// Con responseType 'blob' el detalle de un error del servidor llega como Blob: hay que leerlo como texto.
const detalleDeError = async (e) => {
  const data = e.response?.data
  if (data instanceof Blob) {
    try { return JSON.parse(await data.text()).detail } catch { return e.message }
  }
  return data?.detail || e.message
}

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
      link.setAttribute('download', `${nombreArchivoBase}_${sello()}.${EXTENSIONES[formato]}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
      notification.add('Error exportando el informe: ' + (await detalleDeError(e)), 'error')
    } finally {
      exportando.value = false
    }
  }

  return { exportar, exportando }
}
