<template>
  <div class="flex flex-col h-full w-full backdrop-blur-xl transition-all hud-border-cyan rounded-xl" 
       :class="isCompact ? 'bg-[#0f172a]/90 border-l border-cyan-500' : 'bg-[#0f172a]'">
    <!-- Persistent Header -->
    <div class="flex flex-col border-b border-cyan-500/30 bg-black/20 shrink-0 transition-all gap-2"
         :class="isCompact ? 'p-3 py-2' : 'p-6'">
        <div class="flex justify-between items-start">
             <!-- Center Title Effect in Inspector -->
            <div class="flex-1 text-center">
                 <h2 class="text-lg font-black text-cyan-500 uppercase tracking-[0.2em] transform skew-x-[-10deg] drop-shadow-[0_0_8px_rgba(6,182,212,0.5)] leading-tight pl-1">
                    {{ isNew ? 'Formulario de Alta' : 'Edición Rápida' }}
                </h2>
            </div>
            
            <button v-if="modelValue || isNew" @click="$emit('close')" class="absolute right-3 top-3 text-cyan-900/50 hover:text-cyan-100 transition-colors">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <!-- Razón Social Input (Header) -->
        <!-- Razón Social Input + Agenda Badge -->
        <div class="flex items-center gap-2 relative">
            <input 
                v-model="form.razon_social" 
                autocomplete="off" 
                spellcheck="false" 
                class="bg-black/40 border rounded-md px-3 py-1.5 text-xl font-bold focus:outline-none transition-all placeholder-white/20 w-full" 
                :class="clientColorClass"
                placeholder="Ingrese Razón Social..." 
            />
            
            <!-- AGENDA BADGE (V14) -->
            <div class="relative shrink-0">
                <button 
                    @click="showAgenda = !showAgenda"
                    class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all h-[42px] group/agenda"
                    :class="showAgenda ? 'bg-cyan-600 border-cyan-400 text-white shadow-[0_0_15px_rgba(8,145,178,0.5)]' : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10 hover:text-white'"
                    title="Agenda Rápida"
                >
                    <i class="fas fa-address-book" :class="showAgenda ? 'animate-pulse' : ''"></i>
                    <span v-if="form.vinculos && form.vinculos.length > 0" class="px-1.5 py-0.5 rounded-full text-[9px] font-bold" :class="showAgenda ? 'bg-white/20' : 'bg-cyan-500/20 text-cyan-400'">
                        {{ form.vinculos.length }}
                    </span>
                </button>

                <!-- Popover Backdrop -->
                <div v-if="showAgenda" class="fixed inset-0 z-[55]" @click="showAgenda = false"></div>

                <!-- Popover Component -->
                <ContactoPopover 
                    v-if="showAgenda" 
                    :contactos="form.vinculos || []" 
                    @manager="switchToContactsTab"
                />
            </div>
        </div>
    </div>

    <!-- Inconsistency Banner -->
    <div v-if="hasInconsistency && !isNew" class="bg-red-500/10 border-b border-red-500/20 px-6 py-2 flex items-center justify-between group">
        <div class="flex items-center gap-2 overflow-hidden">
            <i class="fas fa-triangle-exclamation text-red-400 animate-pulse text-xs"></i>
            <span class="text-[10px] font-bold text-red-200/80 uppercase tracking-tighter truncate">
                Datos Inconsistentes: {{ formInconsistency.join(', ') }}
            </span>
        </div>
        <div class="text-[9px] text-red-400/50 font-medium italic opacity-0 group-hover:opacity-100 transition-opacity">
            Corregir para evitar errores fiscales
        </div>
    </div>

    <!-- Empty State -->
    <div v-if="!modelValue && !isNew" class="flex-1 flex flex-col items-center justify-center text-cyan-900/40 p-6 text-center">
        <i class="fas fa-user text-4xl mb-4"></i>
        <p>Seleccione un cliente para ver sus propiedades</p>
    </div>

    <!-- Form Content -->
    <div v-else class="flex-1 flex flex-col min-h-0">
        <!-- Tabs -->
        <div class="flex border-b border-cyan-900/20 shrink-0 bg-black/10">
            <button 
                @click="activeTab = 'general'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'general' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                General
            </button>
            <button 
                @click="activeTab = 'domicilios'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'domicilios' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                Domicilios
            </button>
            <button 
                @click="activeTab = 'contactos'"
                class="flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
                :class="activeTab === 'contactos' ? 'border-cyan-400 text-cyan-400 bg-cyan-900/10' : 'border-transparent text-cyan-200/40 hover:text-cyan-200 hover:bg-cyan-900/5'"
            >
                Contactos
            </button>
        </div>

        <!-- Scrollable Body -->
        <div class="flex-1 overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/50 scrollbar-track-transparent pb-20"
             :class="isCompact ? 'p-3' : 'p-6'">
            
            <!-- TAB: GENERAL -->
            <div v-if="activeTab === 'general'" class="space-y-4">
                
                <!-- SELECCIÓN POR PLANTILLA (F4 Flow) -->
                <div v-if="isNew" class="p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/20 mb-4">
                    <label class="text-[0.65rem] font-bold text-cyan-400 uppercase tracking-widest mb-2 block">
                        Cargar desde Plantilla / Cantera
                    </label>
                    <SmartSelect
                        v-model="templateId"
                        :options="clienteStore.clientes"
                        canteraType="clientes"
                        placeholder="Buscar cliente para clonar..."
                        :allowCreate="true"
                        @update:modelValue="handleTemplateSelect"
                        @select-cantera="handleTemplateSelect"
                        @create-new="handleManualTemplate"
                        class="dark-smart-select"
                    />
                    <p class="text-[9px] text-cyan-400/30 mt-2 italic">
                        Tip: Útil para cargar sedes de un mismo grupo rápidamente.
                    </p>
                </div>

                <!-- Row 1: Addresses (Fiscal & Delivery) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Domicilio Fiscal -->
                    <div class="bg-cyan-900/10 border border-cyan-900/30 rounded-lg p-3 relative group">
                         <div class="flex justify-between items-center mb-2 border-b border-cyan-900/20 pb-1">
                            <label class="text-[10px] font-bold text-cyan-400 uppercase tracking-widest"><i class="fas fa-file-invoice mr-1"></i> Domicilio Fiscal <span class="text-red-400">*</span></label>
                         </div>
                         <div class="space-y-2">
                            <div class="grid grid-cols-3 gap-2">
                                <div class="col-span-2">
                                    <input v-model="fiscalForm.calle" class="w-full bg-black/20 border border-cyan-900/30 rounded px-2 py-1 text-xs text-cyan-100 focus:border-cyan-500 outline-none placeholder-cyan-900/30" placeholder="Calle Fiscal" />
                                </div>
                                <div class="col-span-1">
                                    <input v-model="fiscalForm.numero" class="w-full bg-black/20 border border-cyan-900/30 rounded px-2 py-1 text-xs text-cyan-100 focus:border-cyan-500 outline-none placeholder-cyan-900/30" placeholder="Nro" />
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <input v-model="fiscalForm.localidad" class="w-full bg-black/20 border border-cyan-900/30 rounded px-2 py-1 text-xs text-cyan-100 focus:border-cyan-500 outline-none placeholder-cyan-900/30" placeholder="Localidad" />
                                <select v-model="fiscalForm.provincia_id" class="w-full bg-black/20 border border-cyan-900/30 rounded px-2 py-1 text-[10px] text-cyan-100 focus:border-cyan-500 outline-none appearance-none">
                                    <option :value="null">Provincia...</option>
                                    <option v-for="prov in provincias" :key="prov.id" :value="prov.id">{{ prov.nombre }}</option>
                                </select>
                            </div>
                         </div>
                    </div>

                    <!-- Domicilio Entrega (Simplified) -->
                    <div class="bg-emerald-900/10 border border-emerald-900/30 rounded-lg p-3 relative group">
                         <div class="flex justify-between items-center mb-2 border-b border-emerald-900/20 pb-1">
                            <label class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest"><i class="fas fa-truck mr-1"></i> Entrega / Logística</label>
                            <label class="flex items-center gap-1 cursor-pointer">
                                <input type="checkbox" v-model="useFiscalAsDelivery" class="accent-emerald-500 h-3 w-3" />
                                <span class="text-[9px] text-emerald-300/50 uppercase">Igual a Fiscal</span>
                            </label>
                         </div>
                         <div class="space-y-2" :class="{ 'opacity-50 pointer-events-none': useFiscalAsDelivery }">
                             <!-- Show Fields only if different, or grayed out -->
                            <div class="grid grid-cols-3 gap-2">
                                <div class="col-span-2">
                                    <input v-model="deliveryForm.calle" class="w-full bg-black/20 border border-emerald-900/30 rounded px-2 py-1 text-xs text-emerald-100 focus:border-emerald-500 outline-none placeholder-emerald-900/30" placeholder="Calle Entrega" />
                                </div>
                                <div class="col-span-1">
                                    <input v-model="deliveryForm.numero" class="w-full bg-black/20 border border-emerald-900/30 rounded px-2 py-1 text-xs text-emerald-100 focus:border-emerald-500 outline-none placeholder-emerald-900/30" placeholder="Nro" />
                                </div>
                            </div>
                            <!-- Transporte linked here -->
                            <!-- Transporte linked here -->
                            <div class="pointer-events-auto flex gap-2 items-center" @contextmenu.prevent="openTransportContextMenu">
                                <SmartSelect
                                    v-model="quickTransportId"
                                    :options="transportes"
                                    placeholder="Transporte Habitual..."
                                    :allowCreate="false"
                                    class="dark-smart-select flex-1"
                                />
                                <button 
                                    type="button"
                                    @click.stop="toggleRetira"
                                    class="px-2 py-1.5 rounded border text-[9px] font-black uppercase transition-all shadow-sm"
                                    :class="quickTransportId === null ? 'bg-orange-500/20 border-orange-500 text-orange-300 shadow-[0_0_10px_rgba(249,115,22,0.2)]' : 'bg-white/5 border-white/10 text-white/30 hover:bg-white/10 hover:text-white'"
                                    title="Alternar Retiro por Cliente"
                                >
                                    <i class="fas fa-walking mr-1"></i> Retira
                                </button>
                            </div>
                         </div>
                    </div>
                </div>

                <!-- Row 2: Tax & Classification -->
                <div class="grid grid-cols-12 gap-3 items-end pt-2">
                    <!-- CUIT (15 chars approx) -->
                    <div class="col-span-2">
                         <label class="block text-[10px] font-bold uppercase text-cyan-900/50 mb-1">
                            CUIT <span class="text-red-400">*</span>
                            <span v-if="form.estado_arca === 'VALIDADO'" class="ml-1 text-[9px] bg-emerald-500/20 text-emerald-400 px-1 rounded border border-emerald-500/30 animate-pulse">
                                <i class="fas fa-shield-alt"></i> ARCA
                            </span>
                         </label>
                             <div class="flex gap-1">
                                 <input 
                                    ref="cuitInput"
                                    v-model="form.cuit" 
                                    autocomplete="off" 
                                    spellcheck="false" 
                                    @input="formatCuitInput" 
                                    @blur="checkCuitBackend" 
                                    class="flex-1 bg-[#020a0f] border rounded p-2 text-xs transition-all font-mono placeholder-cyan-900/30 outline-none shadow-[0_0_10px_rgba(250,204,21,0.05)] focus:shadow-[0_0_15px_rgba(250,204,21,0.2)]" 
                                    :class="(form.flags_estado & 4) ? 'border-emerald-500/50 text-emerald-100' : 'border-yellow-400 text-yellow-300 focus:border-yellow-400 ring-1 ring-yellow-400/20 focus:ring-yellow-400/40'"
                                    placeholder="00-00000000-0" 
                                    maxlength="13" 
                                 />
                                 <button 
                                    @click="consultarAfip" 
                                    class="px-2 rounded border transition-all flex items-center justify-center shrink-0"
                                    :class="loadingAfip ? 'bg-cyan-900/50 border-cyan-800' : 'bg-cyan-900/20 border-cyan-500/30 hover:bg-cyan-500/20 hover:text-cyan-200 text-cyan-800'"
                                    :disabled="loadingAfip"
                                    title="Consultar en ARCA (RAR)"
                                >
                                    <i class="fas" :class="loadingAfip ? 'fa-spinner fa-spin' : 'fa-satellite-dish'"></i>
                                 </button>
                                 <button 
                                    v-if="!(form.flags_estado & 4)"
                                    @click="aplicarRosaManual" 
                                    class="px-2 rounded border transition-all flex items-center justify-center shrink-0"
                                    :class="(form.flags_estado & 16) ? 'bg-fuchsia-500/20 border-fuchsia-500 text-fuchsia-400' : 'bg-white/5 border-white/10 text-white/20 hover:text-fuchsia-400 hover:border-fuchsia-500/50'"
                                    title="Validación Manual (Sello Rosa)"
                                >
                                    <i class="fas fa-stamp text-[10px]"></i>
                                 </button>
                             </div>
                    </div>

                    <!-- Condicion IVA (20 chars approx) -->
                    <div class="col-span-3" @contextmenu.prevent="openIvaContextMenu">
                        <div class="flex justify-between mb-1">
                            <label class="block text-[10px] font-bold uppercase text-cyan-900/50">Condición IVA <span class="text-red-400">*</span></label>
                            <button @click="openAbm('IVA')" class="text-[9px] uppercase font-bold text-cyan-500 hover:text-cyan-400 focus:outline-none opacity-50 hover:opacity-100">
                                <i class="fas fa-cog"></i> ABM
                            </button>
                        </div>
                        <select v-model="form.condicion_iva_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-xs text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none truncate">
                            <option :value="null">Seleccionar...</option>
                            <option v-for="cond in condicionesIva" :key="cond.id" :value="cond.id">{{ cond.nombre }}</option>
                        </select>
                    </div>

                    <!-- Lista Precios (20 chars approx) -->
                    <div class="col-span-3">
                         <div class="flex justify-between mb-1">
                            <label class="block text-[10px] font-bold uppercase text-cyan-900/50">Lista Precios <span class="text-red-400">*</span></label>
                        </div>
                        <select v-model="form.lista_precios_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-xs text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none truncate">
                            <option :value="null" disabled>Seleccione Lista...</option>
                            <option v-for="lista in listasPrecios" :key="lista.id" :value="lista.id">{{ lista.nombre }}</option>
                        </select>
                    </div>

                    <!-- Segmento (15 chars approx) -->
                    <div class="col-span-2">
                         <div class="flex justify-between mb-1">
                            <label class="block text-[10px] font-bold uppercase text-cyan-900/50">Segmento <span class="text-red-400">*</span></label>
                             <button @click="openAbm('SEGMENTO')" class="text-[9px] uppercase font-bold text-cyan-500 hover:text-cyan-400 focus:outline-none opacity-50 hover:opacity-100">
                                <i class="fas fa-cog"></i>
                            </button>
                        </div>
                        <select v-model="form.segmento_id" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-xs text-cyan-100 focus:border-cyan-500 outline-none transition-colors appearance-none truncate">
                            <option :value="null">Sin Segmento</option>
                            <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                        </select>
                    </div>

                    <!-- Operativo (Small) -->
                    <div class="col-span-2 flex flex-col justify-end pb-1">
                        <div class="flex items-center justify-between bg-white/5 p-1.5 rounded border border-white/10">
                            <label class="text-[9px] font-bold text-cyan-900/70 uppercase mr-2">Operativo</label>
                            <button 
                                @click="toggleActive"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none"
                                :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                    :class="form.activo ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </button>
                        </div>
                    </div>
                </div>

                <!-- CUIT Warning Banner (Moved here) -->
                <div v-if="cuitWarningClients.length > 0 && !cuitWarningDismissed" class="mt-1 bg-yellow-900/10 border border-yellow-500/20 rounded p-2 text-xs">
                    <div class="flex flex-col gap-2">
                         <div class="flex items-start gap-2">
                             <i class="fas fa-store text-yellow-400 mt-0.5"></i>
                             <div>
                                 <p class="text-yellow-200 font-bold text-[10px] uppercase">CUIT Existente Detectado</p>
                                 <p class="text-yellow-200/50 text-[9px] leading-tight">Este CUIT ya pertenece a {{ cuitWarningClients.length }} cliente(s) (ej: {{ cuitWarningClients[0].razon_social }}).</p>
                             </div>
                         </div>
                         <div class="flex gap-2 justify-end">
                             <button @click="selectExistingClient(cuitWarningClients[0])" class="text-[9px] text-cyan-400 hover:text-cyan-300 underline mr-auto self-center">
                                 Ir al existente
                             </button>
                             <button @click="dismissCuitWarning" class="flex items-center gap-1 text-[9px] bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-200 px-3 py-1 rounded border border-yellow-500/30 uppercase font-bold transition-colors">
                                 <i class="fas fa-plus-circle"></i> Nueva Unidad de Negocio
                             </button>
                         </div>
                    </div>
                </div>
                <p v-if="cuitError" class="text-[10px] text-red-400 mt-1">{{ cuitError }}</p>


                <div v-if="isNew" class="pt-2 text-[10px] text-red-400/80 italic text-right">
                    * Campos Obligatorios
                </div>

                <div class="pt-4 border-t border-cyan-900/20">
                    <label class="block text-xs font-bold uppercase text-cyan-900/50 mb-1">Observaciones</label>
                    <textarea v-model="form.observaciones" rows="3" class="w-full bg-[#020a0f] border border-cyan-900/30 rounded p-2 text-cyan-100 focus:border-cyan-500 outline-none transition-colors resize-none text-sm placeholder-cyan-900/30"></textarea>
                </div>
            </div>

            <!-- TAB: DOMICILIOS -->
            <div v-else-if="activeTab === 'domicilios'" class="space-y-4">
                <div v-if="isNew" class="text-center p-4 text-cyan-900/50 text-sm">
                    Guarde el cliente para agregar domicilios.
                </div>
                <div v-else class="space-y-3">
                    <div 
                        v-for="dom in sortedDomicilios" 
                        :key="dom.id"
                        @dblclick="openDomicilioForm(dom)"
                        @contextmenu.prevent="openDomicilioContextMenu($event, dom)"
                        class="bg-cyan-900/5 border border-cyan-900/20 rounded-lg p-3 relative group hover:bg-cyan-900/10 transition-colors cursor-pointer select-none"
                    >
                        <div class="flex justify-between items-start pr-24">
                            <div class="flex items-center gap-2">
                            <span v-if="dom.es_fiscal" class="text-[10px] bg-purple-500/30 text-purple-200 font-bold px-2 py-0.5 rounded border border-purple-500/50 shadow-sm shadow-purple-900/20">FISCAL</span>
                            <span v-else class="text-[10px] bg-slate-700 text-white font-bold px-2 py-0.5 rounded border border-slate-600 shadow-sm shadow-black/20">SUCURSAL</span>
                            
                            <!-- Logistics Icon -->
                            <div v-if="dom.es_entrega" class="ml-2" :title="dom.origen_logistico === 'RETIRO_EN_PLANTA' ? 'Nos Retiran' : 'Despachamos'">
                                <i v-if="dom.origen_logistico === 'RETIRO_EN_PLANTA'" class="fa-solid fa-truck-pickup text-cyan-400 text-xs"></i>
                                <i v-else class="fa-solid fa-dolly text-emerald-400 text-xs"></i>
                            </div>
                        </div>
                        </div>
                        <p class="text-sm font-medium text-cyan-100 mt-1">{{ dom.calle }} {{ dom.numero }}</p>
                        <p class="text-xs text-cyan-200/50">{{ dom.localidad }}</p>
                        
                        <!-- Actions: Edit, Delete, Toggle -->
                        <div class="absolute top-2 right-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            
                            <!-- Toggle Active (Slider) - Intercept Fiscal -->
                            <button 
                                @click.stop="tryToggleDomicilioActive(dom)"
                                :title="dom.activo ? 'Desactivar Domicilio' : 'Activar Domicilio'"
                                class="relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none shrink-0"
                                :class="dom.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                            >
                                <span 
                                    class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                    :class="dom.activo ? 'translate-x-3.5' : 'translate-x-1'"
                                />
                            </button>

                            <!-- Edit -->
                            <button @click.stop="openDomicilioForm(dom)" class="text-cyan-200 hover:text-white bg-white/10 hover:bg-white/20 p-1.5 rounded transition-colors" title="Editar">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            
                            <!-- Delete (Tachito) - Intercept Fiscal -->
                            <button 
                                @click.stop="tryDeleteDomicilio(dom)" 
                                class="text-red-400 hover:text-red-300 bg-white/10 hover:bg-white/20 p-1.5 rounded transition-colors"
                                title="Eliminar Domicilio"
                            >
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <button @click="openDomicilioForm()" class="w-full py-2 border border-dashed border-cyan-500/30 rounded-lg text-cyan-400/50 hover:text-cyan-300 hover:border-cyan-400/50 hover:bg-cyan-500/5 transition-all text-xs font-bold uppercase">
                        <i class="fas fa-plus mr-1"></i> Agregar Domicilio
                    </button>
                </div>
            </div>

            <!-- TAB: CONTACTOS -->
            <div v-else-if="activeTab === 'contactos'" class="space-y-4">
                <div v-if="isNew" class="text-center p-4 text-cyan-900/50 text-sm">
                    Guarde el cliente para agregar contactos.
                </div>
                <div v-else class="space-y-3">
                    <div 
                        v-for="contact in form.vinculos" 
                        :key="contact.id"
                        class="bg-cyan-900/5 border border-cyan-900/20 rounded-lg p-3 flex items-center gap-3 relative group hover:bg-cyan-900/10 transition-colors"
                    >
                        <div class="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-600 to-blue-500 flex items-center justify-center text-xs font-bold text-white shrink-0">
                            {{ contact.nombre ? contact.nombre.substring(0,2).toUpperCase() : 'NN' }}
                        </div>
                        <div>
                            <p class="text-sm font-bold text-cyan-100">{{ contact.nombre }}</p>
                            <p class="text-[10px] text-cyan-200/50 uppercase">{{ contact.rol || 'Sin Rol' }}</p>
                        </div>
                         <!-- Edit Button (Placeholder) -->
                        <button class="absolute top-2 right-2 text-cyan-900/30 hover:text-cyan-100 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </div>

                     <button class="w-full py-2 border border-dashed border-cyan-900/30 rounded-lg text-cyan-900/50 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all text-xs font-bold uppercase">
                        <i class="fas fa-plus mr-1"></i> Agregar Contacto
                    </button>
                </div>
            </div>
        </div>

        <!-- Domicilio Form Overlay - Outside Tabs -->
        <!-- Domicilio Form Overlay - Outside Tabs -->
        <Teleport to="body">
            <div v-if="showDomicilioForm" class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" @click.self="showDomicilioForm = false">
                <DomicilioSplitCanvas 
                    :show="showDomicilioForm" 
                    :domicilio="selectedDomicilio" 
                    :has-fiscal="hasFiscalAddress"
                    @close="showDomicilioForm = false"
                    @saved="handleDomicilioSaved"
                />
            </div>
        </Teleport>

        <!-- Footer Actions (Sticky Bottom) -->
        <div class="sticky bottom-0 left-0 right-0 p-6 border-t border-cyan-900/20 flex gap-3 shrink-0 bg-black/40 z-50 shadow-[0_-5px_20px_rgba(0,0,0,0.5)]">
            <button @click="save" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded font-bold transition-colors shadow-lg shadow-cyan-900/20">
                <span v-if="saving"><i class="fas fa-spinner fa-spin mr-2"></i>Guardando...</span>
                <span v-else>Guardar (F10)</span>
            </button>
            <button v-if="!isNew" @click="remove" class="px-3 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded border border-red-500/30 transition-colors" title="Dar de baja lógica">
                <i class="fas fa-toggle-off"></i> <span class="ml-2 text-[10px] font-bold uppercase">Baja Lógica</span>
            </button>
            <button v-if="!isNew && !form.activo" @click="hardDelete" class="px-3 bg-red-600 hover:bg-red-500 text-white rounded shadow-lg shadow-red-900/40 transition-all active:scale-95" title="Eliminación Definitiva">
                <i class="fas fa-trash-alt"></i> <span class="ml-2 text-[10px] font-bold uppercase">Baja Física</span>
            </button>
        </div>
    </div>
    
    <!-- Condicion IVA Form Overlay (Old logic preserved but hidden/not used mostly) -->
    <CondicionIvaForm 
        :show="showCondicionIvaForm"
        :initial-view="condicionIvaStartView" 
        @close="showCondicionIvaForm = false"
        @saved="handleCondicionIvaSaved"
    />

    <!-- NEW SIMPLE ABM MODAL -->
    <Teleport to="body">
        <SimpleAbmModal
            v-if="showAbm"
            :title="abmTitle"
            :items="abmItems"
            :isLoading="abmLoading"
            @close="showAbm = false"
            @create="handleAbmCreate"
            @delete="handleAbmDelete"
        />
    </Teleport>

    <!-- Global Context Menu -->
    <Teleport to="body">
        <ContextMenu 
            v-if="contextMenu.show"
            v-model="contextMenu.show" 
            :x="contextMenu.x" 
            :y="contextMenu.y" 
            :actions="contextMenu.actions" 
            @close="contextMenu.show = false"
        />
    </Teleport>

     <!-- Transport Canvas Modal (V5) -->
     <Teleport to="body">
         <Transition name="fade">
             <TransporteCanvas
                v-if="showTransporteCanvas"
                v-model="selectedTransporte"
                @close="showTransporteCanvas = false"
                @save="handleTransporteCanvasCreate"
            />
         </Transition>
     </Teleport>

     <!-- INFILTRADOR AFIP (VANGUARD) -->
     <Teleport to="body">
         <Transition name="fade">
             <AfipComparisonOverlay
                v-if="showAfipInfiltration"
                :local-data="{...form, fiscalAddress: fiscalForm}"
                :arca-data="arcaResults"
                :condiciones-iva="condicionesIva"
                :is-new="isNew"
                @close="showAfipInfiltration = false"
                @confirm="handleAfipInfiltration"
            />
         </Transition>
     </Teleport>
