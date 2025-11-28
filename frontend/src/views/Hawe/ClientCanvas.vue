<template>
  <div class="flex h-full w-full bg-[#165078] text-white overflow-hidden font-sans">
    <!-- ZONE 1: STATIC DATA (Left Panel) -->
    <aside class="w-80 flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-md z-20">
      <!-- Header -->
      <div class="h-14 flex items-center justify-between px-6 border-b border-white/10 shrink-0">
        <div class="flex items-center gap-4">
            <button @click="$router.back()" class="flex items-center gap-2 text-white/50 hover:text-white transition-colors group" title="Volver a la pantalla anterior">
                <i class="fas fa-arrow-left group-hover:-translate-x-1 transition-transform"></i>
                <span class="font-outfit text-sm font-bold uppercase tracking-wider">Volver</span>
            </button>
            
            <div class="h-4 w-px bg-white/10"></div>

            <button @click="goToList" class="flex items-center gap-2 text-white/50 hover:text-cyan-400 transition-colors group" title="Ir al Listado de Clientes">
                <i class="fas fa-list"></i>
                <span class="font-outfit text-sm font-bold uppercase tracking-wider">Fichas</span>
            </button>
        </div>
        
        <button v-if="!isNew" @click="goToNew" class="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors group">
            <i class="fas fa-plus"></i>
            <span class="font-outfit text-sm font-bold uppercase tracking-wider">Nuevo</span>
        </button>
      </div>

      <!-- Form -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
        <!-- Avatar & Name -->
        <div class="text-center">
            <div class="relative group cursor-pointer inline-block">
                <div class="h-20 w-20 rounded-full bg-white/10 flex items-center justify-center text-3xl text-cyan-400 border-2 border-white/20 group-hover:border-cyan-400 transition-colors mx-auto">
                <i class="fas fa-building"></i>
                </div>
            </div>
            <div class="mt-4 space-y-2">
                <input 
                    v-model="form.razon_social" 
                    type="text" 
                    class="w-full bg-transparent text-center font-outfit text-xl font-bold text-white focus:outline-none border-b border-transparent focus:border-cyan-400 placeholder-white/30"
                    placeholder="Razón Social"
                />
                <input 
                    v-model="form.nombre_fantasia" 
                    type="text" 
                    class="w-full bg-transparent text-center text-sm text-white/70 focus:outline-none border-b border-transparent focus:border-cyan-400 placeholder-white/20"
                    placeholder="Nombre Fantasía (Opcional)"
                />
            </div>
        </div>

        <!-- Identifiers -->
        <div class="space-y-3">
            <div class="bg-white/5 rounded-lg p-3 border border-white/5">
                <label class="block text-[10px] font-bold uppercase text-white/40 mb-1">CUIT</label>
                <input 
                    v-model="form.cuit" 
                    @input="handleCuitInput"
                    type="text" 
                    class="w-full bg-transparent text-sm font-mono text-white focus:outline-none" 
                    placeholder="00000000000" 
                    maxlength="11"
                />
            </div>
            <div class="bg-white/5 rounded-lg p-3 border border-white/5">
                <label class="block text-[10px] font-bold uppercase text-white/40 mb-1">Segmento</label>
                <div class="flex gap-2">
                    <select v-model="form.segmento_id" class="flex-1 bg-transparent text-sm text-white focus:outline-none appearance-none [&>option]:bg-slate-900">
                        <option :value="null">Sin Segmento</option>
                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                    </select>
                    <button @click="showAddSegmento = true" class="text-cyan-400 hover:text-cyan-300 text-xs" title="Nuevo Segmento">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Payments & Admin -->
        <div class="space-y-4 pt-4 border-t border-white/10">
            <h3 class="text-xs font-bold uppercase text-white/50">Administración</h3>
            
            <div class="space-y-2">
                <label class="text-xs text-white/70">Portal de Pagos</label>
                <div class="flex items-center bg-white/5 rounded-lg px-3 py-2 border border-white/5">
                    <i class="fas fa-globe w-4 text-white/30"></i>
                    <input v-model="form.web_portal_pagos" type="text" class="flex-1 bg-transparent text-xs text-white focus:outline-none ml-2" placeholder="https://..." />
                </div>
            </div>

            <div class="space-y-2">
                <label class="text-xs text-white/70">Datos Acceso</label>
                <textarea v-model="form.datos_acceso_pagos" rows="2" class="w-full bg-white/5 rounded-lg px-3 py-2 border border-white/5 text-xs text-white focus:outline-none resize-none" placeholder="Usuario / Clave..."></textarea>
            </div>
        </div>
      </div>
    </aside>

    <!-- ZONE 3: DYNAMIC CANVAS (Center) -->
    <main class="flex-1 flex flex-col relative bg-gradient-to-br from-[#0f344e] to-[#0a1f2e]">
        <!-- Top Dashboard (Mock Data for now) -->
        <header class="h-32 px-8 py-6 flex items-start justify-between border-b border-white/5 bg-white/5">
            <div class="flex-1 mr-8">
                <!-- NEW CLIENT HEADER MODE -->
                <div v-if="isNew" class="space-y-4">
                    <h1 class="font-outfit text-2xl font-bold text-white/50 mb-1 uppercase">Alta de Cliente</h1>
                    <div class="bg-white/5 p-4 rounded-xl border border-white/10 shadow-lg backdrop-blur-sm">
                        <label class="block text-xs font-bold uppercase text-cyan-400 mb-1">Razón Social <span class="text-red-400">*</span></label>
                        <input 
                            v-model="form.razon_social" 
                            type="text" 
                            class="w-full bg-transparent text-2xl font-bold text-white focus:outline-none placeholder-white/20 border-b border-white/10 focus:border-cyan-400 transition-colors"
                            placeholder="Ingrese el nombre del cliente..."
                            autofocus
                        />
                    </div>
                </div>

                <!-- EXISTING CLIENT HEADER MODE -->
                <div v-else>
                    <h1 class="font-outfit text-2xl font-bold text-white mb-1">{{ form.razon_social }}</h1>
                    <div class="flex items-center gap-2">
                        <span v-if="form.activo" class="px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 text-[10px] font-bold border border-green-500/30">OPERATIVO</span>
                        <span v-else class="px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 text-[10px] font-bold border border-red-500/30">INACTIVO</span>
                        <span class="text-white/30 text-xs">•</span>
                        <span class="text-white/50 text-xs">Cód: {{ form.codigo_interno || '---' }}</span>
                    </div>
                </div>
            </div>

            <!-- Quick Stats Cards (Hidden in New Mode) -->
            <div v-if="!isNew" class="flex gap-4">
                <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[120px]">
                    <p class="text-[10px] uppercase text-white/40 font-bold">Saldo Actual</p>
                    <p class="text-lg font-mono text-white font-bold">$ 0.00</p>
                </div>
                <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[120px]">
                    <p class="text-[10px] uppercase text-white/40 font-bold">Última Compra</p>
                    <p class="text-lg text-white/70">--/--/--</p>
                </div>
                
                <!-- Pendientes Dropdown -->
                <div class="relative group">
                    <button class="bg-cyan-900/20 rounded-lg p-3 border border-cyan-500/30 min-w-[120px] text-left hover:bg-cyan-900/40 transition-colors w-full">
                        <p class="text-[10px] uppercase text-cyan-400 font-bold flex justify-between">
                            Pendientes <i class="fas fa-chevron-down"></i>
                        </p>
                        <p class="text-lg text-cyan-300 font-bold">0</p>
                    </button>
                    
                    <!-- Dropdown Content -->
                    <div class="absolute right-0 mt-2 w-64 bg-[#0a253a] border border-cyan-500/30 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 p-2">
                        <p class="text-xs text-white/50 uppercase font-bold mb-2 px-2">En curso</p>
                        <div class="space-y-1">
                            <div class="px-2 py-1.5 hover:bg-white/5 rounded text-sm text-white/70 flex justify-between">
                                <span>Cotizaciones</span>
                                <span class="font-bold text-white">0</span>
                            </div>
                            <div class="px-2 py-1.5 hover:bg-white/5 rounded text-sm text-white/70 flex justify-between">
                                <span>Pedidos Abiertos</span>
                                <span class="font-bold text-white">0</span>
                            </div>
                            <div class="px-2 py-1.5 hover:bg-white/5 rounded text-sm text-white/70 flex justify-between">
                                <span>Remitos s/Facturar</span>
                                <span class="font-bold text-white">0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Navigation Tools (Go to New) -->
            <div v-else class="flex items-start">
                 <!-- Placeholder for any specific tools for new mode -->
            </div>
        </header>

        <!-- Operational Body -->
        <div class="flex-1 overflow-y-auto p-8">
            <!-- NEW CLIENT BODY MODE -->
            <div v-if="isNew" class="max-w-3xl space-y-8">
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-white/5 p-6 rounded-xl border border-white/10">
                         <h3 class="text-sm font-bold text-white/90 mb-4 uppercase border-b border-white/10 pb-2">Datos Obligatorios</h3>
                         <div class="space-y-4">
                            <div>
                                <label class="block text-xs font-bold uppercase text-white/40 mb-1">CUIT <span class="text-red-400">*</span></label>
                                <input 
                                    v-model="form.cuit" 
                                    @input="handleCuitInput"
                                    type="text" 
                                    class="w-full bg-black/20 text-lg font-mono text-white focus:outline-none p-2 rounded border border-white/10 focus:border-cyan-400" 
                                    placeholder="00000000000" 
                                    maxlength="11"
                                />
                                <p class="text-[10px] text-white/30 mt-1 text-right">{{ form.cuit ? form.cuit.length : 0 }}/11</p>
                            </div>
                            <div>
                                <label class="block text-xs font-bold uppercase text-white/40 mb-1">Segmento</label>
                                <div class="flex gap-2">
                                    <select v-model="form.segmento_id" class="flex-1 bg-black/20 text-sm text-white focus:outline-none p-2 rounded border border-white/10 focus:border-cyan-400 appearance-none [&>option]:bg-slate-900">
                                        <option :value="null">Seleccionar Segmento...</option>
                                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                                    </select>
                                    <button @click="showAddSegmento = true" class="px-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-cyan-400 hover:text-cyan-300 transition-colors" title="Nuevo Segmento">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            </div>
                         </div>
                    </div>
                    

                    
                    <div class="bg-white/5 p-6 rounded-xl border border-white/10 opacity-50">
                         <h3 class="text-sm font-bold text-white/90 mb-4 uppercase border-b border-white/10 pb-2">Próximos Pasos</h3>
                         <ul class="space-y-2 text-sm text-white/60">
                             <li><i class="fas fa-check-circle text-white/20 mr-2"></i>Guardar Datos Básicos</li>
                             <li><i class="fas fa-circle text-white/20 mr-2"></i>Cargar Domicilios</li>
                             <li><i class="fas fa-circle text-white/20 mr-2"></i>Cargar Contactos</li>
                         </ul>
                         <p class="mt-4 text-xs text-cyan-400">Guarde el cliente para habilitar la carga de domicilios y contactos.</p>
                    </div>
                </div>
            </div>

            <!-- EXISTING CLIENT BODY MODE -->
            <div v-else>
                <!-- Tabs (Visual) -->
                <div class="flex border-b border-white/10 mb-6">
                    <button class="px-4 py-2 text-sm font-bold text-cyan-400 border-b-2 border-cyan-400">Bitácora & Notas</button>
                    <button class="px-4 py-2 text-sm font-medium text-white/50 hover:text-white transition-colors">Historial Compras</button>
                    <button class="px-4 py-2 text-sm font-medium text-white/50 hover:text-white transition-colors">Productos Habituales</button>
                </div>

                <!-- Content: Bitácora -->
                <div class="space-y-6 max-w-3xl">
                    <div class="bg-white/5 border border-white/10 rounded-xl p-4">
                        <div class="flex justify-between items-center mb-2">
                            <h3 class="text-sm font-bold text-white/90"><i class="fas fa-sticky-note mr-2 text-yellow-400"></i>Notas Internas</h3>
                            <span class="text-xs text-white/30">Visible solo para administración</span>
                        </div>
                        <textarea 
                            v-model="form.observaciones"
                            class="w-full h-32 bg-black/20 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-cyan-400 transition-all placeholder-white/20 resize-none"
                            placeholder="Escribe recordatorios, preferencias de entrega, o detalles importantes..."
                        ></textarea>
                    </div>

                    <!-- Placeholder for Future "Action Stream" -->
                    <div class="opacity-50 pointer-events-none">
                        <h4 class="text-xs font-bold uppercase text-white/30 mb-2">Actividad Reciente (Próximamente)</h4>
                        <div class="space-y-2">
                            <div class="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
                                <div class="h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400"><i class="fas fa-check"></i></div>
                                <div>
                                    <p class="text-sm text-white">Pedido #1234 Entregado</p>
                                    <p class="text-xs text-white/40">Hace 2 días</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ZONE 4: GLOBAL TOOLS (Footer) -->
        <footer class="h-16 bg-[#081824] border-t border-white/10 px-6 flex items-center justify-between shrink-0 z-30">
            <div class="flex items-center gap-4 text-xs text-white/40">
                <span><kbd class="bg-white/10 px-1.5 py-0.5 rounded text-white/70 font-mono">F10</kbd> Guardar</span>
                <span><kbd class="bg-white/10 px-1.5 py-0.5 rounded text-white/70 font-mono">ESC</kbd> Volver</span>
            </div>
            <div class="flex items-center gap-3">
                <button 
                    v-if="!isNew"
                    @click="cloneCliente"
                    class="px-4 py-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors"
                    title="Crear nuevo basado en este"
                >
                    <i class="fas fa-copy mr-2"></i>Clonar
                </button>
                <button 
                    v-if="!isNew && form.activo"
                    @click="deleteCliente"
                    class="px-4 py-2 rounded-lg text-red-400 hover:bg-red-900/20 hover:text-red-300 text-sm font-medium transition-colors"
                >
                    Dar de Baja
                </button>
                <button 
                    @click="saveCliente"
                    class="px-6 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-900/50 transition-all transform active:scale-95"
                >
                    Guardar Cambios
                </button>
            </div>
        </footer>
    </main>

    <!-- ZONE 2: REFERENCE (Right Panel) -->
    <aside class="w-80 flex flex-col border-l border-white/10 bg-black/20 backdrop-blur-md z-20">
        <!-- Header -->
        <div class="h-14 flex items-center justify-between px-6 border-b border-white/10 shrink-0">
            <h2 class="font-outfit text-sm font-bold uppercase tracking-wider text-white/70">Logística & Contactos</h2>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
            <!-- Domicilios -->
            <section>
                <div class="flex items-center justify-between mb-3">
                    <h3 class="text-xs font-bold text-white/50 uppercase">Domicilios</h3>
                    <button @click="addDomicilio" class="text-cyan-400 hover:text-cyan-300 text-xs"><i class="fas fa-plus"></i></button>
                </div>
                <div class="space-y-2">
                    <div v-for="dom in domicilios" :key="dom.id" class="bg-white/5 border border-white/10 rounded-lg p-3 transition-colors group">
                        <!-- VIEW MODE -->
                        <div v-if="editingDomicilioId !== dom.id">
                            <div class="flex justify-between items-start mb-1">
                                <span v-if="dom.es_fiscal" class="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 rounded border border-purple-500/30">FISCAL</span>
                                <span v-else class="text-[10px] bg-gray-700 text-gray-300 px-1.5 rounded">SUCURSAL</span>
                                <button @click="editDomicilio(dom)" class="text-[10px] text-white/30 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"><i class="fas fa-pencil-alt"></i></button>
                            </div>
                            <p class="text-sm font-medium text-white leading-tight">{{ dom.calle }} {{ dom.numero }}</p>
                            <p class="text-xs text-white/50">{{ dom.localidad }}</p>
                            <div class="mt-2 flex items-center gap-2 text-xs text-white/40">
                                <i class="fas fa-truck"></i> {{ dom.transporte?.nombre || 'Sin Transporte' }}
                            </div>
                        </div>

                        <!-- EDIT MODE -->
                        <div v-else class="space-y-2">
                            <input v-model="tempDomicilio.calle" placeholder="Calle" class="w-full bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                            <div class="flex gap-2">
                                <input v-model="tempDomicilio.numero" placeholder="Nro" class="w-1/3 bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                                <input v-model="tempDomicilio.localidad" placeholder="Localidad" class="w-2/3 bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                            </div>
                            <div class="flex justify-end gap-2 mt-2">
                                <button @click="cancelEditDomicilio" class="text-red-400 hover:text-red-300"><i class="fas fa-times"></i></button>
                                <button @click="saveDomicilio" class="text-green-400 hover:text-green-300"><i class="fas fa-check"></i></button>
                            </div>
                        </div>
                    </div>
                    <div v-if="domicilios.length === 0" class="text-center py-4 border border-dashed border-white/10 rounded-lg">
                        <p class="text-xs text-white/30">Sin domicilios</p>
                    </div>
                </div>
            </section>

            <!-- Contactos -->
            <section>
                <div class="flex items-center justify-between mb-3">
                    <h3 class="text-xs font-bold text-white/50 uppercase">Contactos</h3>
                    <button @click="addContacto" class="text-cyan-400 hover:text-cyan-300 text-xs"><i class="fas fa-plus"></i></button>
                </div>
                <div class="space-y-2">
                    <div v-for="contact in contactos" :key="contact.id" class="bg-white/5 border border-white/10 rounded-lg p-3 transition-colors group">
                        <!-- VIEW MODE -->
                        <div v-if="editingContactoId !== contact.id" class="flex items-center gap-3">
                            <div class="h-8 w-8 rounded-full bg-gradient-to-br from-pink-500 to-orange-400 flex items-center justify-center text-xs font-bold text-white shrink-0">
                                {{ contact.nombre ? contact.nombre.substring(0,2).toUpperCase() : 'NN' }}
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="flex justify-between">
                                    <p class="text-sm font-bold text-white truncate">{{ contact.nombre }}</p>
                                    <button @click="editContacto(contact)" class="text-[10px] text-white/30 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"><i class="fas fa-pencil-alt"></i></button>
                                </div>
                                <p class="text-[10px] text-white/50 uppercase truncate">{{ contact.rol || 'Sin Rol' }}</p>
                            </div>
                        </div>

                        <!-- EDIT MODE -->
                        <div v-else class="space-y-2">
                            <input v-model="tempContacto.nombre" placeholder="Nombre" class="w-full bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                            <input v-model="tempContacto.rol" placeholder="Rol (Ej: Comprador)" class="w-full bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                            <input v-model="tempContacto.email" placeholder="Email" class="w-full bg-black/20 border border-white/10 rounded px-2 py-1 text-xs text-white focus:border-cyan-400 outline-none" />
                            <div class="flex justify-end gap-2 mt-2">
                                <button @click="cancelEditContacto" class="text-red-400 hover:text-red-300"><i class="fas fa-times"></i></button>
                                <button @click="saveContacto" class="text-green-400 hover:text-green-300"><i class="fas fa-check"></i></button>
                            </div>
                        </div>
                    </div>
                    <div v-if="contactos.length === 0" class="text-center py-4 border border-dashed border-white/10 rounded-lg">
                        <p class="text-xs text-white/30">Sin contactos</p>
                    </div>
                </div>
            </section>
        </div>
    </aside>
    <!-- Quick Add Segmento Modal (Global) -->
    <div v-if="showAddSegmento" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
        <div class="bg-[#0a253a] border border-white/10 rounded-xl p-6 w-96 shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-4">Nuevo Segmento</h3>
            <input 
                v-model="newSegmentoName" 
                @keydown.enter="createSegmento"
                type="text" 
                class="w-full bg-black/20 border border-white/10 rounded p-2 text-white focus:border-cyan-400 outline-none mb-4" 
                placeholder="Nombre del Segmento" 
                autofocus
            />
            <div class="flex justify-end gap-3">
                <button @click="showAddSegmento = false" class="text-white/50 hover:text-white text-sm">Cancelar</button>
                <button @click="createSegmento" class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded text-sm font-bold">Crear</button>
            </div>
        </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientesStore } from '../../stores/clientes'
