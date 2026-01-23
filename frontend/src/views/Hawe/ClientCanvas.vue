<template>
  <div class="flex flex-col h-full w-full bg-[#0f172a] rounded-2xl border-2 border-cyan-500 shadow-[0_0_30px_rgba(6,182,212,0.4)] overflow-hidden relative tokyo-bg neon-cyan">
      
      <!-- HEADER (Cyan Style - STICKY) -->
      <div class="w-full bg-cyan-950/30 border-b border-cyan-500/20 p-4 flex justify-between items-center backdrop-blur-md shrink-0 z-50">
          <div class="flex items-center gap-4">
              <button @click="goBackToSource" class="text-white/50 hover:text-cyan-400 transition-colors">
                  <i class="fas fa-arrow-left"></i>
              </button>
              <h1 class="text-xl font-bold text-cyan-400 tracking-wider flex items-center gap-3 uppercase">
                  <i class="fas fa-user-tie"></i> Ficha de Cliente V5
              </h1>
          </div>
          <div class="flex items-center gap-4">
              <span v-if="form.codigo_interno" class="font-mono text-xs text-cyan-500/50">#{{ form.codigo_interno }}</span>
              <div class="h-6 w-px bg-white/10"></div>
              <button v-if="!isNew" @click="goToNew" class="text-xs font-bold text-white/40 hover:text-white uppercase tracking-tighter">
                  <i class="fas fa-plus mr-1"></i> Nuevo
              </button>
          </div>
      </div>

      <!-- MAIN SCROLLABLE CONTENT -->
      <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-500/20 p-4 space-y-4">
          
          <!-- BLOCK 1: IDENTITY & MASTER DATA (LOGICAL REORDER V5.3) -->
          <section class="bg-black/40 border border-white/10 rounded-2xl p-4 backdrop-blur-md shadow-xl relative overflow-hidden group">
              <div class="absolute top-0 left-0 w-1 h-full bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.8)]"></div>
              
              <div class="space-y-4">
                  <!-- LINE 1: OPERATIONS (Razón Social / Fantasía / Fiscal / Segmento / Activo) -->
                  <div class="grid grid-cols-12 gap-3 items-end">
                      <!-- Razón Social -->
                      <div class="col-span-12 lg:col-span-3 relative">
                          <label class="text-[9px] font-bold text-cyan-400 uppercase tracking-widest block mb-0.5">Razón Social</label>
                          <input 
                              ref="canteraInput"
                              v-model="form.razon_social" 
                              @input="handleSearchCantera"
                              type="text" 
                              class="w-full bg-transparent text-lg font-bold text-white focus:outline-none border-b border-white/5 focus:border-cyan-400 transition-all placeholder-white/10"
                              placeholder="Empresa..."
                          />
                          <!-- Cantera Results -->
                          <Teleport to="body">
                            <div v-if="canteraResults.length > 0 && isNew" :style="canteraResultsStyle" class="fixed bg-[#0a253a] border border-cyan-500/30 rounded-lg shadow-2xl z-[100] overflow-hidden">
                                  <ul class="overflow-y-auto h-full">
                                      <li v-for="res in canteraResults" :key="res.id" @click="importFromCantera(res)" class="px-4 py-3 hover:bg-white/5 cursor-pointer border-b border-white/5 last:border-0 group transition-colors">
                                          <div class="flex justify-between items-start">
                                              <div>
                                                  <p class="font-bold text-white group-hover:text-cyan-300 text-sm">{{ res.razon_social }}</p>
                                                  <p class="text-[9px] text-white/30 font-mono">CUIT: {{ res.cuit }}</p>
                                              </div>
                                              <span class="text-[8px] px-1.5 py-0.5 rounded bg-cyan-900/30 text-cyan-400 border border-cyan-500/30">CANTERA</span>
                                          </div>
                                      </li>
                                  </ul>
                            </div>
                          </Teleport>
                      </div>

                      <!-- Fantasía -->
                      <div class="col-span-12 lg:col-span-2">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-0.5">Fantasía</label>
                          <input v-model="form.nombre_fantasia" type="text" class="w-full bg-white/5 border border-white/5 rounded px-2 py-1 text-xs text-white focus:outline-none" />
                      </div>

                      <!-- Domicilio Fiscal -->
                      <div class="col-span-12 lg:col-span-3 bg-cyan-950/10 border border-cyan-500/10 rounded-lg p-1.5 relative group/fiscal">
                          <div class="flex justify-between items-center mb-0.5">
                              <label class="text-[8px] font-bold text-cyan-400/50 uppercase tracking-widest"><i class="fas fa-file-invoice mr-1"></i> D. FISCAL</label>
                              <button @click="openFiscalEditor" class="text-[10px] text-cyan-400 hover:text-white opacity-0 group-hover/fiscal:opacity-100 transition-opacity">
                                  <i class="fas fa-edit"></i>
                              </button>
                          </div>
                          <p class="text-[10px] text-white/50 truncate font-medium">{{ computedFiscalAddress }}</p>
                      </div>

                      <!-- Segmento -->
                      <div class="col-span-12 lg:col-span-2">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Segmento</label>
                          <select v-model="form.segmento_id" @change="handleSegmentoChange" class="w-full bg-white/5 border border-white/10 rounded px-2 py-1 text-xs text-white focus:outline-none appearance-none [&>option]:bg-slate-900">
                               <option :value="null">Sin Segmento</option>
                               <option value="__NEW__" class="text-green-400 font-bold">+ Nuevo</option>
                               <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                          </select>
                      </div>

                      <!-- Status Slider -->
                      <div class="col-span-12 lg:col-span-2">
                           <div class="flex items-center justify-between bg-black/40 rounded-lg px-2 py-1.5 border border-white/10">
                               <span class="text-[8px] font-bold uppercase" :class="form.activo ? 'text-green-400' : 'text-red-400'">
                                   {{ form.activo ? 'OPERATIVO' : 'INACTIVO' }}
                               </span>
                               <button @click="form.activo = !form.activo" class="relative inline-flex h-3.5 w-7 items-center rounded-full transition-colors focus:outline-none bg-white/10" :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'">
                                   <span class="inline-block h-2 w-2 transform rounded-full bg-white transition-transform" :class="form.activo ? 'translate-x-3.5' : 'translate-x-1'" />
                               </button>
                           </div>
                      </div>
                  </div>

                  <!-- LINE 2: FISCAL & COMMERCIAL (CUIT / IVA / Lista de Precios) -->
                  <div class="grid grid-cols-12 gap-4 items-end border-t border-white/5 pt-3">
                      <div class="col-span-4">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-0.5">CUIT</label>
                          <input v-model="form.cuit" @input="handleCuitInput" type="text" class="w-full bg-white/5 border border-white/5 rounded px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                      </div>
                      <div class="col-span-4">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Condición IVA</label>
                          <select v-model="form.condicion_iva_id" class="w-full bg-white/5 border border-white/10 rounded px-2 py-1 text-xs text-white focus:outline-none appearance-none [&>option]:bg-slate-900">
                              <option :value="null">IVA...</option>
                              <option v-for="iva in condicionesIva" :key="iva.id" :value="iva.id">{{ iva.nombre }}</option>
                          </select>
                      </div>
                      <div class="col-span-4">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Lista de Precios</label>
                          <select v-model="form.lista_precios_id" class="w-full bg-cyan-900/10 border border-cyan-500/20 rounded px-2 py-1 text-xs text-cyan-300 font-bold focus:outline-none appearance-none [&>option]:bg-slate-900">
                              <option :value="null">Lista Automática</option>
                              <option v-for="lp in listasPrecios" :key="lp.id" :value="lp.id">{{ lp.nombre }}</option>
                          </select>
                      </div>
                  </div>
              </div>
          </section>

          <!-- BLOCK 2: LOGISTICS 5.2 (COLLAPSIBLE BY DEFAULT) -->
          <section class="space-y-2">
              <div 
                  @click="expandLogistics = !expandLogistics"
                  class="flex items-center justify-between px-3 py-2 bg-cyan-900/10 border border-cyan-500/20 rounded-xl cursor-pointer hover:bg-cyan-900/20 transition-all select-none"
              >
                  <h3 class="text-[10px] font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-2">
                      <i class="fas fa-truck-loading"></i> Logística y Tratos de Entrega
                      <span v-if="domiciliosLogistica.length > 0" class="text-[9px] bg-cyan-500/30 text-cyan-300 px-1.5 py-0.5 rounded-full ml-2">
                          {{ domiciliosLogistica.length }} {{ domiciliosLogistica.length === 1 ? 'Locación' : 'Locaciones' }}
                      </span>
                  </h3>
                  <div class="flex items-center gap-4">
                      <span v-if="!expandLogistics && domiciliosLogistica.length > 0" class="text-[10px] text-white/30 italic truncate max-w-[200px]">
                          {{ domiciliosLogistica[0].calle }}...
                      </span>
                      <i class="fas text-cyan-400/50 transition-transform duration-300" :class="expandLogistics ? 'fa-chevron-up rotate-180' : 'fa-chevron-down'"></i>
                  </div>
              </div>
              
              <div v-if="expandLogistics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 px-1 animate-in slide-in-from-top-2 duration-300">
                  <div 
                      v-for="dom in domiciliosLogistica" 
                      :key="dom.id"
                      @click="openDomicilioTab(dom)"
                      class="bg-white/5 border border-white/10 rounded-xl p-3 hover:border-cyan-500/30 transition-all cursor-pointer group relative overflow-hidden"
                  >
                      <!-- Note Alert Indicator -->
                      <div v-if="dom.observaciones" class="absolute top-0 right-0 p-1.5 z-10">
                          <i class="fas fa-exclamation-circle text-amber-500 animate-pulse text-[10px]"></i>
                      </div>

                      <div class="flex justify-between items-start mb-2">
                          <span class="text-[9px] font-bold uppercase opacity-40">{{ dom.alias || 'Sucursal' }}</span>
                          <i class="fas fa-map-marker-alt text-cyan-400/50 text-xs"></i>
                      </div>
                      
                      <div class="mb-3">
                          <p class="text-[11px] font-bold text-white truncate">{{ dom.calle }} {{ dom.numero }}</p>
                          <p class="text-[10px] text-white/40 truncate">{{ dom.localidad }}</p>
                      </div>

                      <div class="flex items-center gap-2 text-[10px] text-emerald-400/70 border-t border-white/5 pt-2 mt-auto">
                          <i class="fas fa-truck text-[9px]"></i>
                          <span class="font-bold truncate">{{ dom.transporte?.nombre || dom.transporte_nombre || 'Retira Cliente' }}</span>
                      </div>
                  </div>

                  <!-- Add New Location directly in expanded view -->
                  <div @click="openDomicilioTab()" class="border-2 border-dashed border-white/5 rounded-xl p-3 flex flex-col items-center justify-center gap-1 hover:border-cyan-500/30 hover:bg-white/5 transition-all cursor-pointer text-white/20 hover:text-cyan-400">
                      <i class="fas fa-plus-circle text-sm"></i>
                      <span class="text-[9px] font-bold uppercase tracking-widest">Nueva Planta</span>
                  </div>
              </div>
          </section>

          <!-- BLOCK 3: COMMERCIAL INTELLIGENCE -->
          <div class="grid grid-cols-12 gap-4">
              <!-- Left: History -->
              <div class="col-span-12 lg:col-span-7 space-y-2">
                   <h3 class="text-[10px] font-bold text-white/40 uppercase tracking-widest px-2 flex items-center gap-2">
                      <i class="fas fa-history"></i> Historial Reciente
                  </h3>
                  <div class="bg-black/40 border border-white/5 rounded-xl overflow-hidden min-h-[200px]">
                      <table class="w-full text-left border-collapse">
                          <thead class="bg-white/5 border-b border-white/10">
                              <tr class="text-[9px] font-bold text-white/30 uppercase tracking-widest">
                                  <th class="px-4 py-2">Fecha</th>
                                  <th class="px-4 py-2">Pedido</th>
                                  <th class="px-4 py-2">Total</th>
                                  <th class="px-4 py-2 text-right">Estado</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="h in historial" :key="h.id" class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer text-[11px]">
                                  <td class="px-4 py-2 font-mono text-white/60">{{ h.fecha }}</td>
                                  <td class="px-4 py-2 font-bold text-cyan-400 hover:text-cyan-300" @click.stop="goToPedido(h.id)">
                                      <i class="fas fa-external-link-alt text-[9px] mr-1 opacity-50"></i>{{ h.id }}
                                  </td>
                                  <td class="px-4 py-2 font-mono font-bold text-white">$ {{ h.total.toLocaleString() }}</td>
                                  <td class="px-4 py-2 text-right">
                                      <span class="text-[8px] font-bold uppercase px-1.5 py-0.5 rounded-full border" :class="statusColor(h.estado)">
                                          {{ h.estado }}
                                      </span>
                                  </td>
                              </tr>
                          </tbody>
                      </table>
                  </div>
              </div>

              <!-- Right: Frequent Products -->
              <div class="col-span-12 lg:col-span-5 space-y-2">
                  <h3 class="text-[10px] font-bold text-white/40 uppercase tracking-widest px-2 flex items-center gap-2">
                      <i class="fas fa-star text-yellow-500"></i> Productos Habituales
                  </h3>
                  <div class="bg-black/40 border border-white/5 rounded-xl p-3 space-y-3 min-h-[200px]">
                      <div class="relative">
                          <i class="fas fa-search absolute left-2 top-1/2 -translate-y-1/2 text-white/20 text-xs"></i>
                          <input type="text" placeholder="Buscar favorito..." class="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/50" />
                      </div>
                      <div class="grid grid-cols-1 gap-2 overflow-y-auto max-h-[160px] scrollbar-thin scrollbar-thumb-white/5">
                          <div v-for="p in productosHabituales" :key="p.id" class="flex items-center gap-3 p-1.5 bg-white/5 border border-transparent hover:border-white/10 rounded-lg transition-all group">
                              <div class="h-8 w-8 bg-black/40 rounded flex items-center justify-center text-[10px] font-bold text-cyan-500 border border-white/5 shrink-0">
                                  {{ p.sku.substring(0,2) }}
                              </div>
                              <div class="flex-1 min-w-0">
                                  <p class="text-[11px] font-bold text-white truncate">{{ p.nombre }}</p>
                                  <p class="text-[9px] text-white/30 truncate">{{ p.sku }}</p>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
          </div>

          <!-- BLOCK 4: CONTACTS (COMPACT) -->
          <section class="space-y-2">
               <div class="flex items-center justify-between px-2">
                  <h3 class="text-[10px] font-bold text-white/40 uppercase tracking-widest flex items-center gap-2">
                      <i class="fas fa-address-book"></i> Agenda de Vínculos
                  </h3>
                  <button @click="addContacto" class="text-[9px] font-bold text-white/40 hover:text-white uppercase transition-colors">
                      <i class="fas fa-user-plus mr-1"></i> Vincular
                  </button>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  <div 
                      v-for="contact in contactos" 
                      :key="contact.id" 
                      @click="editContacto(contact)"
                      class="bg-white/5 border border-white/10 rounded-xl p-2 flex items-center gap-3 hover:border-cyan-500/30 transition-all cursor-pointer group"
                  >
                      <div class="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-600 to-emerald-400 flex items-center justify-center text-xs font-bold text-white shadow shadow-cyan-500/20 shrink-0">
                          {{ contact.persona?.nombre_completo?.substring(0,1) || 'N' }}
                      </div>
                      <div class="min-w-0">
                          <p class="text-[10px] font-bold text-white truncate leading-tight">{{ contact.persona?.nombre_completo || 'NN' }}</p>
                          <p class="text-[8px] uppercase font-bold text-cyan-500/70 truncate">{{ contact.tipo_contacto?.nombre || contact.rol || 'Rol' }}</p>
                      </div>
                  </div>
              </div>
          </section>

          <!-- BLOCK 5: NOTES (BOTTOM) -->
          <section class="space-y-3 pt-6">
              <div class="flex items-center gap-2 px-2">
                  <h3 class="text-xs font-bold text-white/40 uppercase tracking-[0.2em]">Observaciones e Instrucciones Internas</h3>
                  <div class="h-px flex-1 bg-white/5"></div>
              </div>
              <div class="relative group">
                  <div class="absolute inset-0 bg-yellow-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                  <textarea 
                    v-model="form.observaciones"
                    class="w-full h-40 bg-black/40 border border-white/10 rounded-2xl p-6 text-sm text-yellow-100/70 focus:text-yellow-100 focus:outline-none focus:border-yellow-500/30 transition-all placeholder-white/5 resize-none shadow-inner"
                    placeholder="Ingrese aquí advertencias, horarios de carga, o preferencias del comprador..."
                  ></textarea>
                  <div v-if="form.observaciones" class="absolute bottom-4 right-4 text-yellow-500/30 flex items-center gap-2 select-none">
                      <i class="fas fa-sticky-note"></i>
                      <span class="text-[9px] font-bold uppercase tracking-widest text-yellow-500/30">Nota Activa</span>
                  </div>
              </div>
          </section>

      </div>

      <!-- FOOTER TOOLS (Cyan Style) -->
      <footer class="h-20 bg-cyan-950/20 border-t border-cyan-500/20 px-8 flex items-center justify-between shrink-0 backdrop-blur-md z-30">
          <div class="flex items-center gap-6">
              <div class="flex items-center gap-4 text-[10px] font-mono text-cyan-500/50 uppercase tracking-widest border-r border-white/10 pr-6">
                  <span>F10: Guardar</span>
                  <span class="w-1.5 h-1.5 rounded-full bg-cyan-500/30"></span>
                  <span>ESC: Volver</span>
              </div>
              <!-- Note Indicator -->
              <div @click="scrollToNotes" class="flex items-center gap-2 cursor-pointer group select-none">
                  <div class="h-2 w-2 rounded-full animate-pulse" :class="form.observaciones ? 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.8)]' : 'bg-gray-600'"></div>
                  <span class="text-[10px] font-black uppercase tracking-widest transition-colors" :class="form.observaciones ? 'text-orange-500 group-hover:text-orange-400' : 'text-gray-600'">
                      {{ form.observaciones ? 'Notas Activas' : 'Sin Notas' }}
                  </span>
                  <i v-if="form.observaciones" class="fas fa-chevron-up text-[9px] text-orange-500/50 group-hover:text-orange-500 transition-all"></i>
              </div>
          </div>

          <div class="flex items-center gap-4">
              <button @click="cloneCliente" class="px-6 py-2.5 rounded-full text-white/50 hover:text-white hover:bg-white/5 transition-all text-xs font-bold uppercase tracking-widest border border-white/10">
                  <i class="fas fa-copy mr-2"></i> Clonar
              </button>
              
               <button 
                   @click="saveCliente"
                   :disabled="guardLoading"
                   class="px-10 py-3 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black uppercase tracking-[0.2em] shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all flex items-center gap-3 active:scale-95 disabled:opacity-50 disabled:cursor-wait"
               >
                   <i v-if="guardLoading" class="fas fa-spinner fa-spin"></i>
                   <span v-else>{{ isNew ? 'Crear Cliente' : 'Actualizar Registro' }}</span>
                   <i v-if="!guardLoading" class="fas fa-check"></i>
               </button>
          </div>
      </footer>

      <!-- Modals & Context Menus (Existing) -->
      <SegmentoForm v-if="showSegmentoModal" :show="showSegmentoModal" :id="editingSegmentoId" @close="closeSegmentoModal" @saved="handleSegmentoSaved" />
      <SegmentoList v-if="showSegmentoList" :isStacked="true" class="fixed inset-0 z-[100] bg-[#0f172a] m-10 rounded-2xl shadow-2xl border border-cyan-500/30" @close="showSegmentoList = false" />
      <DomicilioForm v-if="activeTab === 'DOMICILIO'" :show="true" :domicilio="selectedDomicilio" @close="activeTab = 'CLIENTE'" @saved="handleDomicilioSaved" />
      <ContactoForm v-if="showContactoForm" :show="showContactoForm" :clienteId="String(form.id)" :contacto="selectedContacto" @close="showContactoForm = false" @saved="handleContactoSaved" />
      
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientesStore } from '../../stores/clientes'
import { useMaestrosStore } from '../../stores/maestros'
import { useNotificationStore } from '../../stores/notification'
import canteraService from '../../services/canteraService'
import SegmentoForm from '../Maestros/SegmentoForm.vue'
import SegmentoList from '../Maestros/SegmentoList.vue'
import DomicilioForm from './components/DomicilioForm.vue'
import ContactoForm from './components/ContactoForm.vue'
import { useAuditSemaphore } from '../../composables/useAuditSemaphore'