</div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useMaestrosStore } from '../../../stores/maestros'
import { useClientesStore } from '../../../stores/clientes'
import { useNotificationStore } from '../../../stores/notification'
import clientesService from '../../../services/clientes'
// import DomicilioForm from './DomicilioForm.vue'
import DomicilioSplitCanvas from './DomicilioSplitCanvas.vue'
import CondicionIvaForm from '../../Maestros/CondicionIvaForm.vue'
import ContextMenu from '../../../components/common/ContextMenu.vue'
import SimpleAbmModal from '../../../components/common/SimpleAbmModal.vue'
import TransporteCanvas from './TransporteCanvas.vue'
import ContactoPopover from './ContactoPopover.vue'
import SmartSelect from '../../../components/ui/SmartSelect.vue'
import AfipComparisonOverlay from './AfipComparisonOverlay.vue'
import { useLogisticaStore } from '../../../stores/logistica'

const props = defineProps({
    modelValue: {
        type: Object,
        default: null
    },
    isNew: {
        type: Boolean,
        default: false
    },
    mode: {
        type: String,
        default: 'full' // 'full' | 'compact'
    }
})

const emit = defineEmits(['update:modelValue', 'close', 'save', 'delete', 'hard-delete', 'manage-segmentos', 'switch-client'])