import { useMaestrosStore } from '../../stores/maestros'
import { useNotificationStore } from '../../stores/notification'
import { useFormHistory } from '../../composables/useFormHistory'

const route = useRoute()
const router = useRouter()
const clienteStore = useClientesStore()
const maestrosStore = useMaestrosStore()
const notificationStore = useNotificationStore()

// Initialize History with default state
const { state: form, undo, redo, reset, canUndo, canRedo } = useFormHistory({
    razon_social: '',
    nombre_fantasia: '',
    cuit: '',
    segmento_id: null,
    activo: true,
    observaciones: '',
    web_portal_pagos: '',
    datos_acceso_pagos: '',
    codigo_interno: null
})

const domicilios = ref([])
const contactos = ref([])
const segmentos = ref([])
const isNew = computed(() => route.params.id === 'new')

onMounted(async () => {
    await maestrosStore.fetchSegmentos()
    segmentos.value = maestrosStore.segmentos

    if (!isNew.value) {
        await loadCliente(route.params.id)
    }
})

const loadCliente = async (id) => {
    const cliente = await clienteStore.fetchClienteById(id)
    if (cliente) {
        reset({ ...cliente }) // Reset history with loaded data
        domicilios.value = cliente.domicilios || []
        contactos.value = cliente.contactos || []
    }
}

