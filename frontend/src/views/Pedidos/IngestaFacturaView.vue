<template>
  <div class="flex h-full w-full bg-[#0f172a] text-gray-200 overflow-hidden font-sans tokyo-bg neon-blue rounded-2xl border-2 border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.3)] p-6">
    
    <div class="flex-1 flex flex-col min-w-0">
        <!-- Header -->
        <header class="flex justify-between items-center mb-6 border-b border-blue-900/30 pb-4">
            <div>
                <h1 class="font-outfit text-2xl font-bold text-white flex items-center gap-3">
                    <i class="fas fa-robot text-blue-400"></i>
                    Ingesta Automática de Facturas
                </h1>
                <p class="text-xs text-blue-400/50 font-medium uppercase tracking-wider mt-1">
                    Conversión Inteligente: PDF AFIP <i class="fas fa-arrow-right mx-1"></i> Remito V5
                </p>
            </div>
        </header>

        <div class="grid grid-cols-12 gap-6 h-full overflow-hidden">
            
            <!-- LEFT: DROP ZONE -->
            <div class="col-span-5 flex flex-col gap-4">
                <div 
                    class="flex-1 border-2 border-dashed border-blue-500/30 bg-blue-900/10 rounded-2xl flex flex-col items-center justify-center p-8 transition-all duration-300 relative overflow-hidden group"
                    :class="{'border-blue-400 bg-blue-900/20 scale-[1.01]': isDragging, 'border-red-500/50': error}"
                    @dragover.prevent="isDragging = true"
                    @dragleave.prevent="isDragging = false"
                    @drop.prevent="handleDrop"
                    @click="triggerFileInput"
                >
                    <input type="file" ref="fileInput" class="hidden" accept=".pdf" @change="handleFileSelect">
                    
                    <div v-if="loading" class="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-20">
                        <div class="text-center">
                            <i class="fas fa-circle-notch fa-spin text-4xl text-blue-400 mb-4"></i>
                            <p class="text-blue-200 font-bold animate-pulse">Analizando Documento...</p>
                        </div>
                    </div>

                    <div class="text-center relative z-10 pointer-events-none">
                        <div class="w-20 h-20 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                            <i class="fas fa-file-pdf text-4xl text-blue-400"></i>
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">Arrastre su Factura Aquí</h3>
                        <p class="text-sm text-blue-300/60 mb-6 max-w-xs mx-auto">
                            Soporta Facturas de Crédito Electrónicas MiPyME (FCE) y Facturas B estándar de AFIP.
                        </p>
                        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold shadow-lg shadow-blue-900/50 transition-all pointer-events-auto">
                            O seleccione archivo
                        </button>
                    </div>
                </div>

                <!-- Instructions -->
                <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 text-xs text-slate-400">
                    <h4 class="font-bold text-slate-300 mb-2 uppercase"><i class="fas fa-info-circle mr-1"></i> Cómo funciona</h4>
                    <ol class="list-decimal list-inside space-y-1">
                        <li>Suba el PDF original descargado de AFIP.</li>
                        <li>El sistema extraerá Cliente, CUIT e Ítems.</li>
                        <li>Verifique los datos en el panel derecho.</li>
                        <li>Confirme para generar el Remito automáticamente.</li>
                    </ol>
                </div>
            </div>

            <!-- RIGHT: PREVIEW & ACTIONS -->
            <div class="col-span-7 flex flex-col bg-slate-900/50 rounded-2xl border border-slate-700/50 overflow-hidden relative">
                
                <!-- EMPTY STATE -->
                <div v-if="!parsedData" class="absolute inset-0 flex items-center justify-center text-slate-600 flex-col pointer-events-none">
                    <i class="fas fa-arrow-left text-4xl mb-4 opacity-20"></i>
                    <p class="font-bold opacity-30">Esperando documento...</p>
                </div>

                <!-- CONTENT -->
                <div v-else class="flex flex-col h-full">
                    <!-- Invoice Header Data -->
                    <div class="p-6 bg-slate-800/80 border-b border-slate-700">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                 <span class="text-xs uppercase font-bold text-blue-400 tracking-wider">Factura Detectada</span>
                                 <h2 class="text-2xl font-bold text-white">{{ parsedData.factura?.numero || 'S/N' }}</h2>
                            </div>
                            <div class="text-right">
                                <div class="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20">
                                    <i class="fas fa-check-circle"></i> Validado
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div class="bg-slate-900 p-3 rounded-lg border border-slate-700">
                                <label class="text-[10px] uppercase text-slate-500 font-bold block mb-1">Cliente</label>
                                <p class="font-bold text-white">{{ parsedData.cliente?.razon_social || 'Desconocido' }}</p>
                                <p class="text-xs text-slate-400">{{ parsedData.cliente?.cuit }}</p>
                            </div>
                            <div class="bg-slate-900 p-3 rounded-lg border border-slate-700">
                                <label class="text-[10px] uppercase text-slate-500 font-bold block mb-1">Datos Fiscales</label>
                                <div class="flex justify-between">
                                    <div>
                                        <p class="text-xs text-slate-400">CAE</p>
                                        <p class="font-mono font-bold text-white">{{ parsedData.factura?.cae || '-' }}</p>
                                    </div>
                                    <div class="text-right">
                                        <p class="text-xs text-slate-400">Vencimiento</p>
                                        <p class="font-mono font-bold text-white">{{ parsedData.factura?.vto_cae || '-' }}</p>
                                    </div>
                                 </div>
                            </div>
                        </div>
                    </div>

                    <!-- Items List -->
                    <div class="flex-1 overflow-y-auto p-4 bg-slate-900/30">
                        <table class="w-full text-left border-collapse">
                            <thead class="text-xs uppercase text-slate-500 font-bold border-b border-slate-700">
                                <tr>
                                    <th class="py-2 pl-2">Descripción</th>
                                    <th class="py-2 text-right w-24">Cant.</th>
                                    <th class="py-2 w-10"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-800">
                                <tr v-for="(item, idx) in parsedData.items" :key="idx" class="group hover:bg-slate-800/50">
                                    <td class="py-2 pl-2">
                                        <input 
                                            v-model="item.descripcion" 
                                            type="text" 
                                            class="w-full bg-transparent border-none text-sm text-slate-300 group-hover:text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 rounded px-1 transition-all"
                                            placeholder="Descripción del ítem..."
                                        />
                                    </td>
                                    <td class="py-2 text-right">
                                        <input 
                                            v-model.number="item.cantidad" 
                                            type="number" 
                                            class="w-20 bg-blue-500/10 border border-blue-500/20 rounded px-2 py-1 text-right text-sm font-mono font-bold text-blue-300 focus:outline-none focus:border-blue-500 transition-all"
                                        />
                                    </td>
                                    <td class="py-2 text-center">
                                        <button @click="removeItem(idx)" class="text-slate-600 hover:text-red-500 transition-colors">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </td>
                                </tr>
                                
                                <!-- Add Item Row -->
                                <tr class="bg-blue-500/5">
                                    <td colspan="3" class="py-3 text-center">
                                        <button @click="addItem" class="text-[10px] font-bold text-blue-400 hover:text-blue-300 transition-all uppercase tracking-widest flex items-center justify-center w-full gap-2">
                                            <i class="fas fa-plus-circle"></i> Agregar Ítem Manual
                                        </button>
                                    </td>
                                </tr>

                                <tr v-if="parsedData.items.length === 0">
                                    <td colspan="3" class="py-8 text-center text-slate-500 italic">
                                        No hay ítems cargados.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Actions -->
                    <div class="p-4 bg-slate-800 border-t border-slate-700 flex justify-end gap-3 transition-all">
                        <button @click="reset" class="px-4 py-2 text-slate-400 hover:text-white transition">
                            Descartar
                        </button>
                        <!-- PREVIEW NATIVO REMOVIDO -->
                        <button 
                            @click="confirmIngesta"
                            class="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-lg shadow-lg shadow-blue-900/30 flex items-center gap-2"
                        >
                            <span>Generar Remito</span>
                            <i class="fas fa-file-import"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SE ELIMINÓ EL MODAL PREVIEW DE VUE -->

    <!-- CLIENT ABM MODAL (SABUESO INTERVENTION) -->
    <Teleport to="body">
        <div v-if="showClientAbm" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 lg:p-12">
            <div class="border-2 border-cyan-500/50 rounded-2xl w-full max-w-5xl h-full max-h-[90vh] flex flex-col overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.2)] bg-[#0f172a]">
                <!-- V5 HUD Border Wrapper for Inspector -->
                <div class="flex-1 overflow-hidden relative">
                     <ClientCanvas 
                         :isModal="true"
                         id="new" 
                         :initialData="parsedData?.cliente"
                         @close="closeClientAbm"
                         @save="onClientSaved"
                     />
                </div>
            </div>
        </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import remitosService from '@/services/remitos';
