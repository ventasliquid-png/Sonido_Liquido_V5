<template>
  <div class="h-full flex flex-col bg-[#0a0a0a] text-white">
    <!-- Header Módulo -->
    <div class="flex items-center justify-between p-6 border-b border-white/10 shrink-0">
      <div>
        <h1 class="text-3xl font-outfit font-bold tracking-tight text-emerald-400">
          Registros Creados
        </h1>
        <p class="text-gray-400 text-sm mt-1">
          Visualización y gestión de remitos emitidos (Historial).
        </p>
      </div>
      <div>
        <button 
          @click="fetchRemitos" 
          class="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 transition-all font-medium"
        >
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': loading }"></i>
          Actualizar
        </button>
      </div>
    </div>

    <!-- Contenido Principal -->
    <div class="flex-1 overflow-auto p-6">
      <div v-if="loading && remitos.length === 0" class="flex justify-center items-center h-48">
        <i class="fas fa-spinner fa-spin text-emerald-500 text-3xl"></i>
      </div>

      <div v-else-if="remitos.length === 0" class="flex flex-col items-center justify-center p-12 mt-10 border-2 border-dashed border-white/10 rounded-xl bg-white/5">
        <i class="fas fa-file-invoice text-gray-500 text-5xl mb-4"></i>
        <h3 class="text-lg font-bold text-gray-300">No hay remitos generados</h3>
        <p class="text-gray-500 text-sm mt-2">Los remitos creados a partir de facturas aparecerán aquí.</p>
      </div>

      <div v-else class="bg-[#111] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
        <table class="w-full text-left text-sm text-gray-300">
          <thead class="text-xs uppercase bg-[#1a1a1a] text-emerald-400/80 border-b border-white/10">
            <tr>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider">Nro Remito</th>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider">Fecha</th>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider">Cliente (Razón Social)</th>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider">CUIT / Doc</th>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider text-center">Estado</th>
              <th scope="col" class="px-6 py-4 font-bold tracking-wider text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="remito in remitos" :key="remito.id" class="hover:bg-white/5 transition-colors group">
              <!-- Nro Remito -->
              <td class="px-6 py-4 whitespace-nowrap font-mono text-emerald-300">
                {{ remito.numero_legal || 'S/N' }}
              </td>
              
              <!-- Fecha -->
              <td class="px-6 py-4 whitespace-nowrap text-gray-400">
                {{ formatDate(remito.fecha_creacion) }}
              </td>
              
              <!-- Cliente -->
              <td class="px-6 py-4 font-medium text-gray-200 uppercase tracking-wide">
                {{ remito.cliente_razon_social }}
              </td>
              
              <!-- CUIT -->
              <td class="px-6 py-4 whitespace-nowrap font-mono text-gray-400 text-xs">
                {{ remito.cliente_cuit }}
              </td>

              <!-- Estado -->
              <td class="px-6 py-4 text-center">
                <span class="px-2 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full"
                      :class="remito.estado === 'Despachado' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30'">
                  {{ remito.estado || 'Borrador' }}
                </span>
              </td>

              <!-- Acciones -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <div class="flex items-center justify-end gap-3 opacity-80 group-hover:opacity-100 transition-opacity">
                  
                  <button 
                    @click="imprimirRemito(remito)" 
                    class="text-gray-400 hover:text-emerald-400 transition-colors"
                    title="Ver PDF / Imprimir"
                    :disabled="!remito.pdf_url"
                    :class="{ 'opacity-30 cursor-not-allowed': !remito.pdf_url }"
                  >
                    <i class="fas fa-print"></i>
                  </button>

                  <button 
                    @click="confirmarBorrado(remito)" 
                    class="text-gray-400 hover:text-red-400 transition-colors"
                    title="Eliminar Registro"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                  
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import remitosService from '../../services/remitos';
import { useNotificationStore } from '../../stores/notification';

const remitos = ref([]);
const loading = ref(false);
const notificationStore = useNotificationStore();

const fetchRemitos = async () => {
    loading.value = true;
    try {
        const response = await remitosService.getRemitos();
        remitos.value = response.data.map(r => ({
           id: r.id,
           numero_legal: r.numero_legal,
           fecha_creacion: r.fecha_creacion,
           estado: r.estado,
           pdf_url: r.pdf_url,
           cliente_razon_social: r.cliente_razon_social,
           cliente_cuit: r.cliente_cuit
        }));
    } catch (error) {
        console.error('Error fetching remitos:', error);
        notificationStore.add('No se pudieron cargar los remitos.', 'error');
    } finally {
        loading.value = false;
    }
};

const imprimirRemito = (remito) => {
    if (remito.pdf_url) {
        // Formar URL absoluta si es necesario o usar la relativa (Ej: /static-remitos/...)
        const url = remito.pdf_url.startsWith('http') ? remito.pdf_url : `http://localhost:8000${remito.pdf_url}`;
        window.open(url, '_blank');
    } else {
         notificationStore.add('Este remito no posee un archivo PDF físico vinculado.', 'warning');
    }
};

const confirmarBorrado = async (remito) => {
    if (confirm(`¿Está seguro que desea eliminar permanentemente el remito ${remito.numero_legal}?`)) {
        try {
            await remitosService.deleteRemito(remito.id);
            notificationStore.add('Remito eliminado correctamente.', 'success');
            await fetchRemitos(); // Refrescar grilla
        } catch (error) {
            console.error('Error eliminando:', error);
            notificationStore.add('Error al intentar eliminar el remito.', 'error');
        }
    }
};

const formatDate = (dateString) => {
    if (!dateString) return '-';
    const d = new Date(dateString);
    return new Intl.DateTimeFormat('es-AR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute:'2-digit'
    }).format(d);
};

onMounted(() => {
    fetchRemitos();
});
</script>