const saveCliente = async () => {
    // Validation
    if (!form.value.razon_social || !form.value.cuit) {
        notificationStore.add('Razón Social y CUIT son obligatorios', 'error')
        return
    }

    try {
        if (isNew.value) {
            const newCliente = await clienteStore.createCliente(form.value)
            notificationStore.add('Cliente creado con éxito', 'success')
            router.replace({ name: 'HaweClientCanvas', params: { id: newCliente.id } })
            // Reload to get full object with defaults
            await loadCliente(newCliente.id)
        } else {
            await clienteStore.updateCliente(route.params.id, form.value)
            notificationStore.add('Cliente actualizado con éxito', 'success')
            router.back() // Return to list after update
        }
    } catch (error) {
        notificationStore.add(error.message || 'Error al guardar', 'error')
    }
}

const deleteCliente = async () => {
    if (!confirm('¿Estás seguro de dar de baja este cliente?')) return
    try {
        await clienteStore.deleteCliente(route.params.id)
        notificationStore.add('Cliente dado de baja', 'success')
        form.value.activo = false // Update UI immediately
    } catch (error) {
        notificationStore.add(error.message || 'Error al dar de baja', 'error')
    }
}

const hardDeleteCliente = async () => {
    if (!confirm('¿ESTÁS SEGURO? Esto eliminará permanentemente al cliente y sus datos. No se puede deshacer.')) return
    try {
        await clienteStore.hardDeleteCliente(route.params.id)
        notificationStore.add('Cliente eliminado permanentemente', 'success')
        router.push({ name: 'HaweView' })
    } catch (error) {
        notificationStore.add(error.message || 'Error al eliminar', 'error')
    }
}