import { useNotificationStore } from '@/stores/notification';
import ClientCanvas from '../Hawe/ClientCanvas.vue';

const router = useRouter();
const notification = useNotificationStore();

const isDragging = ref(false);
const loading = ref(false);
const error = ref(null);
const parsedData = ref(null);
const fileInput = ref(null);
const showPreview = ref(false);

const showClientAbm = ref(false);

// SE ELIMINARON MOCKS DE VISTA PREVIA

const triggerFileInput = () => {
    if (fileInput.value) {
        fileInput.value.click();
    } else {
        console.warn("[V5-UI] fileInput ref is not ready.");
    }
};

const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file) await processFile(file);
};

const handleDrop = async (e) => {
    isDragging.value = false;
    const file = e.dataTransfer.files[0];
    if (file) await processFile(file);
};

const processFile = async (file) => {
    if (file.type !== 'application/pdf') {
        notification.add('Solo se admiten archivos PDF', 'error');
        return;
    }

    loading.value = true;
    error.value = null;

    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await remitosService.uploadInvoice(formData);
        
        if (res.data && res.data.success) {
            parsedData.value = res.data.data;
            notification.add('Factura analizada con éxito', 'success');
        } else {
            const errorMsg = res.data?.error || 'El servidor no pudo interpretar el archivo.';
            throw new Error(errorMsg);
        }

    } catch (e) {
        console.error(e);
        error.value = e.message;
        notification.add('Error al procesar factura', 'error');
    } finally {
        loading.value = false;
    }
};

