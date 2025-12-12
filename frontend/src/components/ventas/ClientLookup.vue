<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    show: Boolean,
    clientes: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['close', 'select', 'edit', 'delete']);

const searchQuery = ref('');
const selectedIndex = ref(0);
const searchInput = ref(null);

// Filtrado
const filteredClientes = computed(() => {
    if (!searchQuery.value) return props.clientes.slice(0, 50); // Top 50 default
    const q = searchQuery.value.toLowerCase();
    return props.clientes.filter(c => 
        (c.razon_social?.toLowerCase().includes(q)) ||
        (c.cuit?.includes(q)) ||
        (c.nombre_fantasia?.toLowerCase().includes(q))
    ).slice(0, 50); // Limit results for perf
});

// Semáforo Lógico (Green/Red)
const isClienteValid = (cliente) => {
    // Regla de Negocio: Validar campos minimos para facturar
    const hasCuit = cliente.cuit && cliente.cuit.length >= 11;
    const hasAddress = cliente.domicilio_fiscal_resumen || (cliente.domicilios && cliente.domicilios.some(d => d.es_fiscal && d.activo));
    const hasCond = !!cliente.condicion_iva_id || !!cliente.condicion_iva; // ID or Object check
    
    // Si tiene todo -> GREEN. Si falta algo -> RED.
    // Tambien podriamos usar cliente.requiere_auditoria si viniera del backend
    return hasCuit && hasAddress && hasCond;
};

// Navegación
const handleKeydown = (e) => {
    if (!props.show) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex.value = (selectedIndex.value + 1) % filteredClientes.value.length;
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex.value = (selectedIndex.value - 1 + filteredClientes.value.length) % filteredClientes.value.length;
    } else if (e.key === 'Enter') {
        e.preventDefault();
        confirmSelection(filteredClientes.value[selectedIndex.value]);
    } else if (e.key === 'Delete') {
        // Matar basura
        e.preventDefault();
        handleDelete(filteredClientes.value[selectedIndex.value]);
    } else if (e.key === 'Escape') {
        emit('close');
    }
};

const confirmSelection = (cliente) => {
    if (!cliente) return;
    
    if (isClienteValid(cliente)) {
        // VERDE: Seleccionar
        emit('select', cliente);
        emit('close');
    } else {
        // ROJO: Abrir Inspector (Edit)
        // Opcionalmente podemos permitir seleccionar igual con advertencia? 
        // El user dijo: "Doble click abre inspeccion chequeo... ok"
        // Asumimos que ENTER en Rojo tambien deberia abrir inspeccion para forzar el arreglo
        handleEdit(cliente);
    }
};

const handleEdit = (cliente) => {
    emit('edit', cliente);
    // No cerramos el modal, esperamos a que vuelva de editar? 
    // O cerramos y que el padre maneje? Mejor cerrar o mantenerse visible.
    // El user workflow: Inspector -> Guardar -> Volver a lista con check verde.
    // Emitimos edit.
};

const handleDelete = (cliente) => {
    if (confirm(`¿ELIMINAR DEFINITIVAMENTE a ${cliente.razon_social}?\n(Esta acción quitará el registro de la vista operatoria)`)) {
        emit('delete', cliente);
    }
};

// Focus management
onMounted(() => {
    window.addEventListener('keydown', handleKeydown); // Global capture for arrows when input focused? 
    // Actually better to put keydown on the inputs/container
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});

// Watch show to focus input
import { watch } from 'vue';
watch(() => props.show, (val) => {
    if (val) {
        searchQuery.value = '';
        selectedIndex.value = 0;
        nextTick(() => searchInput.value?.focus());
    }
});

</script>