const isCompact = computed(() => props.mode === 'compact')


const maestrosStore = useMaestrosStore()
const clienteStore = useClientesStore()
const logisticaStore = useLogisticaStore()
const notificationStore = useNotificationStore()

const segmentos = computed(() => maestrosStore.segmentos)
const condicionesIva = computed(() => maestrosStore.condicionesIva)
const provincias = computed(() => maestrosStore.provincias)
const terminosPago = computed(() => maestrosStore.terminosPago || []) // Assuming it exists or will add
const transportes = computed(() => logisticaStore.empresas) // Use Logistica Store

const listasPrecios = computed(() => maestrosStore.listasPrecios)
const sortedDomicilios = computed(() => {
    if (!form.value.domicilios) return []
    // [GY-FIX] Filter only active domicilios (Soft Delete View)
    return [...form.value.domicilios]
        .filter(d => d.activo !== false)
        .sort((a, b) => {
            if (a.es_fiscal && !b.es_fiscal) return -1
            if (!a.es_fiscal && b.es_fiscal) return 1
            return (a.alias || a.calle || '').localeCompare(b.alias || b.calle || '')
        })
})

// [GY-UX] Quick Transport Access (Linked to Main Address)
const quickTransportId = computed({
    get() {
        if (!form.value.domicilios || form.value.domicilios.length === 0) return null
        // 1. Try to find "Entrega" address
        const delivery = form.value.domicilios.find(d => d.es_entrega && d.activo !== false)
        if (delivery) return delivery.transporte_id
        // 2. Fallback to "Fiscal" address
        const fiscal = form.value.domicilios.find(d => d.es_fiscal && d.activo !== false)
        if (fiscal) return fiscal.transporte_id
        // 3. Fallback to first
        return form.value.domicilios[0].transporte_id
    },
    set(val) {
        if (!form.value.domicilios) return
        // Update PRIORITY address
        const target = form.value.domicilios.find(d => d.es_entrega && d.activo !== false) || 
                       form.value.domicilios.find(d => d.es_fiscal && d.activo !== false) ||
                       form.value.domicilios[0]
        
        if (target) {
            target.transporte_id = val
            // Mark as dirty/modified? Form binding handles it.
        } else {
             notificationStore.add('No hay domicilio activo para asignar transporte', 'warning')
        }
    }
})

