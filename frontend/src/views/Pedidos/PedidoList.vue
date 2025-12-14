<template>
    <div class="flex flex-col h-full bg-[#e6f0eb] text-slate-800 font-sans">
        
        <!-- HEADER -->
        <header class="flex items-center justify-between px-6 py-4 bg-white border-b border-slate-200">
            <div>
                <h1 class="text-xl font-bold text-slate-800 tracking-tight">Tablero de Pedidos</h1>
                <p class="text-xs text-slate-400 font-medium uppercase tracking-wider">Gestión & Seguimiento</p>
            </div>
            
            <div class="flex items-center gap-3">
                <!-- Quick Filters -->
                <div class="flex bg-slate-100 rounded p-1">
                    <button 
                        v-for="f in filters" 
                        :key="f.key"
                        class="px-3 py-1 text-xs font-bold rounded transition-all uppercase tracking-wide"
                        :class="activeFilter === f.key ? 'bg-white shadow text-emerald-600' : 'text-slate-400 hover:text-slate-600'"
                        @click="setFilter(f.key)"
                    >
                        {{ f.label }}
                    </button>
                </div>
                
                <button class="bg-emerald-600 text-white w-8 h-8 rounded hover:bg-emerald-500 flex items-center justify-center shadow-lg transition-transform active:scale-95" @click="refresh">
                    <i class="fa-solid fa-sync-alt" :class="{'animate-spin': store.isLoading}"></i>
                </button>
            </div>
        </header>

        <!-- GRID -->
        <main class="flex-1 overflow-hidden p-6">
            <div class="bg-white rounded-lg shadow-sm border border-slate-200 h-full flex flex-col">
                
                <!-- Table Header -->
                <div class="flex px-4 py-2 bg-slate-50 border-b border-slate-200 text-[10px] font-bold uppercase text-slate-400 tracking-widest select-none">
                    <div class="w-20"># ID</div>
                    <div class="w-32">Fecha</div>
                    <div class="w-32">Estado</div>
                    <div class="flex-1">Cliente</div>
                    <div class="w-32 text-right">Total</div>
                    <div class="w-20 text-center">Acciones</div>
                </div>

                <!-- Table Body -->
                <div class="flex-1 overflow-y-auto custom-scrollbar relative">
                    <div v-if="store.pedidos.length === 0" class="flex flex-col items-center justify-center h-64 opacity-40">
                        <i class="fa-solid fa-box-open text-4xl mb-2 text-slate-300"></i>
                        <p class="text-sm font-medium">No hay pedidos para mostrar</p>
                    </div>

                    <div 
                        v-for="p in store.pedidos" 
                        :key="p.id"
                        class="flex items-center px-4 py-3 border-b border-slate-100 hover:bg-blue-50/50 transition-colors group cursor-default text-sm"
                        @dblclick="openPedido(p)"
                    >
                        <div class="w-20 font-mono text-slate-500 font-bold">#{{ p.id }}</div>
                        <div class="w-32 font-mono text-slate-600 text-xs">{{ formatDate(p.fecha) }}</div>
                        <div class="w-32">
                            <span 
                                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border"
                                :class="statusClass(p.estado)"
                            >
                                {{ p.estado }}
                            </span>
                        </div>
                        <div class="flex-1 font-bold text-slate-700 truncate pr-4" :title="p.nota">
                            {{ p.cliente_razon_social || 'Cliente #' + p.cliente_id }}
                             <span v-if="p.nota" class="ml-2 text-xs text-slate-400 font-normal italic truncate max-w-xs inline-block align-bottom">
                                - {{ p.nota }}
                            </span>
                        </div>
                        <div class="w-32 text-right font-mono font-bold text-slate-700">
                            {{ formatCurrency(p.total) }}
                        </div>
                        <div class="w-20 text-center opacity-0 group-hover:opacity-100 transition-opacity flex justify-center gap-2">
                             <button class="text-slate-400 hover:text-blue-500" title="Ver Detalle" @click="openPedido(p)">
                                <i class="fa-solid fa-eye"></i>
                            </button>
                            <button class="text-slate-400 hover:text-emerald-500" title="Re-Imprimir Excel" @click="reprint(p)">
                                <i class="fa-solid fa-file-excel"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Footer Summary -->
                 <div class="px-4 py-2 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex justify-between font-medium">
                    <span>Mostrando {{ store.pedidos.length }} registros</span>
                    <span>Total Visible: <b>{{ formatCurrency(totalVisible) }}</b></span>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { usePedidosStore } from '@/stores/pedidos';

const store = usePedidosStore();
const activeFilter = ref('PENDIENTE');

const filters = [
    { key: null, label: 'Todos' },
    { key: 'PENDIENTE', label: 'Pendientes' },
    { key: 'CUMPLIDO', label: 'Cumplidos' },
    { key: 'ANULADO', label: 'Anulados' },
    { key: 'INTERNO', label: 'Internos' }
];

const totalVisible = computed(() => {
    return store.pedidos.reduce((acc, p) => acc + p.total, 0);
});

onMounted(() => {
    refresh();
});

const refresh = () => {
    const params = {};
    if (activeFilter.value) params.estado = activeFilter.value;
    store.fetchPedidos(params);
};

const setFilter = (key) => {
    activeFilter.value = key;
    refresh();
};

const formatDate = (dateStr) => {
    if(!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: '2-digit' });
};

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(val);
};

const statusClass = (status) => {
    switch (status) {
        case 'PENDIENTE': return 'bg-emerald-50 text-emerald-700 border-emerald-200'; // Proceso (Verde/Neutral)
        case 'CUMPLIDO': return 'bg-yellow-50 text-yellow-700 border-yellow-200'; // Finalizado (Amarillo)
        case 'ANULADO': return 'bg-red-50 text-red-700 border-red-200 line-through opacity-70';
        case 'INTERNO': return 'bg-purple-50 text-purple-700 border-purple-200';
        default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
};

const openPedido = (p) => {
    // TODO: Implement Detail View or Edit
    alert("Próximamente: Edición de Pedido #" + p.id);
};

const reprint = (p) => {
    // TODO: Re-download logic
    alert("Re-descarga Excel pendiente de implementación backend");
};

</script>
