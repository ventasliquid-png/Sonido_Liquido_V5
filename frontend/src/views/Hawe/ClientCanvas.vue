<template>
  <div class="flex flex-col h-full w-full bg-[#0f172a] rounded-2xl border-2 border-cyan-500 shadow-[0_0_30px_rgba(6,182,212,0.4)] overflow-hidden relative tokyo-bg neon-cyan">
      
      <!-- HEADER (Cyan Style - STICKY) -->
      <div class="w-full bg-cyan-950/30 border-b border-cyan-500/20 p-4 flex justify-between items-center backdrop-blur-md shrink-0 z-50">
          <div class="flex items-center gap-4">
              <button @click="goBackToSource" class="text-white/50 hover:text-cyan-400 transition-colors">
                  <i class="fas fa-arrow-left"></i>
              </button>
              <div class="relative group">
                  <span class="absolute -top-3 left-1 text-[9px] font-bold text-cyan-900/50 uppercase tracking-widest transition-colors group-hover:text-cyan-500/50">Razón Social</span>
                  <input 
                      v-model="form.razon_social" 
                      type="text" 
                      class="bg-black/40 border border-white/20 rounded-md px-3 py-1.5 text-xl font-bold text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all placeholder-white/20 w-[300px] lg:w-[450px]"
                      placeholder="Ingrese Razón Social..."
                  />
              </div>

              <!-- AGENDA BADGE (V14) -->
              <div class="relative">
                  <button 
                      @click="showAgenda = !showAgenda"
                      class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all group/agenda"
                      :class="showAgenda ? 'bg-cyan-600 border-cyan-400 text-white shadow-[0_0_15px_rgba(8,145,178,0.5)]' : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10 hover:text-white'"
                  >
                      <i class="fas fa-address-book" :class="showAgenda ? 'animate-pulse' : ''"></i>
                      <span class="text-[10px] font-bold uppercase tracking-widest hidden lg:inline">Agenda</span>
                      <span v-if="contactos.length > 0" class="ml-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold" :class="showAgenda ? 'bg-white/20' : 'bg-cyan-500/20 text-cyan-400'">
                          {{ contactos.length }}
                      </span>
                  </button>
                  
                  <!-- Popover Backdrop (Click Outside) -->
                  <div v-if="showAgenda" class="fixed inset-0 z-[55]" @click="showAgenda = false"></div>

                  <!-- Popover Component -->
                  <ContactoPopover 
                      v-if="showAgenda" 
                      :contactos="contactos" 
                      @manager="scrollToContacts"
                  />
              </div>
          </div>
          
          <!-- CENTER TITLE -->
          <div class="flex-1 flex justify-center items-center pointer-events-none">
              <h1 class="text-2xl font-black text-cyan-500 uppercase tracking-[0.2em] transform skew-x-[-10deg] select-none shadow-cyan-500/50 drop-shadow-[0_0_10px_rgba(6,182,212,0.5)]">
                  {{ isNew ? 'Formulario de Alta' : 'Ficha de Cliente' }}
              </h1>
          </div>
          
          <div class="flex items-center gap-4">
              <span v-if="form.codigo_interno" class="font-mono text-xs text-cyan-500/50 mr-4">#{{ form.codigo_interno }}</span>
              <!-- Status Switch (Header) -->
              <div class="flex items-center justify-between bg-black/40 rounded-lg px-2 py-1 border border-white/10 h-[26px]">
                   <span class="text-[8px] font-bold uppercase truncate mr-2" :class="form.activo ? 'text-green-400' : 'text-red-400'">
                       {{ form.activo ? 'OPERATIVO' : 'INACTIVO' }}
                   </span>
                   <button @click="form.activo = !form.activo" class="relative inline-flex h-3 w-6 items-center rounded-full transition-colors focus:outline-none bg-white/10 shrink-0" :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'">
                       <span class="inline-block h-2 w-2 transform rounded-full bg-white transition-transform" :class="form.activo ? 'translate-x-3' : 'translate-x-0.5'" />
                   </button>
               </div>
              <div class="h-6 w-px bg-white/10 mx-2"></div>
              <button v-if="!isNew" @click="goToNew" class="text-xs font-bold text-white/40 hover:text-white uppercase tracking-tighter">
                  <i class="fas fa-plus mr-1"></i> Nuevo
              </button>
          </div>
      </div>

      <!-- MAIN SCROLLABLE CONTENT -->
      <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-500/20 p-4 space-y-4">
          
          <!-- BLOCK 1: IDENTITY & MASTER DATA (LOGICAL REORDER V5.3) -->
          <section class="bg-black/40 border border-white/10 rounded-2xl p-4 backdrop-blur-md shadow-xl relative group">
              <div class="absolute top-0 left-0 w-1 h-full bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.8)]"></div>
              
              <div class="space-y-4">
                  <!-- LINE 1: ADDRESSES & LOGISTICS (Fiscal & Entrega side-by-side) -->
                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 items-start">
                      
                      <!-- Domicilio Fiscal -->
                      <div 
                        @click="openFiscalEditor"
                        class="bg-cyan-900/10 border border-cyan-500/20 rounded-xl p-3 relative group cursor-pointer hover:bg-cyan-900/20 hover:border-cyan-500/50 transition-all"
                      >
                          <div class="flex justify-between items-center mb-2 border-b border-cyan-500/10 pb-1">
                              <label class="text-[10px] font-bold text-cyan-400 uppercase tracking-widest"><i class="fas fa-file-invoice mr-1"></i> Domicilio Fiscal <span class="text-red-400">*</span></label>
                              <div class="text-[9px] text-cyan-500/50 group-hover:text-cyan-400 transition-colors">
                                  <i class="fas fa-pencil-alt mr-1"></i> Editar
                              </div>
                          </div>
                          <div>
                              <p class="text-sm font-bold text-white tracking-wide truncate">{{ computedFiscalAddress.split(',')[0] }}</p>
                              <p class="text-[10px] text-cyan-200/50 font-mono">{{ computedFiscalAddress.split(',').slice(1).join(', ') || 'Sin Localidad' }}</p>
                          </div>
                      </div>

                      <!-- Domicilio Entrega & Transporte -->
                      <div class="bg-emerald-900/10 border border-emerald-500/20 rounded-xl p-3 relative group">
                          <div class="flex justify-between items-center mb-2 border-b border-emerald-500/10 pb-1">
                              <label class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest"><i class="fas fa-truck mr-1"></i> Entrega Principal</label>
                              <div class="flex items-center gap-2">
                                  <label class="text-[9px] font-bold text-white/30 uppercase">Fantasía:</label>
                                  <input v-model="form.nombre_fantasia" type="text" class="bg-black/20 border border-white/10 rounded px-1.5 py-0.5 text-[10px] text-white focus:outline-none w-32" placeholder="Nombre Fantasía..." />
                              </div>
                          </div>
                          
                          <div class="grid grid-cols-2 gap-3">
                              <!-- Address Preview -->
                              <div @click="openDomicilioTab(domiciliosLogistica.length > 0 ? domiciliosLogistica[0] : null)" class="cursor-pointer hover:opacity-80 transition-opacity">
                                   <!-- Logic to show Primary Delivery Address -->
                                    <template v-if="domiciliosLogistica.length > 0">
                                        <p class="text-xs font-bold text-white truncate">{{ domiciliosLogistica[0].calle }} {{ domiciliosLogistica[0].numero }}</p>
                                        <p class="text-[9px] text-emerald-200/50 uppercase">{{ domiciliosLogistica[0].localidad }}</p>
                                    </template>
                                    <template v-else>
                                        <p class="text-[10px] text-white/30 italic">Igual a Fiscal</p>
                                    </template>
                              </div>

                              <!-- Transport Selector -->
                              <div @contextmenu.prevent="openTransportContextMenu">
                                  <SmartSelect
                                    v-model="quickTransportId"
                                    :options="transportes"
                                    placeholder="Transporte..."
                                    :allowCreate="false"
                                    class="dark-smart-select"
                                />
                              </div>
                          </div>
                      </div>

                  </div>

                  <!-- LINE 2: FISCAL & COMMERCIAL (CUIT / IVA / Lista / Segmento) -->
                  <div class="grid grid-cols-12 gap-3 items-end border-t border-white/5 pt-3">
                       <!-- CUIT -->
                      <div class="col-span-12 lg:col-span-3">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-0.5">CUIT <span class="text-red-400">*</span></label>
                          <input v-model="form.cuit" @input="handleCuitInput" type="text" class="w-full bg-white/5 border rounded px-2 py-1 text-xs font-mono text-white focus:outline-none" :class="errors.cuit ? 'border-red-500' : 'border-white/5'" maxlength="13" />
                      </div>

                      <!-- Condición IVA -->
                      <div class="col-span-12 lg:col-span-3">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Condición IVA <span class="text-red-400">*</span></label>
                          <select v-model="form.condicion_iva_id" class="w-full bg-white/5 border rounded px-2 py-1 text-xs text-white focus:outline-none appearance-none [&>option]:bg-slate-900" :class="errors.condicion_iva_id ? 'border-red-500' : 'border-white/10'">
                              <option :value="null">IVA...</option>
                              <option v-for="iva in condicionesIva" :key="iva.id" :value="iva.id">{{ iva.nombre }}</option>
                          </select>
                      </div>

                      <!-- Lista de Precios -->
                      <div class="col-span-12 lg:col-span-3">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Lista de Precios <span class="text-red-400">*</span></label>
                          <select v-model="form.lista_precios_id" class="w-full bg-cyan-900/10 border rounded px-2 py-1 text-xs text-cyan-300 font-bold focus:outline-none appearance-none [&>option]:bg-slate-900" :class="errors.lista_precios_id ? 'border-red-500' : 'border-cyan-500/20'">
                              <option :value="null">Lista Automática</option>
                              <option v-for="lp in listasPrecios" :key="lp.id" :value="lp.id">{{ lp.nombre }}</option>
                          </select>
                      </div>

                       <!-- Segmento (Expanded) -->
                      <div class="col-span-12 lg:col-span-3">
                          <label class="text-[9px] font-bold text-white/30 uppercase tracking-widest block mb-1">Segmento <span class="text-red-400">*</span></label>
                          <select v-model="form.segmento_id" @change="handleSegmentoChange" class="w-full bg-white/5 border rounded px-2 py-1 text-xs text-white focus:outline-none appearance-none [&>option]:bg-slate-900" :class="errors.segmento_id ? 'border-red-500' : 'border-white/10'">
                               <option :value="null">Sin Segmento</option>
                               <option value="__NEW__" class="text-green-400 font-bold">+ Nuevo</option>
                               <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
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
          <section id="contacts-section" class="space-y-2">
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
      <footer v-if="activeTab === 'CLIENTE'" class="h-20 bg-cyan-950/20 border-t border-cyan-500/20 px-8 flex items-center justify-between shrink-0 backdrop-blur-md z-30">
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
                  class="px-10 py-3 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black uppercase tracking-[0.2em] shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all flex items-center gap-3 active:scale-95"
              >
                  Actualizar Registro <i class="fas fa-check"></i>
              </button>
          </div>
      </footer>

      <!-- Modals & Context Menus (Existing) -->
      <SegmentoForm v-if="showSegmentoModal" :show="showSegmentoModal" :id="editingSegmentoId" @close="closeSegmentoModal" @saved="handleSegmentoSaved" />
      <SegmentoList v-if="showSegmentoList" :isStacked="true" class="fixed inset-0 z-[100] bg-[#0f172a] m-10 rounded-2xl shadow-2xl border border-cyan-500/30" @close="showSegmentoList = false" />
      <DomicilioForm v-if="activeTab === 'DOMICILIO'" :show="true" :domicilio="selectedDomicilio" @close="activeTab = 'CLIENTE'" @saved="handleDomicilioSaved" />
      <ContactoForm v-if="showContactoForm" :show="showContactoForm" :clienteId="String(form.id)" :contacto="selectedContacto" @close="showContactoForm = false" @saved="handleContactoSaved" />
      
       <!-- Transport Context Menu Modal -->
       <Teleport to="body">
         <TransporteAbmModal
            v-if="showTransporteAbm"
            :show="showTransporteAbm"
            :transport-id="selectedTransporteId"
            @close="showTransporteAbm = false"
            @saved="handleTransporteAbmCreate"
        />
        <!-- Also Context Menu for Transport -->
         <ContextMenu 
            v-if="contextMenuState.show" 
            v-model="contextMenuState.show"
            :x="contextMenuState.x"
            :y="contextMenuState.y"
            :actions="contextMenuProps.actions"
            @close="contextMenuState.show = false"
        />
    </Teleport>
      
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
import ContactoPopover from './components/ContactoPopover.vue'
import SmartSelect from '../../components/ui/SmartSelect.vue'
import TransporteAbmModal from '../Logistica/components/TransporteAbmModal.vue'
import ContextMenu from '../../components/common/ContextMenu.vue'
import { useLogisticaStore } from '../../stores/logistica'
import { useAuditSemaphore } from '../../composables/useAuditSemaphore'