const activeTab = ref('general')
const showAgenda = ref(false)
const saving = ref(false)

const GENERIC_CUITS = ['00000000000', '99999999999', '11111111111', '11111111119']
const commonCuitNames = {
    '11111111119': 'CONSUMIDOR FINAL GENERICO',
    '00000000000': 'CONSUMIDOR FINAL'
}

// 🧬 ENIGMA BLUEPRINT: CONSTANTS
const BIT_EXISTENCE = 1
const BIT_VIRGINITY = 2
const BIT_GOLD_ARCA = 4
const BIT_V14_STRUCT = 8
const BIT_OPERATOR_OK = 16
const BIT_MULTI_CUIT = 32

const clientColorClass = computed(() => {
    const flag = form.value.flags_estado || 9
    const cuit = (form.value.cuit || '').replace(/[^0-9]/g, '')
    const isGeneric = GENERIC_CUITS.includes(cuit) || cuit === '' || cuit.length < 5

    // Dominancia:
    // 1. Rosa (Genérico/Faltante)
    if (isGeneric) return 'text-fuchsia-400 border-fuchsia-500/30 focus:border-fuchsia-500 focus:ring-1 focus:ring-fuchsia-500/50'

    // 2. Azul (Multicliente)
    if (flag & BIT_MULTI_CUIT) return 'text-cyan-300 border-cyan-500/30 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]'

    // 3. Blanco (Gold ARCA)
    if (flag & BIT_GOLD_ARCA) return 'text-white border-emerald-500/30 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50'

    // 4. Rosa (Operador)
    if (flag & BIT_OPERATOR_OK) return 'text-fuchsia-400 border-fuchsia-500/30 focus:border-fuchsia-500 focus:ring-1 focus:ring-fuchsia-500/50'

    // 5. Amarillo (Amarillo Base)
    return 'text-yellow-400 border-yellow-500/30 focus:border-yellow-500 focus:ring-1 focus:ring-yellow-500/50'
})

const switchToContactsTab = () => {
    activeTab.value = 'contactos'
    showAgenda.value = false
}
// [GY-UX] CUIT Auto-Focus
const cuitInput = ref(null)
const focusCuit = () => {
    nextTick(() => {
        setTimeout(() => {
            if (cuitInput.value) {
                cuitInput.value.focus()
                cuitInput.value.select()
            }
        }, 150)
    })
}

