// [IDENTIDAD] - frontend\src\views\Pedidos\IngestaFacturaView.vue
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

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
                    <!-- Invoice & Client Header (EDITABLE) -->
                    <div class="p-6 bg-slate-800/80 border-b border-slate-700 space-y-6">
                        <div class="flex justify-between items-start">
                            <div class="flex-1 mr-4">
                                 <label class="text-[10px] uppercase font-bold text-blue-400 tracking-wider block mb-1">Nro. Factura / Remito</label>
                                 <input 
                                    v-model="parsedData.factura.numero" 
                                    class="text-2xl font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full"
                                    placeholder="0000-00000000"
                                 />
                                 <p class="text-[10px] text-blue-500/50 font-mono italic mt-1">Soberanía Total: Edite si el OCR falló.</p>
                            </div>
                            <div class="text-right">
                                <div class="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20 text-xs font-bold uppercase">
                                    <i class="fas fa-check-circle"></i> Validado
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <!-- CLIENT BOX -->
                            <div class="bg-slate-900 p-4 rounded-xl border border-blue-500/20 shadow-inner group transition-all hover:border-blue-500/40">
                                <label class="text-[10px] uppercase text-blue-500 font-black block mb-2 tracking-widest">Cliente Destinatario</label>
                                <input 
                                    v-model="parsedData.cliente.razon_social" 
                                    class="font-bold text-white bg-transparent border-none focus:ring-0 w-full px-0 mb-1"
                                    placeholder="Razón Social..."
                                />
                                <div class="flex items-center gap-2 text-xs text-slate-400">
                                    <span class="font-mono text-blue-400/50">CUIT:</span>
                                    <input 
                                        v-model="parsedData.cliente.cuit" 
                                        class="bg-transparent border-none focus:ring-0 p-0 text-slate-300 w-full font-mono"
                                        placeholder="00-00000000-0"
                                    />
                                </div>
                            </div>

                            <!-- FISCAL DATA BOX -->
                            <div class="bg-slate-900 p-4 rounded-xl border border-slate-700/50">
                                <label class="text-[10px] uppercase text-slate-500 font-bold block mb-2">Comprobante AFIP</label>
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <p class="text-[9px] uppercase text-slate-600 font-bold mb-1">CAE</p>
                                        <input 
                                            v-model="parsedData.factura.cae" 
                                            class="font-mono font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full text-sm"
                                            placeholder="CAE..."
                                        />
                                    </div>
                                    <div class="text-right">
                                        <p class="text-[9px] uppercase text-slate-600 font-bold mb-1">Vencimiento</p>
                                        <input 
                                            v-model="parsedData.factura.vto_cae" 
                                            class="font-mono font-bold text-white bg-transparent border-none focus:ring-0 p-0 w-full text-sm text-right"
                                            placeholder="DD/MM/YYYY"
                                        />
                                    </div>
                                 </div>
                            </div>
                        </div>

                        <!-- LOGISTICS BOX -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                             <div class="space-y-1">
                                <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Empresa Logística</label>
                                <select 
                                    v-model="selectedTransportId" 
                                    class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all appearance-none"
                                >
                                    <option v-for="t in maestrosStore.transportes" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                                </select>
                             </div>
                    <!-- LOGISTICS EXTENSION: COSTOS Y BULTOS -->
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4">
                        <div class="md:col-span-2 space-y-1" v-if="clientAddresses.length > 0">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest flex items-center justify-between">
                                <span>Sede de Entrega (Padrón)</span>
                                <span v-if="addressAmbiguity && !manualAddressChange" class="text-amber-500 animate-pulse flex items-center gap-1">
                                    <i class="fas fa-exclamation-triangle text-[8px]"></i> AMBIGÜEDAD: CONFIRME SEDE
                                </span>
                            </label>
                            <div class="relative group">
                                <select 
                                    v-model="selectedAddressId" 
                                    @change="manualAddressChange = true; onAddressSelectChange()"
                                    class="w-full bg-slate-950 border rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all appearance-none pr-8"
                                    :class="[
                                        addressAmbiguity && !manualAddressChange ? 'border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.2)]' : 'border-blue-900/30',
                                        isSuggestedSelected ? 'border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]' : ''
                                    ]"
                                >
                                    <!-- Options from DB -->
                                    <option v-for="d in clientAddresses" :key="d.id" :value="d.id">
                                        {{ d.is_suggested ? '🪄' : (d.es_entrega ? '🚛' : '🏠') }} 
                                        {{ d.alias || (d.calle + ' ' + (d.numero || '')) }} 
                                        {{ d.is_suggested ? '(SUGERIDO)' : (d.es_fiscal ? '(FISCAL)' : '') }}
                                    </option>
                                    
                                    <!-- Management Options -->
                                    <option value="ADD_NEW" class="text-blue-400 font-bold">➕ AGREGAR NUEVA DIRECCIÓN...</option>
                                </select>
                                <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-blue-400">
                                    <i class="fas" :class="isSuggestedSelected ? 'fa-magic text-emerald-400' : 'fa-chevron-down'"></i>
                                </div>
                            </div>
                            <!-- Help text for Ambiguity [GY-UX] -->
                            <div v-if="addressAmbiguity && !manualAddressChange" class="mt-1 text-[9px] text-amber-500/70 italic flex items-center gap-1">
                                <i class="fas fa-arrow-up"></i> Haga clic para seleccionar la sede correcta de la lista
                            </div>
                        </div>
                        
                        <!-- NEW ADDRESS MINI-FORM -->
                        <div v-if="selectedAddressId === 'ADD_NEW'" class="md:col-span-4 bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 mt-2 animate-in fade-in slide-in-from-top-4 duration-300">
                            <div class="flex items-center gap-2 mb-3">
                                <i class="fas fa-plus-circle text-blue-400"></i>
                                <span class="text-[10px] uppercase font-bold text-blue-200 tracking-wider">Alta de Nueva Sede de Entrega</span>
                            </div>
                            <div class="grid grid-cols-12 gap-3">
                                <div class="col-span-8">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Calle</label>
                                    <input v-model="newAddress.calle" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Calle..." />
                                </div>
                                <div class="col-span-4">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Número</label>
                                    <input v-model="newAddress.numero" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Nro..." />
                                </div>
                                <div class="col-span-6">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Localidad</label>
                                    <input v-model="newAddress.localidad" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none" placeholder="Localidad..." />
                                </div>
                                <div class="col-span-6">
                                    <label class="text-[8px] uppercase text-blue-400/50 font-bold block mb-1">Provincia (ID)</label>
                                    <input v-model="newAddress.provincia_id" type="text" class="w-full bg-slate-950 border border-blue-900/40 rounded px-2 py-1 text-xs text-white focus:border-blue-500 outline-none uppercase" placeholder="B / X / C..." />
                                </div>
                            </div>
                            <p class="text-[9px] text-blue-400/40 italic mt-3 flex items-center gap-1">
                                <i class="fas fa-info-circle"></i> Al confirmar, esta sede se guardará permanentemente en la ficha del cliente.
                            </p>
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Bultos</label>
                            <input type="number" v-model.number="bultos" class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all text-center" />
                        </div>
                        <div class="space-y-1">
                            <label class="text-[10px] uppercase text-blue-500 font-black block mb-1 tracking-widest">Valor Decl.</label>
                            <input type="number" v-model.number="valor_declarado" class="w-full bg-slate-950 border border-blue-900/30 rounded-lg px-3 py-2 text-xs text-white focus:border-blue-500 outline-none transition-all text-center" />
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
                                    <th class="py-2 text-right w-28">P. Unit. Neto</th>
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
                                            class="w-20 bg-blue-500/10 border rounded px-2 py-1 text-right text-sm font-mono font-bold transition-all"
                                            :class="item.cantidad <= 0 ? 'border-red-500 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.3)]' : 'border-blue-500/20 text-blue-300 focus:border-blue-500'"
                                        />
                                    </td>
                                    <td class="py-2 text-right">
                                        <input
                                            v-model.number="item.precio_unitario_neto"
                                            type="number"
                                            class="w-28 bg-emerald-500/10 border rounded px-2 py-1 text-right text-sm font-mono font-bold transition-all"
                                            :class="item.precio_unitario_neto <= 0 ? 'border-red-500 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.3)]' : 'border-emerald-500/20 text-emerald-300 focus:border-emerald-500'"
                                            placeholder="0.00"
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
                            :disabled="loading || hasZeroValues"
                            class="px-6 py-2 font-bold rounded-lg shadow-lg flex items-center gap-2 transition-all"
                            :class="[
                                (loading || hasZeroValues) 
                                ? 'bg-slate-700 text-slate-500 cursor-not-allowed shadow-none' 
                                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-900/30'
                            ]"
                        >
                            <span>{{ hasZeroValues ? 'Corregir Valores en 0' : 'Generar Remito' }}</span>
                            <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-file-import'"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SE ELIMINÓ EL MODAL PREVIEW DE VUE -->

    <!-- MODAL SELECCIÓN DE FLUJO DE INGESTA -->
    <Teleport to="body">
        <div v-if="showModoIngesta" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-[#0f172a] border-2 border-blue-500/50 rounded-2xl w-full max-w-2xl shadow-[0_0_30px_rgba(59,130,246,0.3)] p-6">

                <h2 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
                    <i class="fas fa-code-branch text-blue-400"></i>
                    ¿Qué hacemos con esta factura?
                </h2>
                <p class="text-sm text-slate-400 mb-6">
                    {{ parsedData?.cliente?.razon_social }} — {{ parsedData?.factura?.numero }}
                </p>

                <!-- CANDIDATOS -->
                <div v-if="pedidosCandidatos.length > 0" class="mb-4">
                    <p class="text-xs uppercase font-bold text-blue-400 mb-2 tracking-wider">
                        Pedidos activos de este cliente
                    </p>
                    <div class="space-y-2 max-h-48 overflow-y-auto">
                        <button
                            v-for="p in pedidosCandidatos.slice(0,5)"
                            :key="p.pedido_id"
                            @click="pedidoVinculadoId = p.pedido_id; modoIngestaSeleccionado = p.estado === 'CUMPLIDO' ? 'VINCULAR_CUMPLIDO' : 'VINCULAR_EXISTENTE'; showModoIngesta = false; confirmIngesta()"
                            class="w-full text-left bg-slate-800 hover:bg-blue-900/30 border rounded-lg px-4 py-3 transition-all"
                            :class="p.score > 30 ? 'border-blue-500/50' : 'border-slate-700'"
                        >
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-white">Pedido #{{ p.pedido_id }}</span>
                                <span class="text-xs px-2 py-1 rounded-full"
                                    :class="p.es_interno ? 'bg-orange-900/50 text-orange-400' : p.estado === 'CUMPLIDO' ? 'bg-green-900/50 text-green-400' : 'bg-blue-900/50 text-blue-400'">
                                    {{ p.estado }}
                                </span>
                            </div>
                            <div class="text-xs text-slate-400 mt-1">
                                {{ p.fecha }} — {{ p.items_count }} ítems — ${{ p.total?.toLocaleString('es-AR') }}
                                <span v-if="p.score > 30" class="ml-2 text-blue-400">
                                    <i class="fas fa-magic"></i> Sugerido
                                </span>
                            </div>
                            <div v-if="p.es_interno" class="text-xs text-orange-400 mt-1 flex items-center gap-1">
                                <i class="fas fa-exclamation-triangle"></i>
                                Pedido INTERNO — los precios pueden diferir del PDF. Verificar antes de vincular.
                            </div>
                        </button>
                    </div>
                </div>

                <!-- OPCIONES -->
                <div class="grid grid-cols-1 gap-3 mt-4">
                    <button
                        v-if="pedidosCandidatos.length === 0"
                        class="w-full text-center py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 text-sm italic"
                        disabled
                    >
                        No hay pedidos activos para este cliente
                    </button>

                    <button
                        @click="modoIngestaSeleccionado = 'NUEVO'; showModoIngesta = false; confirmIngesta()"
                        class="w-full text-left px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg transition-all"
                    >
                        <div class="font-bold text-white flex items-center gap-2">
                            <i class="fas fa-plus-circle text-green-400"></i>
                            Crear pedido nuevo con datos de esta factura
                        </div>
                        <div class="text-xs text-slate-400 mt-1">
                            La factura no corresponde a ningún pedido previo
                        </div>
                    </button>

                    <button
                        @click="modoIngestaSeleccionado = 'DIRECTO'; showModoIngesta = false; confirmIngesta()"
                        class="w-full text-left px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg transition-all"
                    >
                        <div class="font-bold text-white flex items-center gap-2">
                            <i class="fas fa-check-circle text-amber-400"></i>
                            Venta directa — ya entregado, sin pedido pendiente
                        </div>
                        <div class="text-xs text-slate-400 mt-1">
                            Mostrador, entrega inmediata. Solo registrar la factura.
                        </div>
                    </button>

                    <button
                        @click="showModoIngesta = false"
                        class="w-full text-center py-2 text-slate-500 hover:text-white transition text-sm"
                    >
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    </Teleport>

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
import { useMaestrosStore } from '@/stores/maestros';
import { useClientesStore } from '@/stores/clientes';
import ClientCanvas from '../Hawe/ClientCanvas.vue';
import SmartSelect from '@/components/ui/SmartSelect.vue';
import api from '@/services/api';

const router = useRouter();
const notification = useNotificationStore();
const maestrosStore = useMaestrosStore();
const clientesStore = useClientesStore();

const isDragging = ref(false);
const loading = ref(false);
const error = ref(null);
const parsedData = ref(null);
const fileInput = ref(null);
const showPreview = ref(false);

const showClientAbm = ref(false);
const clientAddresses = ref([]);
const selectedTransportId = ref(null);
const selectedAddressId = ref(null);
const bultos = ref(1);
const valor_declarado = ref(0.0);
const addressAmbiguity = ref(false);
const manualAddressChange = ref(false);
const hasZeroValues = computed(() => {
    if (!parsedData.value || !parsedData.value.items) return false;
    return parsedData.value.items.some(item => item.cantidad <= 0 || item.precio_unitario_neto <= 0);
});
const isSuggestedSelected = computed(() => {
    const selected = clientAddresses.value.find(d => d.id === selectedAddressId.value);
    return selected?.is_suggested || false;
});

const newAddress = ref({
    calle: '',
    numero: '',
    localidad: '',
    provincia_id: 'X'
});

const showModoIngesta = ref(false);
const pedidosCandidatos = ref([]);
const modoIngestaSeleccionado = ref(null);
const pedidoVinculadoId = ref(null);

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
            
            // Auto-load client details if matched in DB
            if (parsedData.value.cliente?.id) {
                // [V5.8] Use addresses returned by the API during ingestion to avoid Round-trip delay
                if (parsedData.value.cliente.domicilios_disponibles?.length > 0) {
                    clientAddresses.value = parsedData.value.cliente.domicilios_disponibles;
                    autoSelectAddress();
                } else {
                    await loadClientDetails(parsedData.value.cliente.id);
                }
            }
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
    bultos.value = 1;
    valor_declarado.value = 0.0;
    if (fileInput.value) fileInput.value.value = '';
    modoIngestaSeleccionado.value = null;
    pedidoVinculadoId.value = null;
    showModoIngesta.value = false;
    pedidosCandidatos.value = [];
};