// Keyboard Shortcuts
// Keyboard Shortcuts
const goToList = () => {
    router.push({ name: 'HaweHome' })
}

const goToNew = () => {
    router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
    // Force reset if we are already in the component but route changes (Vue reuses component)
    // Watcher on route.params.id handles this usually, but let's ensure clean state
    reset({
        razon_social: '',
        nombre_fantasia: '',
        cuit: '',
        segmento_id: null,
        activo: true,
        observaciones: '',
        web_portal_pagos: '',
        datos_acceso_pagos: '',
        codigo_interno: null
    })
    domicilios.value = []
    contactos.value = []
}

const cloneCliente = () => {
    // Prepare form for new entry based on current
    const clonedData = {
        ...form.value,
        razon_social: form.value.razon_social + ' (Copia)',
        cuit: '', // Clear CUIT as it must be unique
        codigo_interno: null,
        id: undefined,
        created_at: undefined,
        updated_at: undefined
    }
    
    // Navigate to new with state? Or just reset form and change URL?
    // Easiest is to go to 'new' route and pre-fill.
    // But router.push doesn't pass state easily to same component without query params or store.
    // Let's manually set state and change route.
    router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
    reset(clonedData)
    // Keep domicilios and contactos? User said "modify little".
    // Usually logistics might be different, but contacts might be same?
    // Let's keep them as "new" (no IDs)
    domicilios.value = domicilios.value.map(d => ({ ...d, id: undefined, cliente_id: undefined }))
    contactos.value = contactos.value.map(c => ({ ...c, id: undefined, cliente_id: undefined }))
    
    notificationStore.add('Cliente clonado. Ajuste CUIT y Razón Social.', 'info')
}