const form = ref({})
const cuitError = ref(null)
const pristineName = ref('')
const templateId = ref(null)

const formInconsistency = computed(() => {
    const issues = []
    
    // Check CUIT (except for INT or Consumidor Final)
    const isSpecial = form.value.razon_social?.toUpperCase().includes('CONSUMIDOR FINAL') || 
                      form.value.condicion_iva_id === 'INT' // This assumes 'INT' is an ID or label, will verify
    
    if (!form.value.cuit && !isSpecial) {
        issues.push('CUIT faltante')
    }
    
    if (!form.value.condicion_iva_id) {
        issues.push('Condición IVA faltante')
    }
    
    if (!form.value.segmento_id && !isSpecial) {
        issues.push('Segmento no definido')
    }

    // Check Fiscal Domicile
    const hasFiscal = form.value.domicilios?.some(d => d.es_fiscal && d.activo)
    if (!hasFiscal && !props.isNew) {
        issues.push('Sin domicilio fiscal activo')
    }

    return issues
})

const hasInconsistency = computed(() => formInconsistency.value.length > 0)

const headerTitle = computed(() => {
    if (!props.modelValue && !props.isNew) return 'Inspector'
    return props.isNew ? 'Nuevo Cliente' : 'Editar Cliente'
})

const headerSubtitle = computed(() => {
    // Fix reactivity: check form.value.cuit if editing, or modelValue if valid. 
    // Actually form.value is the source of truth for the inputs.
    return form.value.cuit || (props.isNew ? 'Nuevo' : 'Sin CUIT')
})

const hasFiscalAddress = computed(() => {
    if (!form.value.domicilios) return false
    return form.value.domicilios.some(d => d.es_fiscal && d.activo !== false)
})

const formatCuitInput = () => {
    let val = form.value.cuit || ''
    // Allow digits and up to 2 separators (-, _, /)
    // First remove anything that is not digit or separator
    val = val.replace(/[^0-9\-_/]/g, '')
    
    // Check separator count
    const separators = val.match(/[\-_/]/g)
    if (separators && separators.length > 2) {
        // Keep only first 2
       // This is complex to do via regex replace on the fly, easier to warn or truncate.
       // Let's iterate chars
       let count = 0
       let newVal = ''
       for (let char of val) {
           if (['-', '_', '/'].includes(char)) {
               count++
               if (count <= 2) newVal += char
           } else {
               newVal += char
           }
       }
       val = newVal
    }
    
    form.value.cuit = val.slice(0, 13) // Max 13 chars
    cuitError.value = null
    // Reset warning on typing
    cuitWarningDismissed.value = false
    if (val.length < 13) cuitWarningClients.value = []
}

// CUIT Multi-Sede Warning System
const cuitWarningClients = ref([])
const cuitWarningDismissed = ref(false)

const dismissCuitWarning = () => {
    cuitWarningDismissed.value = true
}

const aplicarSelloAzul = () => {
    // [V14] Sello Azul (Multi-CUIT) +32
    if (form.value.flags_estado & BIT_MULTI_CUIT) {
        form.value.flags_estado &= ~BIT_MULTI_CUIT
        notificationStore.add('Sello Azul retirado', 'info')
    } else {
        form.value.flags_estado |= BIT_MULTI_CUIT
        notificationStore.add('Sello Azul aplicado (CUIT Compartido)', 'success')
        cuitWarningDismissed.value = true
    }
}

const checkCuitBackend = async () => {
    // Check if we have a potentially valid CUIT (at least 11 digits, valid structure)
    if (!form.value.cuit) return
    if (!validateCuit(form.value.cuit)) return 
    
    try {
        const res = await clienteStore.checkCuit(form.value.cuit, props.isNew ? null : form.value.id)
        if (res.status === 'EXISTS' || res.status === 'INACTIVE') {
            cuitWarningClients.value = res.existing_clients
            // Do not reset dismissed flag here if it was already dismissed for THIS cuit?
            // Actually users might tab out multiple times. If they dismissed it, keep it dismissed unless they changed input.
            // But 'cuitWarningDismissed' is reset in 'formatCuitInput' (on input). 
            // So here we don't need to force reset it to false, allowing persistance if user just tabs out again.
            // However, if we found new results (different list?), maybe we should?
            // For simplicity, if input didn't change (handled by formatCuitInput), we respect current dismissed state.
        } else {
            cuitWarningClients.value = []
            cuitWarningDismissed.value = false
        }
    } catch (e) {
        console.error("Error checking CUIT:", e)
    }

}

// --- RAR-V5 BRIDGE (AFIP) ---
const loadingAfip = ref(false)
const showAfipInfiltration = ref(false)
const arcaResults = ref(null)

const consultarAfip = async () => {
    if (!form.value.cuit || form.value.cuit.length < 11) {
        notificationStore.add('Ingrese un CUIT válido (11 dígitos)', 'warning')
        return
    }
    
    notificationStore.add('Llamando a Satélite RAR... Iniciando Infiltración.', 'info')
    // Feedback Amarillo Neón (Visual) en notificación si es posible
    loadingAfip.value = true
    try {
        const response = await clientesService.checkAfip(form.value.cuit)
        const res = response.data 

        if (res.error) {
            notificationStore.add(`Fallo en Puente: ${res.error}`, 'error')
            return
        }
        
        // Open Overlay for Comparison
        arcaResults.value = res
        showAfipInfiltration.value = true
        
        notificationStore.add('Datos Fiscales Recuperados. Pendiente de Infiltración.', 'success')
        
    } catch (e) {
        console.error("Error consultando AFIP:", e)
        const errorDetail = e.response?.data?.detail || e.message
        notificationStore.add(`Error de Conexión Satélite: ${errorDetail}`, 'error')
    } finally {
        loadingAfip.value = false
    }
}

const handleAfipInfiltration = async (payload) => {
    const res = payload.data
    const targetFlag = payload.flag

    // 1. Update Golden Data
    form.value.razon_social = res.razon_social
    form.value.estado_arca = 'VALIDADO'
    form.value.datos_arca_last_update = new Date().toISOString()
    
    // 2. Aplicar Doctrina de Virginidad (Flags)
    form.value.flags_estado = targetFlag
    
    // 3. Map Condicion IVA (Smart Mapping V14)
    const arcaIvaName = (res.condicion_iva || '').toUpperCase()
    const ivaTarget = condicionesIva.value.find(c => {
        const localName = (c.nombre || '').toUpperCase()
        return localName === arcaIvaName || arcaIvaName.includes(localName) || localName.includes(arcaIvaName)
    })
    if (ivaTarget) {
        form.value.condicion_iva_id = ivaTarget.id
    }
    
    // 4. Update Domicilio Fiscal (Smart Parser)
    if (res.parsed_address) {
        const pa = res.parsed_address
        fiscalForm.value.calle = pa.calle || ''
        fiscalForm.value.localidad = pa.localidad || ''
        fiscalForm.value.numero = pa.numero || ''
        
        if (pa.provincia) {
            const provName = pa.provincia.toUpperCase()
            const targetProv = provincias.value.find(p => 
                p.nombre.toUpperCase() === provName || 
                provName.includes(p.nombre.toUpperCase()) ||
                p.nombre.toUpperCase().includes(provName)
            )
            if (targetProv) {
                fiscalForm.value.provincia_id = targetProv.id
            }
        }
        notificationStore.add(`Identidad Infiltrada: ${res.razon_social} (Flag ${targetFlag})`, 'success')
    }

    showAfipInfiltration.value = false
}

const toggleRetira = () => {
    // [V14] Genuine Toggle
    if (quickTransportId.value === null) {
        // Toggling back from Retira: Try to assign first transport as fallback
        if (transportes.value.length > 0) {
            quickTransportId.value = transportes.value[0].id
            notificationStore.add('Método de entrega: DESPACHO (' + transportes.value[0].nombre + ')', 'success')
        } else {
            notificationStore.add('No hay transportes definidos para asignar', 'warning')
        }
    } else {
        quickTransportId.value = null // Toggle to Retira
        notificationStore.add('Método de entrega: RETIRO CLIENTE', 'info')
    }
}

