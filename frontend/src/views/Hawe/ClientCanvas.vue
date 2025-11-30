<template>
  <div class="flex h-full w-full bg-[var(--hawe-bg-panel)] text-white overflow-hidden font-sans">
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

            <button @click="goToList" class="flex items-center gap-2 text-white hover:text-cyan-400 transition-colors group" title="Ir al Listado de Clientes">
                <i class="fas fa-list text-cyan-400"></i>
                <span class="font-outfit text-sm font-bold uppercase tracking-wider text-cyan-400">Fichas</span>
            </button>
        </div>
        
        <button v-if="!isNew" @click="goToNew" class="flex items-center gap-2 text-white/50 hover:text-white px-3 py-1.5 rounded-md hover:bg-white/5 transition-all group border border-transparent hover:border-white/10">
            <i class="fas fa-plus text-xs"></i>
            <span class="font-outfit text-xs font-bold uppercase tracking-wider">Nuevo Cliente</span>
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
                <label 
                    class="block text-[10px] font-bold uppercase text-white/40 mb-1 cursor-pointer hover:text-white/80"
                    @contextmenu.prevent="handleSegmentoContextMenu($event)"
                >
                    Segmento
                </label>
                <div class="w-full">
                    <select 
                        v-model="form.segmento_id" 
                        @change="handleSegmentoChange"
                        class="w-full bg-transparent text-sm text-white focus:outline-none appearance-none [&>option]:bg-slate-900 border-b border-white/10 focus:border-cyan-400 pb-1"
                    >
                        <option :value="null">Sin Segmento</option>
                        <option value="__NEW__" class="text-green-400 font-bold">+ Crear Nuevo Segmento</option>
                        <option disabled>----------------</option>
                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                    </select>
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
        
        <!-- TAB: CLIENTE (Main View) -->
        <template v-if="activeTab === 'CLIENTE'">
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
                        <p class="text-lg font-mono text-white font-bold">$ {{ form.saldo ? Number(form.saldo).toFixed(2) : '0.00' }}</p>
                    </div>
                    <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[120px]">
                        <p class="text-[10px] uppercase text-white/40 font-bold">Última Compra</p>
                        <p class="text-lg text-white/70">{{ form.fecha_ultima_compra ? new Date(form.fecha_ultima_compra).toLocaleDateString() : '--/--/--' }}</p>
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
                                    <label 
                                        class="block text-xs font-bold uppercase text-white/40 mb-1 cursor-pointer hover:text-white/80"
                                        @contextmenu.prevent="handleSegmentoContextMenu($event)"
                                    >
                                        Segmento
                                    </label>
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
            <footer class="h-16 bg-[#081824] border-t border-white/10 px-6 flex items-center justify-end shrink-0 z-30">
                <div class="flex items-center gap-3">
                    <span class="text-xs text-white/30 mr-4 font-mono hidden sm:inline-block">
                        <span class="mr-3">ESC = Volver</span>
                        <span>F10 = Guardar</span>
                    </span>
                    
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
                        class="px-6 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-sm font-bold shadow-lg shadow-emerald-900/50 transition-all transform active:scale-95 flex items-center gap-2"
                    >
                        Guardar Cambios <span class="font-mono opacity-80">F10</span>
                    </button>
                </div>
            </footer>
        </template>

        <!-- TAB: DOMICILIO -->
        <DomicilioForm 
            v-if="activeTab === 'DOMICILIO'"
            :show="true" 
            :domicilio="selectedDomicilio"
            :defaultTransportId="form.domicilios?.find(d => d.es_fiscal)?.transporte_id"
            @close="activeTab = 'CLIENTE'" 
            @saved="handleDomicilioSaved"
        />

    </main>

    <!-- ZONE 2: REFERENCE (Right Panel) -->
    <aside class="w-80 flex flex-col border-l border-white/10 bg-black/20 backdrop-blur-md z-20">
        <!-- Header -->
        <div class="h-14 flex items-center justify-center px-6 border-b border-white/10 shrink-0 relative">
            <h2 class="font-outfit text-sm font-bold uppercase tracking-wider text-white/70">Logística & Contactos</h2>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
            <!-- Domicilios -->
            <section>
                <div class="flex items-center justify-between mb-3 group">
                    <h3 
                        @contextmenu.prevent="handleDomicilioContextMenu($event)"
                        class="text-xs font-bold text-white/50 uppercase cursor-context-menu hover:text-white/80 transition-colors"
                    >
                        Domicilios
                    </h3>
                    <div class="flex gap-2">
                        <button @click="openDomicilioTab()" class="text-[10px] uppercase font-bold text-cyan-400 hover:text-cyan-300">FICHA - NUEVO</button>
                    </div>
                </div>
                <div class="space-y-2">
                    <div 
                        v-for="dom in domicilios" 
                        :key="dom.id" 
                        @click="selectDomicilio(dom)"
                        @dblclick="openDomicilioTab(dom)"
                        @contextmenu.prevent="handleDomicilioContextMenu($event, dom)"
                        :class="[
                            'bg-white/5 border rounded-lg p-3 transition-all cursor-pointer group relative',
                            selectedDomicilioId === dom.id ? 'border-cyan-500/50 bg-cyan-500/5 ring-1 ring-cyan-500/20' : 'border-white/10 hover:border-white/20'
                        ]"
                    >
                        <div class="flex justify-between items-start mb-1">
                            <span v-if="dom.es_fiscal" class="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 rounded border border-purple-500/30">FISCAL</span>
                            <span v-else class="text-[10px] bg-gray-700 text-gray-300 px-1.5 rounded">SUCURSAL</span>
                            <button @click.stop="openDomicilioTab(dom)" class="text-[10px] text-white/30 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"><i class="fas fa-pencil-alt"></i></button>
                        </div>
                        <p class="text-sm font-medium text-white leading-tight">{{ dom.calle }} {{ dom.numero }}</p>
                        <p class="text-xs text-white/50">{{ dom.localidad }}</p>
                        <div class="mt-2 flex items-center gap-2 text-xs text-white/40">
                            <i class="fas fa-truck"></i> {{ dom.transporte?.nombre || dom.transporte_nombre || 'Sin Transporte' }}
                        </div>
                    </div>
                    
                    <!-- Add Button -->
                    <button 
                        @click="openDomicilioTab()"
                        class="w-full py-2 border border-dashed border-white/10 rounded-lg text-white/30 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all flex items-center justify-center gap-2 text-xs font-bold uppercase"
                    >
                        <i class="fas fa-plus"></i> Agregar Domicilio
                    </button>
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
                        <div class="flex items-center gap-3">
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
    <!-- Modals & Context Menu -->
    <SegmentoForm 
        :show="showSegmentoModal" 
        :id="editingSegmentoId" 
        @close="closeSegmentoModal" 
        @saved="handleSegmentoSaved"
    />

    <SegmentoList 
        v-if="showSegmentoList"
        :isStacked="true"
        class="fixed inset-0 z-[60] bg-white m-4 rounded-lg shadow-2xl overflow-hidden"
        @close="showSegmentoList = false"
    />

    <ContextMenu 
        v-model="contextMenu.show" 
        :x="contextMenu.x" 
        :y="contextMenu.y" 
        :actions="contextMenu.actions"
        @close="contextMenu.show = false"
    />
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, computed, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClientesStore } from '../../stores/clientes'
import { useMaestrosStore } from '../../stores/maestros'
import { useNotificationStore } from '../../stores/notification'
import ContextMenu from '../../components/common/ContextMenu.vue'
import SegmentoForm from '../Maestros/SegmentoForm.vue'
import SegmentoList from '../Maestros/SegmentoList.vue'
import DomicilioForm from './components/DomicilioForm.vue'