const route = useRoute()
const router = useRouter()
const store = useClientesStore()
const maestrosStore = useMaestrosStore()
const logisticaStore = useLogisticaStore()
const notificationStore = useNotificationStore()

// Audit Logic
const { evaluateCliente } = useAuditSemaphore()

const isNew = ref(false)
const expandLogistics = ref(false)
const showAgenda = ref(false)
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
const transportes = computed(() => logisticaStore.empresas)

// [GY-UX] Quick Transport Access (Linked to Main Address)
const quickTransportId = computed({
    get() {
        if (!domicilios.value || domicilios.value.length === 0) return null
        // 1. Try to find "Entrega" address
        const delivery = domicilios.value.find(d => d.es_entrega && d.activo !== false)
        if (delivery) return delivery.transporte_id
        // 2. Fallback to active "Fiscal" address
        const fiscal = domicilios.value.find(d => d.es_fiscal && d.activo !== false)
        if (fiscal) return fiscal.transporte_id
        // 3. Fallback to first
        return domicilios.value[0].transporte_id
    },
    set(val) {
        if (!domicilios.value) return
        // Update PRIORITY address (same priority logic as get)
        const target = domicilios.value.find(d => d.es_entrega && d.activo !== false) || 
                       domicilios.value.find(d => d.es_fiscal && d.activo !== false) ||
                       domicilios.value[0]
        
        if (target) {
            target.transporte_id = val
             // If existing client, we might want to save immediately?
             // But usually form is saved via F10.
             // However, for layout "Quick Access", user assumes instant or dirty state.
             // Since form.value is not touched, we must ensure these changes persist.
             // They are in 'domicilios' array ref.
        } else {
             notificationStore.add('No hay domicilio activo para asignar transporte', 'warning')
        }
    }
})

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
        if (fiscal) {
            let addr = `${fiscal.calle} ${fiscal.numero}`
            if (fiscal.piso) addr += ` ${fiscal.piso}`
            if (fiscal.depto) addr += ` ${fiscal.depto}`
            // Add comma before locality
            addr += `, ${fiscal.localidad}`
            return addr
        }
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
const goBackToSource = () => {
    if (route.query.mode === 'satellite') {
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
    showAgenda.value = false
    router.replace({ name: 'HaweClientCanvas', params: { id: 'new' } })
}

const scrollToContacts = () => {
    showAgenda.value = false
    // Force expand block if collapsed? It's always visible in V5.4 layout
    // Just scroll to it?
    const el = document.getElementById('contacts-section')
    if (el) el.scrollIntoView({ behavior: 'smooth' })
}

// --- Cantera Logic ---
const canteraResults = ref([])
const isSearching = ref(false)
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
        const res = await canteraService.importCliente(canteraClient.id)
        if (res.data.status === 'success') {
            notificationStore.add(`Cliente importado desde Cantera exitosamente`, 'success')
            router.replace({ name: 'HaweClientCanvas', params: { id: res.data.imported_id } })
        }
    } catch (e) {
        console.error("Error importing from cantera", e)
        notificationStore.add('Error al importar cliente desde Cantera', 'error')
    } finally {
        isSearching.value = false
        canteraResults.value = []
    }
}