const aplicarRosaManual = () => {
    // [V14] Evolución 9 -> 25 (Excluyente de Gold)
    if (form.value.flags_estado & BIT_GOLD_ARCA) {
        notificationStore.add('Imposible aplicar Rosa: El cliente ya es Gold ARCA', 'warning')
        return
    }

    if (form.value.flags_estado & BIT_OPERATOR_OK) {
        form.value.flags_estado &= ~BIT_OPERATOR_OK
        notificationStore.add('Sello Rosa retirado', 'info')
    } else {
        form.value.flags_estado |= BIT_OPERATOR_OK
        notificationStore.add('Sello Rosa aplicado (Validación Manual)', 'success')
    }
}
// ----------------------------

const selectExistingClient = (clientSummary) => {
    if(confirm(`¿Desea descartar el alta y cargar el cliente "${clientSummary.razon_social}"?`)) {
         emit('switch-client', clientSummary.id)
    }
}

const validateCuit = (cuit) => {
    if (!cuit) return false
    const clean = cuit.replace(/[^0-9]/g, '')
    if (clean.length !== 11) return false
    
    // [GY-FIX] Excepción de CUITs Genéricos (Consumidor Final / Mostrador)
    if (['00000000000', '99999999999', '11111111111'].includes(clean)) return true;
    
    const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    let total = 0
    for (let i = 0; i < 10; i++) {
        total += parseInt(clean[i]) * multipliers[i]
    }
    
    let mod = total % 11
    let digit = mod === 0 ? 0 : 11 - mod
    if (digit === 10) digit = 9 // Rare case, typically handled by different algorithm variant but acceptable for standard simplified check
    
    // Official algorithm handles 10 slightly differently (Type Z), but standard personal/business CUITs follow this.
    // If we want to be strict: 
    // Verification digit is clean[10]
    const valid = digit === parseInt(clean[10])
    if (!valid) {
        cuitError.value = 'CUIT inválido (Dígito verificador incorrecto)'
    } else {
        cuitError.value = null
    }
    return valid
}

// Fiscal Form for New Client
// Fiscal Form for New Client
const fiscalForm = ref({
    calle: '',
    numero: '',
    localidad: '',
    provincia_id: null,
    // transposte moved to delivery
})

// Delivery Form logic (Alta Refactor)
const useFiscalAsDelivery = ref(true)
const deliveryForm = ref({
    calle: '',
    numero: '',
    // Localidad/Provincia inferred or duplicated if needed, keeping simple text for now
})

watch(() => useFiscalAsDelivery.value, (val) => {
    if (val) {
        // Sync Logic could happen on save, or reactive?
        // Let's keep deliveryForm distinct but ignore it on save if flag is true
    }
})

// Domicilio Management (Editing)
const showDomicilioForm = ref(false)
const selectedDomicilio = ref(null)

const openDomicilioForm = (dom = null) => {
    selectedDomicilio.value = dom
    showDomicilioForm.value = true
}

const handleDomicilioSaved = async (domData) => {
    try {
        if (domData.id) {
            await clienteStore.updateDomicilio(form.value.id, domData.id, domData)
            notificationStore.add('Domicilio actualizado', 'success')
        } else {
            await clienteStore.createDomicilio(form.value.id, domData)
            notificationStore.add('Domicilio creado', 'success')
        }
        
        // [GY-FIX] Force Refresh from Backend to ensure Full Consistency
        // Bypass return value optimization to guarantee relationships (active/fiscal) are 100% synced
        const freshClient = await clienteStore.fetchClienteById(form.value.id)
        form.value = JSON.parse(JSON.stringify(freshClient)) // Deep copy to reset form state
        
        showDomicilioForm.value = false
    } catch (error) {
        console.error(error)
        notificationStore.add('Error al guardar domicilio', 'error')
    }
}

// Condicion IVA Management
const showCondicionIvaForm = ref(false)
const condicionIvaStartView = ref('list')

const openCondicionIva = (view = 'list') => {
    condicionIvaStartView.value = view
    showCondicionIvaForm.value = true
}

const handleCondicionIvaSaved = async () => {
    await maestrosStore.fetchCondicionesIva()
    // Don't close automatically if in list mode? Or close?
    // User requested "Alta rápida". If fast add, usually close.
    if (condicionIvaStartView.value === 'form') {
         showCondicionIvaForm.value = false
    } else {
        // In manager mode, stay open?
        // But CondicionIvaForm emits 'saved', let's just refresh.
        // It handles internal view switch if needed.
    }
    notificationStore.add('Condición de IVA actualizada', 'success')
}

// Context Menu Logic
const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const openIvaContextMenu = (e) => {
    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: [
            { 
                label: 'Administrar (ABM)', 
                iconClass: 'fas fa-tasks', 
                handler: () => { openCondicionIva('list') } 
            },
            { 
                label: 'Nueva Condición (+)', 
                iconClass: 'fas fa-plus', 
                handler: () => { openCondicionIva('form') } 
            }
        ]
    }
}

const openDomicilioContextMenu = (e, dom) => {
    // Only for Fiscal Addresses (that need special handling)
    if (!dom.es_fiscal) return;

    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: [
            {
                label: 'Dar de baja (Transferir Fiscalidad)',
                iconClass: 'fas fa-exchange-alt',
                handler: () => { transferFiscalityAndDeactivate(dom) }
            }
        ]
    }
}

const transferFiscalityAndDeactivate = async (currentFiscal) => {
    // 1. Find Candidate (Next Active Domicilio)
    // We use form.value.domicilios source of truth
    const candidates = form.value.domicilios.filter(d => d.id !== currentFiscal.id && d.activo !== false);

    if (candidates.length === 0) {
        notificationStore.add('Imposible dar de baja: No existe otro domicilio para heredar la condición Fiscal.', 'error');
        return;
    }

    const heir = candidates[0]; // Pick the first available one
    
    if (confirm(`¿Confirma transferir la condición FISCAL a "${heir.calle} ${heir.numero}" y dar de baja el actual?`)) {
        try {
            // Step 1: Promote Heir (Backend will auto-demote current fiscal, but we do it explicitly to be safe contextually)
            // Backend create_domicilio/update_domicilio has logic: if new is fiscal, others become not fiscal.
            // So we update Heir to be Fiscal.
            await clienteStore.updateDomicilio(form.value.id, heir.id, { ...heir, es_fiscal: true });
            
            // Step 2: Deactivate Old Fiscal (Now it should be non-fiscal effectively, or we ensure it)
            // We reload because Step 1 might have changed the state on backend.
            // But we can just send update to deactivate specific ID.
            await clienteStore.deleteDomicilio(form.value.id, currentFiscal.id); // Soft delete

            notificationStore.add('Fiscalidad transferida y domicilio dado de baja.', 'success');
            
            // Refresh
            const freshClient = await clienteStore.fetchClienteById(form.value.id);
            form.value = JSON.parse(JSON.stringify(freshClient));

        } catch (error) {
            console.error(error);
            notificationStore.add('Error al transferir fiscalidad.', 'error');
        }
    }
}



const deleteDomicilio = async (dom) => {
    if (!confirm(`¿Está seguro que desea eliminar el domicilio de ${dom.calle}? Esta acción no se puede deshacer.`)) return
    
    try {
        await clienteStore.deleteDomicilio(form.value.id, dom.id)
        
        // Refresh client
        const updatedClient = await clienteStore.fetchClienteById(form.value.id)
        form.value = JSON.parse(JSON.stringify(updatedClient))
        emit('switch-client', updatedClient.id) // Force refresh
        
        notificationStore.add('Domicilio eliminado', 'success')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al eliminar domicilio', 'error')
    }
}

const toggleDomicilioActive = async (dom) => {
    try {
        const newState = !dom.activo
        // Optimistic update
        dom.activo = newState
        
        // [GY-FIX] Use store instead of direct service for consistency
        await clienteStore.updateDomicilio(form.value.id, dom.id, { ...dom, activo: newState })
        
        // Background refresh to ensure consistency
        const freshClient = await clienteStore.fetchClienteById(form.value.id)
        form.value = JSON.parse(JSON.stringify(freshClient))
        
        // Force list refresh to ensure indicators update in Grid/List
        clienteStore.fetchClientes()
    } catch (e) {
        console.error(e)
        dom.activo = !dom.activo // Revert on error
        notificationStore.add('Error al actualizar estado', 'error')
    }
}