const route = useRoute()
const router = useRouter()
const store = useClientesStore()
const maestrosStore = useMaestrosStore()
const notificationStore = useNotificationStore()

const goToList = () => router.push('/hawe')
const goToNew = () => router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })

// State
const isNew = ref(false)
const activeTab = ref('CLIENTE') // 'CLIENTE', 'DOMICILIO', 'CONTACTO'

const form = ref({
    id: null,
    razon_social: '',
    cuit: '',
    condicion_iva: 'Responsable Inscripto',
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

const showAddSegmento = ref(false)
const newSegmentoName = ref('')

// Segmento ABM Logic
const showSegmentoModal = ref(false)
const showSegmentoList = ref(false)
const editingSegmentoId = ref(null)

// Domicilios State
const selectedDomicilio = ref(null)
const selectedDomicilioId = ref(null)

const contextMenu = reactive({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

// Computed properties for selects
const listasPrecios = computed(() => maestrosStore.listasPrecios)
const vendedores = computed(() => maestrosStore.vendedores)
const segmentos = computed(() => maestrosStore.segmentos)

// Keyboard Shortcuts
const handleKeydown = (e) => {
    if (e.key === 'Escape') {
        if (activeTab.value !== 'CLIENTE') {
            activeTab.value = 'CLIENTE'
            return
        }
        router.push('/hawe')
    }
    if (e.key === 'F10') {
        e.preventDefault()
        if (activeTab.value === 'DOMICILIO') {
            // DomicilioForm handles its own save via F10, but we need to ensure propagation if needed
            // Actually, DomicilioForm captures F10 locally if focused, but global listener might catch it first
            // We'll let the component handle it or trigger a save event
            return 
        }
        saveCliente()
    }
    
    // Navigation
    if (!isNew.value && activeTab.value === 'CLIENTE') {
        // Domicilio Navigation (Up/Down)
        if (domicilios.value.length > 0 && selectedDomicilioId.value) {
            const currentIndex = domicilios.value.findIndex(d => d.id === selectedDomicilioId.value)
            
            if (e.key === 'ArrowUp') {
                e.preventDefault()
                const newIndex = currentIndex > 0 ? currentIndex - 1 : domicilios.value.length - 1
                selectDomicilio(domicilios.value[newIndex])
                return
            }
            if (e.key === 'ArrowDown') {
                e.preventDefault()
                const newIndex = currentIndex < domicilios.value.length - 1 ? currentIndex + 1 : 0
                selectDomicilio(domicilios.value[newIndex])
                return
            }
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                openDomicilioTab(domicilios.value[currentIndex])
                return
            }
        }

        // Client Navigation (Left/Right)
        if (store.clientes.length > 0) {
            if (e.key === 'ArrowLeft') {
                navigateClient(-1)
            }
            if (e.key === 'ArrowRight') {
                navigateClient(1)
            }
            if (e.key === 'Home') {
                e.preventDefault()
                navigateToIndex(0)
            }
            if (e.key === 'End') {
                e.preventDefault()
                navigateToIndex(store.clientes.length - 1)
            }
            if (e.key === 'PageUp') {
                e.preventDefault()
                navigateClient(-10) // Jump 10 back
            }
            if (e.key === 'PageDown') {
                e.preventDefault()
                navigateClient(10) // Jump 10 forward
            }
        }
    }
}

const navigateToIndex = (index) => {
    if (index >= 0 && index < store.clientes.length) {
        const nextClient = store.clientes[index]
        router.push({ name: 'HaweClientCanvas', params: { id: nextClient.id } })
    }
}

const navigateClient = (direction) => {
    // Use loose equality to handle string/number ID mismatch
    const currentIndex = store.clientes.findIndex(c => c.id == form.value.id)
    if (currentIndex === -1) return

    let newIndex = currentIndex + direction
    
    // Looping Logic for single steps
    if (Math.abs(direction) === 1) {
        if (newIndex < 0) newIndex = store.clientes.length - 1
        if (newIndex >= store.clientes.length) newIndex = 0
    } else {
        // Clamping logic for page jumps
        if (newIndex < 0) newIndex = 0
        if (newIndex >= store.clientes.length) newIndex = store.clientes.length - 1
    }

    navigateToIndex(newIndex)
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    
    // Fetch auxiliary data
    await maestrosStore.fetchAll()

    // Ensure we have the list for navigation
    if (store.clientes.length === 0) {
        await store.fetchClientes()
    }

    if (route.params.id === 'new') {
        isNew.value = true
        resetForm()
    } else {
        isNew.value = false
        await loadCliente(route.params.id)
    }
})

// Watch for route changes to reload data without remounting
watch(() => route.params.id, async (newId) => {
    if (newId === 'new') {
        isNew.value = true
        resetForm()
    } else if (newId) {
        isNew.value = false
        await loadCliente(newId)
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

const resetForm = () => {
    form.value = {
        id: null,
        razon_social: '',
        cuit: '',
        condicion_iva: 'Responsable Inscripto',
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
    }
    domicilios.value = []
    contactos.value = []
}

const loadCliente = async (id) => {
    try {
        const client = await store.fetchClienteById(id)
        if (client) {
            form.value = { ...client }
            // Ensure arrays exist
            domicilios.value = client.domicilios || []
            contactos.value = client.vinculos || [] // Store uses 'vinculos', mapping to 'contactos' for view compatibility
        }
    } catch (e) {
        notificationStore.add('Error al cargar cliente', 'error')
        console.error(e)
    }
}

const saveCliente = async () => {
    try {
        // Prepare payload with nested data
        const payload = {
            ...form.value,
            domicilios: domicilios.value,
            vinculos: contactos.value
        }

        if (isNew.value) {
            await store.createCliente(payload)
            notificationStore.add('Cliente creado exitosamente', 'success')
        } else {
            await store.updateCliente(form.value.id, payload)
            notificationStore.add('Cliente actualizado exitosamente', 'success')
        }
        router.push('/hawe')
    } catch (e) {
        notificationStore.add('Error al guardar cliente', 'error')
        console.error(e)
    }
}

const deleteCliente = async () => {
    if(!confirm('¿Está seguro de dar de baja este cliente?')) return
    try {
        // await store.deleteCliente(form.value.id)
        notificationStore.add('Cliente dado de baja', 'success')
        router.push('/hawe')
    } catch (e) {
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const cloneCliente = () => {
    // Clone logic: reset ID, keep data, set isNew
    form.value.id = null
    form.value.razon_social += ' (Copia)'
    form.value.codigo_interno = ''
    isNew.value = true
    router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
    notificationStore.add('Cliente clonado. Edite y guarde.', 'info')
}

// Placeholder functions for other actions
const addContacto = () => console.log('Add Contacto')
const editContacto = (c) => console.log('Edit Contacto', c)

const createSegmento = async () => {
    if (!newSegmentoName.value) return
    try {
        if (maestrosStore.createSegmento) {
             const newSeg = await maestrosStore.createSegmento({ nombre: newSegmentoName.value })
             form.value.segmento_id = newSeg.id
             notificationStore.add('Segmento creado', 'success')
        } else {
             notificationStore.add('Función crear segmento no implementada en store', 'warning')
        }

        showAddSegmento.value = false
        newSegmentoName.value = ''
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al crear segmento', 'error')
    }
}

const handleSegmentoChange = () => {
    if (form.value.segmento_id === '__NEW__') {
        form.value.segmento_id = null
        showAddSegmento.value = true
    }
}

const handleCuitInput = (e) => {
    // Basic CUIT formatting or validation could go here
    // For now, just ensuring numeric input if needed, or leaving as is
    form.value.cuit = e.target.value.replace(/[^0-9]/g, '')
}

// Context Menu Logic
const openSegmentoModal = (segmento = null) => {
    editingSegmentoId.value = segmento ? segmento.id : null
    showSegmentoModal.value = true
}

const closeSegmentoModal = () => {
    showSegmentoModal.value = false
    editingSegmentoId.value = null
}

const handleSegmentoSaved = async () => {
    await maestrosStore.fetchSegmentos(null, true) // Force refresh
}

const handleSegmentoContextMenu = (e) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    contextMenu.actions = [
        {
            label: 'Nuevo Segmento',
            icon: '➕',
            handler: () => openSegmentoModal()
        },
        {
            label: 'Administrar Segmentos',
            icon: '📋',
            handler: () => { showSegmentoList.value = true }
        }
    ]
}

// --- Domicilios Logic ---
const openDomicilioTab = (domicilio = null) => {
    selectedDomicilio.value = domicilio
    activeTab.value = 'DOMICILIO'
}

const handleDomicilioSaved = (domicilioData) => {
    if (domicilioData.id) {
        // Update existing
        const index = domicilios.value.findIndex(d => d.id === domicilioData.id)
        if (index !== -1) {
            domicilios.value[index] = { ...domicilios.value[index], ...domicilioData }
        }
    } else {
        // Add new
        domicilios.value.push({
            ...domicilioData,
            id: Date.now(), // Temp ID
            es_fiscal: domicilios.value.length === 0 // First one is fiscal default
        })
    }
    activeTab.value = 'CLIENTE'
}

const selectDomicilio = (dom) => {
    selectedDomicilioId.value = dom.id
}

const handleDomicilioContextMenu = (e, dom = null) => {
    contextMenu.show = true
    contextMenu.x = e.clientX
    contextMenu.y = e.clientY
    
    if (dom) {
        contextMenu.actions = [
            {
                label: 'Editar Domicilio',
                icon: '✏️',
                handler: () => openDomicilioTab(dom)
            },
            {
                label: 'Eliminar',
                icon: '🗑️',
                handler: () => {
                    domicilios.value = domicilios.value.filter(d => d.id !== dom.id)
                }
            }
        ]
    } else {
        // Header context menu
        contextMenu.actions = [
            {
                label: 'Nuevo Domicilio',
                icon: '➕',
                handler: () => openDomicilioTab()
            },
            {
                label: 'Administrar Domicilios',
                icon: '📋',
                handler: () => alert('Administrar Domicilios')
            }
        ]
    }
}
</script>