// --- Transport ABM Context Menu ---
const showTransporteAbm = ref(false)
const selectedTransporteId = ref(null)

const contextMenuState = ref({ show: false, x: 0, y: 0 })
const contextMenuProps = ref({ actions: [] })

const openTransportContextMenu = (e) => {
    const currentId = quickTransportId.value
    const actions = [
        { 
            label: 'Nuevo Transporte (F4)', 
            iconClass: 'fas fa-plus', 
            handler: () => { 
                selectedTransporteId.value = null
                showTransporteAbm.value = true 
            } 
        }
    ]

    if (currentId) {
        actions.push({
            label: 'Editar Seleccionado',
            iconClass: 'fas fa-pencil-alt',
            handler: () => {
                selectedTransporteId.value = currentId
                showTransporteAbm.value = true
            }
        })
    }

    actions.push({ 
        label: 'Administrar Transportes', 
        iconClass: 'fas fa-truck', 
        handler: () => { 
             notificationStore.add('Para administrar, ir al menú Logística', 'info')
        } 
    })

    contextMenuState.value = {
        show: true,
        x: e.clientX,
        y: e.clientY
    }
    contextMenuProps.value.actions = actions
}

const handleTransporteAbmCreate = async (data) => {
    await logisticaStore.fetchEmpresas()
    if (data.id) quickTransportId.value = data.id
    notificationStore.add('Transporte creado y asignado', 'success')
    showTransporteAbm.value = false
}