// --- Domicilio Actions Interceptors ---
const tryToggleDomicilioActive = (dom) => {
    // If activating, just do it
    if (!dom.activo) {
        toggleDomicilioActive(dom)
        return
    }

    // If deactivating...
    if (dom.es_fiscal) {
         // Fiscal Protection Logic
         const activeCandidates = form.value.domicilios.filter(d => d.id !== dom.id && d.activo !== false)
         
         if (activeCandidates.length === 0) {
             // Case: Unique Address
             notificationStore.add('Imposible desactivar: Es el único domicilio fiscal y no hay alternativas.', 'error')
             return
         }
         
         // Case: Alternatives exist
         // Trigger Confirmation/Transfer
         transferFiscalityAndDeactivate(dom)
         return
    }

    // Normal deactivation
    toggleDomicilioActive(dom)
}

const tryDeleteDomicilio = (dom) => {
    if (dom.es_fiscal) {
         const activeCandidates = form.value.domicilios.filter(d => d.id !== dom.id && d.activo !== false)
         
         if (activeCandidates.length === 0) {
             notificationStore.add('Imposible eliminar: Es el domicilio fiscal obligatorio.', 'error')
             return
         }
         
         // Trigger Transfer/Delete
         transferFiscalityAndDeactivate(dom) // Reuse transfer logic which ends in delete
         return
    }
    
    deleteDomicilio(dom)
}


const showTransporteCanvas = ref(false)
const selectedTransporte = ref(null)

const openTransportContextMenu = (e) => {
    const currentId = quickTransportId.value
    const actions = [
        { 
            label: 'Nuevo Transporte (F4)', 
            iconClass: 'fas fa-plus', 
            handler: () => { 
                selectedTransporte.value = {
                    id: null,
                    nombre: '',
                    telefono_reclamos: '',
                    web_tracking: '',
                    activo: true,
                    requiere_carga_web: false,
                    servicio_retiro_domicilio: false,
                    formato_etiqueta: 'PROPIA',
                    cuit: '',
                    condicion_iva_id: null,
                    direccion: '',
                    localidad: '',
                    provincia_id: null,
                    direccion_despacho: '',
                    horario_despacho: '',
                    telefono_despacho: ''
                }
                showTransporteCanvas.value = true 
            } 
        }
    ]

    if (currentId) {
        actions.push({
            label: 'Editar Seleccionado',
            iconClass: 'fas fa-pencil-alt',
            handler: () => {
                const t = transportes.value.find(tr => tr.id === currentId)
                if (t) {
                    selectedTransporte.value = { ...t }
                    showTransporteCanvas.value = true
                } else {
                    notificationStore.add('Transporte no encontrado en lista local', 'warning')
                }
            }
        })
    }
    
    contextMenu.value = {
        show: true,
        x: e.clientX,
        y: e.clientY,
        actions: actions
    }
}

const handleTransporteCanvasCreate = async (newId) => {
    await logisticaStore.fetchEmpresas()
    if (newId) quickTransportId.value = newId
    notificationStore.add('Transporte asignado', 'success')
    showTransporteCanvas.value = false
}


// Initialize form when modelValue changes
watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        form.value = JSON.parse(JSON.stringify(newVal)) // Deep copy
        // Ensure arrays exist
        if (!form.value.domicilios) form.value.domicilios = []
        if (newVal.activo === undefined) form.value.activo = true // Default to true if undefined
        // Ensure arrays exist
    } else {
        form.value = {}
    }
    
    // Reset/Populate fiscal form
    if (newVal) {
        const fiscal = newVal.domicilios?.find(d => d.es_fiscal && d.activo !== false)
        if (fiscal) {
            fiscalForm.value = {
                calle: fiscal.calle || '',
                numero: fiscal.numero || '',
                localidad: fiscal.localidad || '',
                provincia_id: fiscal.provincia_id
            }
        } else {
            fiscalForm.value = { calle: '', numero: '', localidad: '', provincia_id: null }
        }
    }

    if (props.isNew) {
        activeTab.value = 'general'
        useFiscalAsDelivery.value = true
        deliveryForm.value = { calle: '', numero: '' }
        templateId.value = null
        pristineName.value = form.value.razon_social || ''
        
        // [V14] Genoma: Todo cliente nace como Flag 9 (1+8)
        if (!form.value.flags_estado) {
            form.value.flags_estado = BIT_EXISTENCE | BIT_V14_STRUCT
        }
    }

    if (props.isNew || (newVal && newVal._forceFocus)) {
        focusCuit()
    }
}, { immediate: true })

const handleTemplateSelect = (itemOrId) => {
    let template = null;
    if (typeof itemOrId === 'object') {
        template = itemOrId;
    } else {
        template = clienteStore.clientes.find(c => c.id === itemOrId);
    }

    if (template) {
        // Inherit everything except ID, CUIT (usually differs for clones unless multi-sede)
        form.value = {
            ...JSON.parse(JSON.stringify(template)),
            id: null,
            // Keep current CUIT if user already typed it? or clear it?
            // Usually if they search template, they want to KEEP their typed CUIT but get the REST.
            cuit: form.value.cuit || '',
             _isClone: true
        };
        pristineName.value = template.razon_social;
        // If template has fiscal address, maybe load it too?
        // Let's assume they want to change the address.
    }
}

const handleManualTemplate = (name) => {
    // [GY-MOD] Manual creation bypass if not found in Cantera
    if (name) {
        form.value.razon_social = name
        // Set focus to CUIT field maybe? Or just leave it.
    }
    templateId.value = null
    notificationStore.add('Alta Manual: Complete los datos', 'info')
}

// --- ABM LOGIC ---
const showAbm = ref(false)
const abmLoading = ref(false)
const abmType = ref(null) // 'IVA' | 'SEGMENTO'
const abmTitle = computed(() => abmType.value === 'IVA' ? 'Condiciones de IVA' : 'Segmentos')
const abmItems = computed(() => abmType.value === 'IVA' ? condicionesIva.value : segmentos.value)

const openAbm = (type) => {
    abmType.value = type
    showAbm.value = true
}

const handleAbmCreate = async (name) => {
    // [GY-UX] Duplicate Validation (Frontend)
    const exists = abmItems.value.some(item => item.nombre.toLowerCase() === name.toLowerCase())
    if (exists) {
        notificationStore.add(`"${name}" ya existe en la lista`, 'warning')
        return
    }

    abmLoading.value = true
    try {
        let res;
        if (abmType.value === 'IVA') {
            res = await maestrosStore.createCondicionIva({ nombre: name })
            if (res && res.id) form.value.condicion_iva_id = res.id
        } else {
            res = await maestrosStore.createSegmento({ nombre: name })
            if (res && res.id) form.value.segmento_id = res.id
        }
        notificationStore.add('Elemento creado y seleccionado', 'success')
        showAbm.value = false
    } catch (e) {
        console.error(e)
        notificationStore.add('Error al crear elemento', 'error')
    } finally {
        abmLoading.value = false
    }
}



const handleAbmDelete = async (id) => {
    try {
        if (abmType.value === 'IVA') {
            await maestrosStore.deleteCondicionIva(id)
        } else {
             // Implement Segmento deletion
             if (maestrosStore.deleteSegmento) {
                 await maestrosStore.deleteSegmento(id)
             } else {
                 console.warn("deleteSegmento implementation missing in store")
                 alert("Funcionalidad no implementada en backend aún.")
                 return
             }
        }
        notificationStore.add('Elemento eliminado', 'success')
    } catch (e) {
        console.error(e)
        notificationStore.add('Error: Elemento en uso o fallo técnico', 'error')
    }
}


const toggleActive = () => {
    if (form.value.activo) {
        // If turning off, we might want to trigger the delete flow or just toggle
        // For now, just toggle, but parent might intercept save
        if (!confirm('¿Está seguro que desea desactivar este cliente?')) return
    }
    form.value.activo = !form.value.activo
}