<template>
    <div v-if="show" class="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/50 backdrop-blur-sm" @click.self="$emit('close')">
        <div class="bg-[#0f172a] w-full max-w-4xl rounded-lg shadow-2xl border border-slate-700 flex flex-col max-h-[80vh]">
            
            <!-- Header -->
            <div class="p-4 border-b border-slate-700 flex gap-4 items-center bg-slate-900 rounded-t-lg">
                <i class="fa-solid fa-search text-slate-400 text-xl"></i>
                <input 
                    ref="searchInput"
                    v-model="searchQuery"
                    type="text" 
                    placeholder="Buscar Cliente (Razón Social, CUIT, Fantasía)..." 
                    class="bg-transparent border-none outline-none text-xl text-white placeholder-slate-500 w-full font-light"
                    @keydown.stop="handleKeydown" 
                >
                <div class="text-xs text-slate-500 text-right min-w-[120px]">
                    <span class="block">ENTER: Seleccionar</span>
                    <span class="block text-rose-400">DOBLE CLICK: Corregir</span>
                </div>
            </div>

            <!-- List -->
            <div class="overflow-y-auto flex-1 p-2 bg-[#020617]">
                <table class="w-full border-collapse">
                    <thead class="text-xs text-slate-500 uppercase font-bold sticky top-0 bg-[#020617] z-10">
                        <tr>
                            <th class="p-2 text-left w-8"></th>
                            <th class="p-2 text-left">Razón Social / Fantasía</th>
                            <th class="p-2 text-left">CUIT</th>
                            <th class="p-2 text-left">Dirección Fiscal</th>
                            <th class="p-2 text-center w-16">Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr 
                            v-for="(cliente, index) in filteredClientes" 
                            :key="cliente.id"
                            @click="selectedIndex = index"
                            @dblclick="confirmSelection(cliente)"
                            :class="[
                                'cursor-pointer transition-colors border-b border-slate-800/50',
                                selectedIndex === index ? 'bg-indigo-900/40' : 'hover:bg-slate-800/30'
                            ]"
                        >
                            <!-- Valid Status Dot -->
                            <td class="p-2 text-center">
                                <div 
                                    :class="[
                                        'w-3 h-3 rounded-full mx-auto shadow-sm',
                                        isClienteValid(cliente) ? 'bg-emerald-500 shadow-emerald-500/50' : 'bg-rose-500 shadow-rose-500/50 animate-pulse'
                                    ]"
                                    :title="isClienteValid(cliente) ? 'Listo para Facturar' : 'Requiere Auditoría'"
                                ></div>
                            </td>
                            
                            <!-- Datos -->
                            <td class="p-2 text-slate-300">
                                <div class="font-bold text-sm">{{ cliente.razon_social }}</div>
                                <div class="text-xs text-slate-500" v-if="cliente.nombre_fantasia">{{ cliente.nombre_fantasia }}</div>
                            </td>
                            <td class="p-2 text-slate-400 font-mono text-sm">
                                {{ cliente.cuit || '---' }}
                            </td>
                            <td class="p-2 text-slate-400 text-sm truncate max-w-[200px]">
                                {{ cliente.domicilio_fiscal_resumen || '---' }}
                            </td>
                            
                            <!-- Acciones / Status Text -->
                            <td class="p-2 text-center text-xs font-bold">
                                <span v-if="isClienteValid(cliente)" class="text-emerald-500">OK</span>
                                <span v-else class="text-rose-500">REVISAR</span>
                            </td>
                        </tr>
                        <tr v-if="filteredClientes.length === 0">
                            <td colspan="5" class="p-8 text-center text-slate-500">
                                No se encontraron resultados.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Footer -->
            <div class="p-2 bg-slate-900 text-xs text-slate-500 border-t border-slate-800 flex justify-between items-center rounded-b-lg">
                <div>
                    {{ filteredClientes.length }} Clientes encontrados
                </div>
                <div class="flex gap-4">
                    <span><kbd class="bg-slate-700 px-1 rounded text-white">⬆⬇</kbd> Navegar</span>
                    <span><kbd class="bg-slate-700 px-1 rounded text-white">Enter</kbd> Elegir</span>
                    <span><kbd class="bg-slate-700 px-1 rounded text-white">Supr</kbd> Eliminar</span>
                </div>
            </div>
        </div>
    </div>
</template>