// --- Initialization ---
onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    await maestrosStore.fetchAll()
    await logisticaStore.fetchEmpresas()
    
    if (route.params.id === 'new') {
        isNew.value = true
        if (store.draft) {
             form.value = { ...store.draft }
             domicilios.value = store.draft.domicilios || []
             contactos.value = store.draft.vinculos || []
             store.clearDraft() // Consume draft
             notificationStore.add('Datos clonados precargados', 'info')
        } else {
             resetForm()
        }
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

// Validation State
const errors = ref({});

const validateForm = () => {
    errors.value = {};
    let isValid = true;
    
    // [GY-UX] Flexible Validation (V14)
    // If deactivating, only Identity is required
    const isDeactivating = !form.value.activo;

    if (!form.value.razon_social) { errors.value.razon_social = true; isValid = false; }
    if (!form.value.cuit) { errors.value.cuit = true; isValid = false; }
    
    // Strict validations only if Active
    if (!isDeactivating) {
        if (!form.value.segmento_id) { errors.value.segmento_id = true; isValid = false; }
        if (!form.value.condicion_iva_id) { errors.value.condicion_iva_id = true; isValid = false; }
        if (!form.value.lista_precios_id) { errors.value.lista_precios_id = true; isValid = false; }
        
        // Validate Fiscal Domicile
        const hasFiscal = domicilios.value.some(d => d.es_fiscal && d.activo !== false);
        if (!hasFiscal) {
            errors.value.domicilio = true;
            isValid = false;
        }
    }
    
    return isValid;
};

const saveCliente = async () => {
    if (!validateForm()) {
        notificationStore.add('Complete los campos obligatorios indicados en rojo.', 'error');
        // Shake animation or sound could go here
        return;
    }

    try {
        const payload = {
            ...form.value,
            vinculos: contactos.value
        }
        
        // [GY-FIX] For updates, Domicilios are handled independently via sub-form.
        // We exclude them from the main payload to prevent 'updateCliente' from overwriting 
        // granular changes with stale data or partial objects.
        // For CREATE, we usually need them.
        if (isNew.value) {
            payload.domicilios = domicilios.value;
            await store.createCliente(payload)
            notificationStore.add('Cliente creado exitosamente', 'success')
        } else {
            // Explicitly do NOT send domicilios allow backend to keep current state
            delete payload.domicilios; 
            
            // [GY-FIX] Inject Quick Transport logic for backend shortcut
            if (quickTransportId.value) {
                payload.transporte_id = quickTransportId.value
            }

            await store.updateCliente(form.value.id, payload)
            notificationStore.add('Cliente actualizado exitosamente', 'success')
        }
        goBackToSource()
    } catch (e) {
        console.error(e)
        const msg = e.response?.data?.detail || 'Error al guardar cliente';
        notificationStore.add(msg, 'error')
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
        // Sanitize Payload (Strict Whitelist)
        const allowedFields = [
            'calle', 'numero', 'piso', 'depto', 'cp', 'localidad', 
            'provincia_id', 'transporte_id', 'es_fiscal', 'es_entrega', 'activo',
            'metodo_entrega', 'modalidad_envio', 'origen_logistico', 'observaciones',
            'id', 'cliente_id' 
        ];
        
        const payload = {};
        for (const key of allowedFields) {
            if (domicilioData[key] !== undefined) {
                payload[key] = domicilioData[key];
            }
        }

        if (isNew.value) {
            // Local saving for new clients
            if (domicilioData.local_id || domicilioData.id) {
                const idx = domicilios.value.findIndex(d => (d.local_id && d.local_id === domicilioData.local_id) || (d.id && d.id === domicilioData.id))
                if (idx !== -1) {
                    domicilios.value[idx] = { ...domicilioData } // Update Local
                }
            } else {
                const newDom = { ...domicilioData, local_id: Date.now() }
                domicilios.value.push(newDom)
            }
            notificationStore.add('Domicilio añadido localmente', 'info')
        } else {
            // Persistent saving for existing clients
            // 1. Optimistic Update (Immediate Feedback)
            // [GY-FIX] Loose equality for ID to handle String/Number mismatch
            const idx = domicilios.value.findIndex(d => String(d.id) === String(domicilioData.id));
            if (idx !== -1) {
                // Use splice to guarantee reactivity
                const updatedDom = { ...domicilios.value[idx], ...domicilioData };
                domicilios.value.splice(idx, 1, updatedDom);
            }
            
            // 2. Server Update (Wait for confirmation)
            let savedDom;
            console.log("Saving Domicilio Payload:", payload); // [GY-DEBUG]
            if (domicilioData.id) {
                // Return value from store is the Server Object
                savedDom = await store.updateDomicilio(form.value.id, domicilioData.id, payload)
            } else {
                savedDom = await store.createDomicilio(form.value.id, payload)
            }
            console.log("Server Saved Domicilio:", savedDom); // [GY-DEBUG]

            // 3. Authoritative Update (Replace Optimistic with Server Truth)
            // This ensures if server sanitized/rejected something (like Piso), UI reflects it immediately
            if (savedDom) {
                 const authIdx = domicilios.value.findIndex(d => String(d.id) === String(savedDom.id));
                 if (authIdx !== -1) {
                     domicilios.value.splice(authIdx, 1, savedDom);
                 } else {
                     domicilios.value.push(savedDom);
                 }
            }
            
            // Reload to ensuring consistency (Background)
            await loadCliente(form.value.id) // [GY-FIX] Re-enabled to ensure Fiscal Flag sync
            notificationStore.add('Domicilio guardado en servidor', 'success')
        }
    } catch (e) {
        console.error(e)
        // Revert? For now just error.
        notificationStore.add('Error al gestionar domicilio', 'error')
        // Force reload to restore true state
        await loadCliente(form.value.id)
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
    if (activeTab.value !== 'CLIENTE' || showContactoForm.value) return

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