const save = async () => {
    saving.value = true
    try {
        // [DEOU Flow] If no changes in name for a new template-based item, cancel save
        if (props.isNew && form.value.razon_social === pristineName.value && form.value._isClone) {
            alert('No se detectaron cambios en el nombre. No se generará un nuevo registro.');
            emit('close');
            return;
        }

        // [GY-UX] Flexible Validation (V14)
        // If we are DEACTIVATING, skip strict business validations (Segmento, Lista Precios, IVA)
        // Only require basic Identity (Razon Social, CUIT)
        const isDeactivating = !form.value.activo;
        
        // Bypass for Generic CUITs
    if (GENERIC_CUITS.includes(form.value.cuit)) {
        notificationStore.add('CUIT Genérico Detectado: Se omite validación ARCA', 'info')
        if (!form.value.razon_social) {
            form.value.razon_social = commonCuitNames[form.value.cuit] || 'CONSUMIDOR FINAL'
        }
        // Force mapped status if needed
        return
    }
        // Validation for New Client
        // Shared Validations (Create & Edit)
        if (!form.value.razon_social) {
             alert('La Razón Social es obligatoria.')
             saving.value = false
             return
        }
        if (!form.value.cuit) {
             alert('El CUIT es obligatorio.')
             saving.value = false
             return
        }
        
        // CUIT Validation
        if (!validateCuit(form.value.cuit) && form.value.activo) { // Allow invalid CUIT if deactivating? Maybe not.
            cuitError.value = 'CUIT inválido (Dígito verificador incorrecto)'
            saving.value = false
            return
        }

        // Check if Generic CUIT
        const cleanCuit = form.value.cuit ? form.value.cuit.replace(/[^0-9]/g, '') : ''
        const isGenericCuit = ['00000000000', '99999999999', '11111111111'].includes(cleanCuit)

        // Strict Validations ONLY if Active
        if (!isDeactivating) {
             if (!form.value.segmento_id && !isGenericCuit) {
                 alert('El Segmento es obligatorio para activar el cliente.')
                 saving.value = false
                 return
             }
             if (!form.value.lista_precios_id) {
                 alert('La Lista de Precios es obligatoria para activar el cliente.')
                 saving.value = false
                 return
             }
             if (!form.value.condicion_iva_id && !isGenericCuit) {
                  // For Generic, we can auto-set Consumidor Final if not set
                  if (isGenericCuit) {
                      const consFinal = condicionesIva.value.find(c => c.nombre.toLowerCase().includes('consumidor final'))
                      if (consFinal) form.value.condicion_iva_id = consFinal.id
                  } else {
                     alert('La Condición IVA es obligatoria para activar el cliente.')
                     saving.value = false
                     return
                  }
             }
        }

        // Specific Validations for New Client
        if (props.isNew) {
            // [GY-FIX] Skip Address Check for Generic CUITs
            if (!isGenericCuit) {
                if (!fiscalForm.value.calle || !fiscalForm.value.numero || !fiscalForm.value.localidad || !fiscalForm.value.provincia_id) {
                    alert('Por favor complete todos los datos obligatorios del Domicilio Fiscal.')
                    saving.value = false
                    return
                }
            } else {
                // Auto-fill dummy fiscal for generic if empty
                if (!fiscalForm.value.calle) {
                     fiscalForm.value = {
                         calle: 'Mostrador',
                         numero: 'S/N',
                         localidad: 'Local',
                         provincia_id: provincias.value.length > 0 ? provincias.value[0].id : null, 
                         transporte_id: null
                     }
                }
            }

            // FORCE CHECK before saving to ensure state is up to date
            await checkCuitBackend()
            
            // Check duplicates (Skip for Generic)
            if (cuitWarningClients.value.length > 0 && !isGenericCuit) {
                if (cuitWarningDismissed.value) {
                    form.value.requiere_auditoria = true
                } else {
                    if(!confirm(`Este CUIT ya existe en ${cuitWarningClients.value.length} clientes. ¿Confirma que es una nueva sede/facultad?`)) {
                        saving.value = false
                        return
                    }
                    form.value.requiere_auditoria = true
                }
            }

            // New Client Logic (With Dual Address)
            const payload = { ...form.value }
            
            // 1. Prepare Fiscal Domicilio
            const fiscalDom = {
                ...fiscalForm.value,
                es_fiscal: true,
                // Logic: A fiscal address CAN be delivery too. 
                // But V5 model allows multiple.
                // If "Use Fiscal As Delivery" is true -> Fiscal is ALSO Delivery.
                // If false -> Fiscal is NOT Delivery (another one is).
                es_entrega: useFiscalAsDelivery.value, 
                activo: true,
                transporte_id: useFiscalAsDelivery.value ? quickTransportId.value : null // Link transport if it is delivery
            }

            payload.domicilios = [fiscalDom]

            // 2. Prepare Delivery Domicilio (if separate)
            if (!useFiscalAsDelivery.value) {
                const deliveryDom = {
                    calle: deliveryForm.value.calle || fiscalForm.value.calle, 
                    numero: deliveryForm.value.numero || fiscalForm.value.numero,
                    localidad: fiscalForm.value.localidad, 
                    provincia_id: fiscalForm.value.provincia_id,
                    es_fiscal: false,
                    es_entrega: true,
                    activo: true,
                    transporte_id: quickTransportId.value
                }
                payload.domicilios.push(deliveryDom)
            }
            
            // [GY-FIX] Single Create Call
            const result = await clienteStore.createCliente(payload)
            emit('save', result)
            notificationStore.add('Cliente creado con éxito', 'success')
            emit('close')
            return // Exit early after creation
        } 
        
        // --- UPDATE LOGIC (Existing Client) ---
        // 1. Persist Fiscal Address Changes (from General Tab)
        const fiscalIdx = form.value.domicilios.findIndex(d => d.es_fiscal && d.activo !== false)
        if (fiscalIdx !== -1) {
            const currentFiscal = form.value.domicilios[fiscalIdx]
            // Solo actualizamos si hubo cambios para evitar triggers innecesarios
            if (currentFiscal.calle !== fiscalForm.value.calle || 
                currentFiscal.numero !== fiscalForm.value.numero ||
                currentFiscal.localidad !== fiscalForm.value.localidad ||
                currentFiscal.provincia_id !== fiscalForm.value.provincia_id) {
                
                const updatedDom = { ...currentFiscal, ...fiscalForm.value }
                await clienteStore.updateDomicilio(form.value.id, currentFiscal.id, updatedDom)
            }
        }

        const payload = { ...form.value }
        delete payload.domicilios // Safe now as we updated it separately
        
        if (quickTransportId.value) {
            payload.transporte_id = quickTransportId.value
        }
        const result = await clienteStore.updateCliente(form.value.id, payload)
        
        // [V14-FIX] Ensure local state is updated with backend result (Flags, etc)
        form.value = JSON.parse(JSON.stringify(result))

        emit('save', result)
        notificationStore.add('Cliente actualizado con éxito. DNA Sincronizado.', 'success')

        if (props.isNew) {
             emit('close')
        }
    } catch(e) {
        console.error(e)
        // Show clearer error
        alert('Error al guardar: ' + (e.response?.data?.detail || e.message))
    } finally {
        saving.value = false
    }
}



const remove = () => {
    if (confirm('¿Seguro que desea dar de baja LOGICA a este cliente? (Pasará a Inactivo)')) {
        emit('delete', form.value)
    }
}

const hardDelete = () => {
    if (confirm('⚠ ATENCION: ¿Está seguro de realizar la BAJA FISICA? Esta acción eliminará permanentemente al cliente de la base de datos y no se puede deshacer.')) {
        emit('hard-delete', form.value)
    }
}

const handleKeydown = (e) => {
    if (e.key === 'F10') { // Changed from e.code to e.key for better compatibility
        e.preventDefault()
        if (showDomicilioForm.value) return 
        save()
    }
    if (e.key === 'Escape' && !showDomicilioForm.value) { 
        e.preventDefault()
        emit('close')
    }
}

onMounted(() => {
    maestrosStore.fetchAll() // Ensure we have masters
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})


</script>