const handleCuitInput = (e) => {
    // Strip non-numeric characters
    let value = e.target.value.replace(/\D/g, '')
    // Limit to 11 digits
    if (value.length > 11) {
        value = value.slice(0, 11)
    }
    // Update model
    form.value.cuit = value
    // Force update input value if characters were stripped (Vue v-model sometimes needs help with this)
    e.target.value = value
}

// Segmento Quick Add
const showAddSegmento = ref(false)
const newSegmentoName = ref('')

const createSegmento = async () => {
    if (!newSegmentoName.value.trim()) return
    try {
        const newSeg = await maestrosStore.createSegmento({ nombre: newSegmentoName.value, activo: true })
        // Refresh local list (store action usually refetches, but let's be sure)
        await maestrosStore.fetchSegmentos()
        segmentos.value = maestrosStore.segmentos
        // Select the new one
        // Note: createSegmento in store doesn't return the object, it returns void. 
        // We need to find it or update store to return it.
        // For now, let's assume it's the last one or find by name.
        const created = segmentos.value.find(s => s.nombre === newSegmentoName.value)
        if (created) {
            form.value.segmento_id = created.id
        }
        
        notificationStore.add('Segmento creado', 'success')
        showAddSegmento.value = false
        newSegmentoName.value = ''
    } catch (error) {
        notificationStore.add('Error al crear segmento', 'error')
    }
}

// Keyboard Shortcuts
const handleKeydown = (e) => {
    const isCtrl = e.ctrlKey || e.metaKey
    const key = e.key.toLowerCase()

    // Save (F10)
    if (e.key === 'F10') {
        e.preventDefault()
        saveCliente()
    }
    
    // New (F4)
    if (e.key === 'F4') {
        e.preventDefault()
        goToNew()
    }
    
    // Undo (Ctrl+Z)
    if (isCtrl && key === 'z' && !e.shiftKey) {
        e.preventDefault()
        undo()
        if (canUndo()) notificationStore.add('Deshacer', 'info')
    }
    
    // Redo (Ctrl+Shift+Z or Ctrl+Y)
    if (isCtrl && ((key === 'z' && e.shiftKey) || key === 'y')) {
        e.preventDefault()
        redo()
        if (canRedo()) notificationStore.add('Rehacer', 'info')
    }
}

window.addEventListener('keydown', handleKeydown)
// Clean up listener would be good in onUnmounted but script setup handles it reasonably well if we are careful. 
// Ideally: onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>