const route = useRoute()
const router = useRouter()
const store = useClientesStore()
const maestrosStore = useMaestrosStore()
const notificationStore = useNotificationStore()

// Audit Logic
const { evaluateCliente } = useAuditSemaphore()

const isNew = ref(false)
const expandLogistics = ref(false)
const activeTab = ref('CLIENTE') // 'CLIENTE', 'DOMICILIO', 'CONTACTO'

const form = ref({
    id: null,
    razon_social: '',
    nombre_fantasia: '',
    cuit: '',
    condicion_iva_id: null,
    lista_precios_id: null,
    vendedor_id: null,
    segmento_id: null,
    limite_credito: 0,
    dias_vencimiento: 30,
    activo: true,
    observaciones: '',
    web_portal_pagos: '',
    datos_acceso_pagos: '',
    saldo: 0,
    fecha_ultima_compra: null,
    codigo_interno: ''
})
const domicilios = ref([])
const contactos = ref([])
const historial = ref([])
const productosHabituales = ref([])

// Computed Helpers
const condicionesIva = computed(() => maestrosStore.condicionesIva)
const segmentos = computed(() => maestrosStore.segmentos)
const listasPrecios = computed(() => maestrosStore.listasPrecios)

const auditResult = computed(() => {
    const tempClient = {
        ...form.value,
        domicilios: domicilios.value, 
        domicilio_fiscal_resumen: null 
    }
    return evaluateCliente(tempClient)
})
const returnUrl = computed(() => route.query.returnUrl)