const reset = () => {
    parsedData.value = null;
    if (fileInput.value) fileInput.value.value = '';
};

const addItem = () => {
    if (!parsedData.value) return;
    if (!parsedData.value.items) parsedData.value.items = [];
    parsedData.value.items.push({
        descripcion: '',
        cantidad: 1,
        precio_unitario: 0.0,
        codigo: null
    });
};

const removeItem = (index) => {
    if (parsedData.value && parsedData.value.items) {
        parsedData.value.items.splice(index, 1);
    }
};

const checkClientStatus = () => {
    if (!parsedData.value) return false;
    
    const status = parsedData.value.cliente.db_status;
    const flags = parsedData.value.cliente.flags_estado || 0;
    
    // Level 13 = Existence (1) | GOLD_ARCA (4) | V14_STRUCT (8)
    const BIT_EXISTENCE = 1;
    const BIT_GOLD_ARCA = 4;
    
    // Si no existe, o si no cumple con ser "Blanco" básico (1 y 4)
    if (status === 'NO_EXISTE' || !(flags & BIT_EXISTENCE) || !(flags & BIT_GOLD_ARCA)) {
        return false;
    }
    
    return true;
};

const closeClientAbm = () => {
    showClientAbm.value = false;
};

const onClientSaved = (savedClient) => {
    showClientAbm.value = false;
    notification.add('Cliente consistido. Procediendo a generar remito...', 'success');
    
    // Update local data with the new verified status
    if (parsedData.value && savedClient) {
        parsedData.value.cliente.db_status = 'EXISTE';
        parsedData.value.cliente.flags_estado = savedClient.flags_estado;
        parsedData.value.cliente.razon_social = savedClient.razon_social;
        parsedData.value.cliente.id = savedClient.id; // Guarda el ID real devuelto por la DB
    }
    
    // Auto-resume formulation  
    confirmIngesta();
};

const confirmIngesta = async () => {
    if (!parsedData.value) return;

    // [V5] Interception Check (ABM Workflow)
    if (!checkClientStatus()) {
        notification.add('El cliente no existe o requiere consistencia AFIP. Complete la ficha técnica.', 'warning');
        showClientAbm.value = true;
        return;
    }

    try {
        loading.value = true;
        
        // Prepare Payload based on schema
        // Ensure numbers are floats/ints as expected
        const payload = {
            cliente: {
                id: parsedData.value.cliente.id || null,
                cuit: parsedData.value.cliente.cuit,
                razon_social: parsedData.value.cliente.razon_social
            },
            factura: {
                numero: parsedData.value.factura.numero,
                cae: parsedData.value.factura.cae,
                vto_cae: parsedData.value.factura.vto_cae
            },
            items: parsedData.value.items.map(item => ({
                descripcion: item.descripcion,
                cantidad: parseFloat(item.cantidad),
                precio_unitario: 0.0, // Assuming 0 for Remito logic
                codigo: item.codigo || null
            }))
        };

        const res = await remitosService.confirmIngesta(payload);
        
        if (res.data && res.data.id) {
            notification.add('Remito generado con éxito en Base de Datos', 'success');
            // [GY-FIX] Ya no mostramos la Vista Previa de Vue, sino que abrimos
            // el PDF Oficial generado por el Motor Python FPDF (Estilo RAR)
            const pdfUrl = `/remitos/${res.data.id}/pdf`;
            window.open(pdfUrl, '_blank');
            
            reset();
        }

    } catch (e) {
        console.error(e);
        notification.add('Error al generar remito: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.tokyo-bg {
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.05) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 20%);
}
</style>