const addItem = () => {
    if (!parsedData.value) return;
    if (!parsedData.value.items) parsedData.value.items = [];
    parsedData.value.items.push({
        descripcion: '',
        cantidad: 1,
        precio_unitario_neto: 0.0,
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

const onClientSaved = async (savedClient) => {
    showClientAbm.value = false;

    // Update local data with the new verified status
    if (parsedData.value && savedClient) {
        parsedData.value.cliente.db_status = 'EXISTE';
        parsedData.value.cliente.flags_estado = savedClient.flags_estado;
        parsedData.value.cliente.razon_social = savedClient.razon_social;
        parsedData.value.cliente.id = savedClient.id;

        await loadClientDetails(savedClient.id);
    }

    // [V5-FIX] BUG pedidos fantasma: no auto-confirmar.
    // El usuario revisa domicilio y confirma manualmente.
    notification.add('Cliente consistido. Revisá la sede de entrega y presioná "Generar Remito".', 'info');
};

const loadClientDetails = async (clientId) => {
    try {
        const res = await api.get(`/clientes/${clientId}`);
        clientAddresses.value = res.data.domicilios || [];
        autoSelectAddress();
    } catch (e) {
        console.error("[V5] No se pudieron cargar domicilios del cliente", e);
    }
}

const onAddressSelectChange = () => {
    manualAddressChange.value = true;
    if (selectedAddressId.value === 'ADD_NEW') {
        const extracted = parsedData.value?.cliente?.domicilio || '';
        // Heurística básica de limpieza para el formulario
        const clean = extracted.replace('[EXTRACTED] ', '').replace('SIN DOMICILIO FISCAL', '').trim();
        
        // Intentar separar Calle y Número (Simple split por último espacio que sea número?)
        // Por ahora lo ponemos todo en calle y el usuario separa en el mini-form
        newAddress.value.calle = clean;
        newAddress.value.numero = '';
        newAddress.value.localidad = 'CABA'; // Default situational
        newAddress.value.provincia_id = 'C';
    }
}

const buscarPedidosCandidatos = async () => {
    if (!parsedData.value?.cliente?.cuit) return;
    try {
        const cuit = parsedData.value.cliente.cuit.replace(/-/g, '').trim();
        const items = parsedData.value.items.map(i => ({
            descripcion: i.descripcion,
            cantidad: i.cantidad
        }));
        const res = await api.post('/remitos/ingesta-buscar-pedidos', { cuit, items });
        pedidosCandidatos.value = res.data.candidatos || [];
        showModoIngesta.value = true;
    } catch(e) {
        console.error('[V5] Error buscando candidatos:', e);
        pedidosCandidatos.value = [];
        showModoIngesta.value = true;
    }
};

const autoSelectAddress = () => {
    if (clientAddresses.value.length === 0) return;
    
    manualAddressChange.value = false;
    addressAmbiguity.value = false;
    
    // Logic V15.8 (Carlos Policy):
    // 1. [V15.8.5 GOLD] Priorizar Sugerencia Heurística (Magic Wand)
    const suggested = clientAddresses.value.find(d => d.is_suggested);
    if (suggested) {
        selectedAddressId.value = suggested.id;
        return;
    }

    // 2. [V5.8.7] Heurística de Segmentación de Entrega (dedicated delivery vs fiscal-delivery)
    const allDelivery = clientAddresses.value.filter(d => d.es_entrega && d.activo !== false);
    const dedicatedDelivery = allDelivery.filter(d => !d.es_fiscal);

    if (dedicatedDelivery.length === 1) {
        // Encontramos exactamente un punto de entrega dedicado. Lo usamos sin warning.
        selectedAddressId.value = dedicatedDelivery[0].id;
        addressAmbiguity.value = false;
    } else if (dedicatedDelivery.length > 1) {
        // Ambigüedad entre varios puntos dedicados. Chequeamos predeterminado.
        const primary = dedicatedDelivery.find(d => d.es_predeterminado);
        if (primary) {
            selectedAddressId.value = primary.id;
            addressAmbiguity.value = false;
        } else {
            selectedAddressId.value = dedicatedDelivery[0].id;
            addressAmbiguity.value = true;
            notification.add('Atención: El cliente tiene múltiples sedes de entrega dedicadas. Verifique.', 'warning');
        }
    } else if (allDelivery.length === 1) {
        // Solo un punto de entrega (probablemente el fiscal).
        selectedAddressId.value = allDelivery[0].id;
        addressAmbiguity.value = false;
    } else if (allDelivery.length > 1) {
        // Caso raro: múltiples fiscales marcados como entrega.
        selectedAddressId.value = allDelivery[0].id;
        addressAmbiguity.value = true;
    } else {
        // Fallback: Fiscal
        const fiscal = clientAddresses.value.find(d => d.es_fiscal);
        selectedAddressId.value = fiscal ? fiscal.id : clientAddresses.value[0].id;
    }
}

const confirmIngesta = async () => {
    if (!parsedData.value || loading.value) return;

    // [V5-FIX] Guardia de ingesta incompleta: bloquear si el parser no extrajo datos mínimos
    const cuit = (parsedData.value.cliente?.cuit || '').replace(/-/g, '').trim();
    const items = parsedData.value.items || [];
    if (!cuit || cuit === '00000000000' || items.length === 0) {
        notification.add('El PDF no pudo extraer CUIT o ítems. Revisá el documento o completá los datos manualmente antes de continuar.', 'error');
        return;
    }

    // [V5-FLUJO-C] Si no se eligió modo de ingesta, buscar candidatos primero
    if (!modoIngestaSeleccionado.value) {
        await buscarPedidosCandidatos();
        return;
    }

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
                precio_unitario_neto: parseFloat(item.precio_unitario_neto || item.precio_unitario) || 0.0,
                alicuota_iva: parseFloat(item.alicuota_iva) || 21.0,
                codigo: item.codigo || null
            })),
            transporte_id: selectedTransportId.value,
            bultos: bultos.value,
            valor_declarado: valor_declarado.value,
            nuevo_domicilio: selectedAddressId.value === 'ADD_NEW' ? newAddress.value : null,
            modo_ingesta: modoIngestaSeleccionado.value || 'NUEVO',
            pedido_id_vinculado: pedidoVinculadoId.value || null,
        };

        // Si hay domicilio seleccionado de la lista
        if (selectedAddressId.value && selectedAddressId.value !== 'ADD_NEW') {
            payload.domicilio_id = selectedAddressId.value;
        }

        const res = await remitosService.confirmIngesta(payload);

        if (res.data && res.data.id) {
            if (modoIngestaSeleccionado.value === 'NUEVO') {
                // Pedido nuevo: redirigir a la ficha para revisión/aprobación antes de confirmar
                notification.add('Pedido creado. Revisá y aprobá la ficha antes de continuar.', 'info');
                reset();
                router.push({ name: 'PedidoEditar', params: { id: res.data.pedido_id } });
            } else {
                notification.add('Remito generado con éxito en Base de Datos', 'success');
                const pdfUrl = `/remitos/${res.data.id}/pdf`;
                window.open(pdfUrl, '_blank');
                reset();
            }
        }

    } catch (e) {
        console.error(e);
        notification.add('Error al generar remito: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
        loading.value = false;
    }
};
import { onMounted } from 'vue';
onMounted(() => {
    if (maestrosStore.transportes.length === 0) {
        maestrosStore.fetchTransportes();
    }
});
</script>

<style scoped>
.tokyo-bg {
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.05) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 20%);
}
</style>