const computedFiscalAddress = computed(() => {
    if (domicilios.value && domicilios.value.length > 0) {
        const fiscal = domicilios.value.find(d => d.es_fiscal)
        if (fiscal) return `${fiscal.calle} ${fiscal.numero}, ${fiscal.localidad}`
    }
    return 'Definir Domicilio Fiscal'
})

const domiciliosLogistica = computed(() => {
    return domicilios.value.filter(d => !d.es_fiscal && d.activo !== false)
})

const visibleLogistics = computed(() => {
    if (expandLogistics.value) return domiciliosLogistica.value
    return domiciliosLogistica.value.slice(0, 4)
})

// --- Navigation Methods ---
const canteraInput = ref(null)
const canteraResultsStyle = computed(() => {
    if (!canteraInput.value) return {}
    const rect = canteraInput.value.getBoundingClientRect()
    return {
        top: `${rect.bottom + 8}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
        maxHeight: '500px'
    }
})

const goBackToSource = () => {
    if (route.query.mode === 'satellite') {
        // [GY-FIX] Tratar de cerrar la ventana y avisar al padre si existe
        if (window.opener) {
            window.opener.postMessage({ type: 'SATELLITE_CLOSED' }, '*');
        }
        window.close()
        return
    }
    if (returnUrl.value) router.push(returnUrl.value)
    else router.push('/hawe')
}
const goToNew = () => {
    resetForm()
    isNew.value = true
    activeTab.value = 'CLIENTE'
    showContactoForm.value = false
    router.replace({ 
        name: 'HaweClientCanvas', 
        params: { id: 'new' },
        query: { ...route.query } 
    })
}

// --- Cantera Logic ---
const canteraResults = ref([])
const isSearching = ref(false)
const guardLoading = ref(false)
let searchTimeout = null

const handleSearchCantera = () => {
    if (!isNew.value) return
    const query = form.value.razon_social
    if (searchTimeout) clearTimeout(searchTimeout)
    if (!query || query.length < 3) {
        canteraResults.value = []
        return
    }
    isSearching.value = true
    searchTimeout = setTimeout(async () => {
        try {
            const res = await canteraService.searchClientes(query)
            canteraResults.value = res.data
        } catch (e) {
            console.error("Error searching cantera", e)
        } finally {
            isSearching.value = false
        }
    }, 300)
}

const importFromCantera = async (canteraClient) => {
    try {
        isSearching.value = true
        guardLoading.value = true
        const res = await canteraService.importCliente(canteraClient.id)
        if (res.data && res.data.status === 'success') {
            notificationStore.add(`Cliente importado desde Cantera exitosamente`, 'success')
            
            const imported = res.data.cliente
            if (imported) {
                form.value = { ...imported }
                domicilios.value = imported.domicilios || []
                contactos.value = imported.vinculos || []
                isNew.value = false
            }

            router.replace({ 
                name: 'HaweClientCanvas', 
                params: { id: res.data.imported_id },
                query: { ...route.query }
            })
        } else {
            throw new Error(res.data?.detail || 'Fallo en la respuesta del servidor')
        }
    } catch (e) {
        console.error("Error importing from cantera", e)
        const msg = e.response?.data?.detail || e.message || 'Error desconocido'
        notificationStore.add(`Fallo la importación: ${msg}. Podés completar los datos manualmente.`, 'error')
        
        // [GY-FIX] Si falla, al menos dejamos el nombre que el usuario quería
        if (!form.value.razon_social && canteraClient.razon_social) {
            form.value.razon_social = canteraClient.razon_social
        }
    } finally {
        isSearching.value = false
        guardLoading.value = false
        canteraResults.value = []
    }
}

// --- Initialization ---
onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    await maestrosStore.fetchAll()
    
    if (route.params.id === 'new') {
        isNew.value = true
        resetForm()
    } else {
        isNew.value = false
        await loadCliente(route.params.id)
    }
})

watch(() => route.params.id, async (newId) => {
    if (newId === 'new') {
        isNew.value = true; resetForm()
    } else if (newId) {
        isNew.value = false; await loadCliente(newId)
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

// --- Core Client Logic ---
const resetForm = () => {
    form.value = {
        id: null, razon_social: '', nombre_fantasia: '', cuit: '',
        condicion_iva_id: null, lista_precios_id: null, vendedor_id: null, segmento_id: null,
        limite_credito: 0, dias_vencimiento: 30, activo: true, observaciones: '',
        web_portal_pagos: '', datos_acceso_pagos: '', saldo: 0, fecha_ultima_compra: null,
        codigo_interno: ''
    }
    domicilios.value = []
    contactos.value = []
    historial.value = []
    productosHabituales.value = []
}

const loadCliente = async (id) => {
    try {
        const client = await store.fetchClienteById(id)
        if (client) {
            form.value = { ...client }
            domicilios.value = client.domicilios || []
            contactos.value = client.vinculos || [] 
            loadCommercialIntel()
        }
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al cargar cliente', 'error')
    }
}

const loadCommercialIntel = () => {
    // Mock Commercial Intelligence
    historial.value = [
        { id: 'ORD-9821', fecha: '2023-11-15', total: 45200.50, estado: 'Entregado' },
        { id: 'ORD-9815', fecha: '2023-11-10', total: 12500.00, estado: 'En Viaje' },
        { id: 'ORD-9788', fecha: '2023-10-28', total: 8900.20, estado: 'Entregado' }
    ]
    productosHabituales.value = [
        { id: 1, sku: 'AGUA-01', nombre: 'Agua Mineral 500ml Sin Gas' },
        { id: 2, sku: 'SODA-05', nombre: 'Sifón de Soda 1.5L x 6' },
        { id: 3, sku: 'PACK-MIX', nombre: 'Pack Degustación Varietal' }
    ]
}

const saveCliente = async () => {
    if (!form.value.razon_social) {
        notificationStore.add('La razón social es obligatoria', 'error')
        return
    }
    try {
        guardLoading.value = true
        console.log("Saving client...", { isNew: isNew.value, id: form.value.id })
        
        const payload = {
            ...form.value,
            domicilios: domicilios.value,
            vinculos: contactos.value
        }
        
        if (isNew.value) {
            const res = await store.createCliente(payload)
            console.log("Create client success:", res)
            notificationStore.add('Cliente creado exitosamente', 'success')
        } else {
            const res = await store.updateCliente(form.value.id, payload)
            console.log("Update client success:", res)
            notificationStore.add('Cliente actualizado exitosamente', 'success')
        }
        
        // Pequeño delay para que se vea la notificación antes de cerrar
        setTimeout(() => {
            goBackToSource()
        }, 500)
    } catch (e) {
        console.error("Save client error:", e)
        const errorMsg = e.response?.data?.detail || e.message || 'Error desconocido'
        notificationStore.add(`Error al guardar: ${errorMsg}`, 'error')
    } finally {
        guardLoading.value = false
    }
}

const cloneCliente = () => {
    form.value.id = null
    form.value.razon_social += ' (COPIA)'
    isNew.value = true
    notificationStore.add('Registro clonado. Revise y guarde.', 'info')
}

// --- Specific Logic & UI Handlers ---
const handleCuitInput = (e) => {
    form.value.cuit = e.target.value.replace(/[^0-9]/g, '')
}

const handleSegmentoChange = () => {
    if (form.value.segmento_id === '__NEW__') {
        form.value.segmento_id = null
        showSegmentoModal.value = true
    }
}

// Segmentos Modals
const showSegmentoModal = ref(false)
const showSegmentoList = ref(false)
const editingSegmentoId = ref(null)

const closeSegmentoModal = () => {
    showSegmentoModal.value = false
    editingSegmentoId.value = null
}
const handleSegmentoSaved = async () => {
    await maestrosStore.fetchSegmentos(null, true)
}

// Domicilios Logic
const selectedDomicilio = ref(null)
const openDomicilioTab = (domicilio = null) => {
    selectedDomicilio.value = domicilio
    activeTab.value = 'DOMICILIO'
}
const openFiscalEditor = () => {
    const fiscal = domicilios.value.find(d => d.es_fiscal)
    openDomicilioTab(fiscal)
}
const handleDomicilioSaved = async (domicilioData) => {
    try {
        if (isNew.value) {
            // Local saving for new clients
            if (domicilioData.local_id || domicilioData.id) {
                const idx = domicilios.value.findIndex(d => (d.local_id && d.local_id === domicilioData.local_id) || (d.id && d.id === domicilioData.id))
                if (idx !== -1) {
                    domicilios.value[idx] = { ...domicilioData }
                }
            } else {
                const newDom = { ...domicilioData, local_id: Date.now() }
                domicilios.value.push(newDom)
            }
            notificationStore.add('Domicilio añadido localmente', 'info')
        } else {
            // Persistent saving for existing clients
            if (domicilioData.id) {
                await store.updateDomicilio(form.value.id, domicilioData.id, domicilioData)
            } else {
                await store.createDomicilio(form.value.id, domicilioData)
            }
            await loadCliente(form.value.id)
            notificationStore.add('Domicilio guardado en servidor', 'success')
        }
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al gestionar domicilio', 'error')
    }
    activeTab.value = 'CLIENTE'
}

// Contactos Logic
const showContactoForm = ref(false)
const selectedContacto = ref(null)

const addContacto = () => {
    if (isNew.value) return notificationStore.add('Guarde el cliente primero', 'warning')
    selectedContacto.value = null; showContactoForm.value = true
}
const editContacto = (c) => {
    selectedContacto.value = c; showContactoForm.value = true
}
const handleContactoSaved = () => loadCliente(form.value.id)

const handleKeydown = (e) => {
    // Si el evento ya fue manejado (ej: por un modal), no hacemos nada
    if (e.defaultPrevented) return

    // IMPORTANTE: Si hay un sub-formulario abierto (Domicilio, Contacto), 
    // ignoramos el evento para que no se dispare el guardado/cierre del cliente principal.
    if (activeTab.value !== 'CLIENTE' || showContactoForm.value) {
        console.log("Global hotkey ignored: sub-form active", { activeTab: activeTab.value, showContactoForm: showContactoForm.value })
        return
    }

    if (e.key === 'Escape') {
        e.preventDefault()
        goBackToSource()
    }
    if (e.key === 'F10') { 
        e.preventDefault()
        saveCliente() 
    }
}

const scrollToNotes = () => {
    const el = document.querySelector('textarea')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const goToPedido = (orderId) => {
    // Assuming orderId might come with # or prefix, sanitize if needed
    const numericId = orderId.replace(/[^0-9]/g, '')
    router.push({ name: 'PedidoCanvas', params: { id: numericId } })
}

const statusColor = (status) => {
    if (status === 'Entregado') return 'bg-green-900/20 text-green-400 border-green-500/30'
    if (status === 'En Viaje') return 'bg-blue-900/20 text-blue-400 border-blue-500/30'
    return 'bg-gray-900/20 text-gray-400 border-gray-500/30'
}
</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(6, 182, 212, 0.2);
  border-radius: 10px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(6, 182, 212, 0.4);
}
.tokyo-bg {
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 40%);
}
.neon-cyan {
    box-shadow: inset 0 0 100px rgba(6, 182, 212, 0.03);
}
</style>
