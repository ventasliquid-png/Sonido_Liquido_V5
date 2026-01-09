<!-- ClientCanvas.vue: Natural Habitat for Client Management -->
<template>
  <div class="flex h-full w-full bg-[var(--hawe-bg-panel)] text-white overflow-hidden font-sans">
    
    <!-- ZONE 1: STATIC DATA (Left Panel) -->
    <aside class="w-80 flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-md z-20">
      <!-- Header -->
      <div class="h-14 flex items-center justify-between px-6 border-b border-white/10 shrink-0">
        <div class="flex items-center gap-4">
            
            <!-- RETURN MODE -->
            <button 
                v-if="returnUrl" 
                @click="goBackToSource" 
                class="flex items-center gap-2 text-white hover:text-green-400 transition-colors group px-3 py-1.5 rounded bg-green-900/20 border border-green-500/30" 
                title="Volver a la operación anterior"
            >
                <i class="fa-solid fa-arrow-left text-green-400"></i>
                <span class="font-outfit text-sm font-bold uppercase tracking-wider text-green-400">Volver al Pedido</span>
            </button>

            <!-- STANDARD MODE -->
            <button 
                v-else 
                @click="goToList" 
                class="flex items-center gap-2 text-white hover:text-cyan-400 transition-colors group" 
                title="Ir al Listado de Clientes"
            >
                <i class="fa-solid fa-list text-cyan-400"></i>
                <span class="font-outfit text-sm font-bold uppercase tracking-wider text-cyan-400">Fichas</span>
            </button>
        </div>
        
        <button v-if="!isNew" @click="goToNew" class="flex items-center gap-2 text-white/50 hover:text-white px-3 py-1.5 rounded-md hover:bg-white/5 transition-all group border border-transparent hover:border-white/10">
            <i class="fa-solid fa-plus text-xs"></i>
            <span class="font-outfit text-xs font-bold uppercase tracking-wider">Nuevo Cliente</span>
        </button>
      </div>

      <!-- Form -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
        <!-- Avatar & Name -->
        <div class="text-center">
            <div class="relative group cursor-pointer inline-block">
                <div class="h-20 w-20 rounded-full bg-white/10 flex items-center justify-center text-3xl text-cyan-400 border-2 border-white/20 group-hover:border-cyan-400 transition-colors mx-auto">
                <i class="fa-solid fa-building"></i>
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
            
            <!-- LIVE AUDIT STATUS -->
            <div v-if="auditResult.code !== 'VERDE'" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 animate-pulse">
                <div class="flex items-center gap-2 mb-2">
                    <i class="fa-solid fa-triangle-exclamation text-red-400"></i>
                    <span class="text-xs font-bold text-red-400 uppercase">Ficha Incompleta</span>
                </div>
                <ul class="list-disc list-inside text-[10px] text-red-300/80 font-mono">
                    <li v-for="reason in auditResult.reasons" :key="reason">{{ reason }}</li>
                </ul>
            </div>
            
            <!-- CUIT -->
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
            
            <!-- CONDICION IVA -->
            <div class="bg-white/5 rounded-lg p-3 border border-white/5">
                <label class="block text-[10px] font-bold uppercase text-white/40 mb-1">CONDICIÓN IVA</label>
                <div class="w-full">
                    <select 
                        v-model="form.condicion_iva_id" 
                        class="w-full bg-transparent text-sm text-white focus:outline-none appearance-none [&>option]:bg-slate-900 border-b border-white/10 focus:border-cyan-400 pb-1"
                    >
                        <option :value="null">Seleccionar...</option>
                        <option v-for="iva in condicionesIva" :key="iva.id" :value="iva.id">
                            {{ iva.nombre }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- SEGMENTOS -->
            <div class="bg-white/5 rounded-lg p-3 border border-white/5" @dblclick="showSegmentoList = true" title="Doble click para administrar">
                <label 
                    class="block text-[10px] font-bold uppercase text-white/40 mb-1 cursor-pointer hover:text-white/80 select-none"
                    @contextmenu.prevent="handleSegmentoContextMenu($event)"
                >
                    SEGMENTOS
                </label>
                <div class="w-full flex gap-2">
                    <select 
                        v-model="form.segmento_id" 
                        @change="handleSegmentoChange"
                        class="flex-1 bg-transparent text-sm text-white focus:outline-none appearance-none [&>option]:bg-slate-900 border-b border-white/10 focus:border-cyan-400 pb-1"
                    >
                        <option :value="null">Sin Segmento</option>
                        <option value="__NEW__" class="text-green-400 font-bold">+ Crear Nuevo Segmento</option>
                        <option disabled>----------------</option>
                        <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                    </select>
                    <button 
                         @click="showSegmentoList = true"
                         class="text-white/30 hover:text-cyan-400 transition-colors px-1"
                         title="Administrar Segmentos"
                    >
                        <i class="fa-solid fa-cog"></i>
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
                    <i class="fa-solid fa-globe w-4 text-white/30"></i>
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
    <main class="flex-1 flex flex-col relative bg-gradient-to-br from-[#1e3a8a] to-[#0f172a]">

        
        <!-- TAB: CLIENTE (Main View) -->
        <template v-if="activeTab === 'CLIENTE'">
            <!-- Top Dashboard -->
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
                        <div class="flex items-center gap-4">
                            <!-- Active Toggle -->
                            <div class="flex items-center gap-2 bg-black/20 px-2 py-1 rounded-full border border-white/10">
                                <span class="text-[10px] font-bold uppercase" :class="form.activo ? 'text-green-400' : 'text-red-400'">
                                    {{ form.activo ? 'OPERATIVO' : 'INACTIVO' }}
                                </span>
                                <button 
                                    @click="form.activo = !form.activo"
                                    class="relative inline-flex h-4 w-8 items-center rounded-full transition-colors focus:outline-none"
                                    :class="form.activo ? 'bg-green-500/50' : 'bg-red-500/50'"
                                    title="Click para cambiar estado"
                                >
                                    <span 
                                        class="inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform shadow-sm"
                                        :class="form.activo ? 'translate-x-4' : 'translate-x-1'"
                                    />
                                </button>
                            </div>
                            
                            <span class="text-white/30 text-xs">•</span>
                            <span class="text-white/50 text-xs ml-1 font-mono">Nro: {{ form.codigo_interno || '---' }}</span>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats Cards (Hidden in New Mode) -->
                <div v-if="!isNew" class="flex gap-4">
                    
                    <!-- NEW: Fiscal Address Badge -->
                    <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[180px] max-w-[250px] flex flex-col justify-center">
                        <p class="text-[10px] uppercase text-white/40 font-bold mb-1"><i class="fa-solid fa-map-pin mr-1"></i>Domicilio Fiscal</p>
                        <p class="text-xs text-white font-medium truncate" :title="computedFiscalAddress">{{ computedFiscalAddress }}</p>
                    </div>

                    <!-- Saldo with Dynamic Color -->
                    <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[120px]">
                        <p class="text-[10px] uppercase text-white/40 font-bold">Saldo Actual</p>
                        <p 
                            class="text-lg font-mono font-bold"
                            :class="form.saldo > 0 ? 'text-red-400' : (form.saldo < 0 ? 'text-green-400' : 'text-white')"
                        >
                            $ {{ form.saldo ? Number(form.saldo).toFixed(2) : '0.00' }}
                        </p>
                    </div>

                    <div class="bg-black/20 rounded-lg p-3 border border-white/5 min-w-[120px]">
                        <p class="text-[10px] uppercase text-white/40 font-bold">Última Compra</p>
                        <p class="text-lg text-white/70">{{ form.fecha_ultima_compra ? new Date(form.fecha_ultima_compra).toLocaleDateString() : '--/--/--' }}</p>
                    </div>
                    
                    <!-- Pendientes Dropdown -->
                    <div class="relative group">
                        <button class="bg-cyan-900/20 rounded-lg p-3 border border-cyan-500/30 min-w-[120px] text-left hover:bg-cyan-900/40 transition-colors w-full">
                            <p class="text-[10px] uppercase text-cyan-400 font-bold flex justify-between">
                                Pendientes <i class="fa-solid fa-chevron-down"></i>
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
                                        class="block text-xs font-bold uppercase text-white/40 mb-1 cursor-pointer hover:text-white/80 select-none"
                                        @contextmenu.prevent="handleSegmentoContextMenu($event)"
                                        @dblclick="showSegmentoList = true"
                                        title="Doble click para administrar"
                                    >
                                        Segmento
                                    </label>
                                    <div class="flex gap-2">
                                        <select v-model="form.segmento_id" class="flex-1 bg-black/20 text-sm text-white focus:outline-none p-2 rounded border border-white/10 focus:border-cyan-400 appearance-none [&>option]:bg-slate-900">
                                            <option :value="null">Seleccionar Segmento...</option>
                                            <option v-for="seg in segmentos" :key="seg.id" :value="seg.id">{{ seg.nombre }}</option>
                                        </select>
                                        <button @click="showAddSegmento = true" class="px-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-cyan-400 hover:text-cyan-300 transition-colors" title="Nuevo Segmento">
                                            <i class="fa-solid fa-plus"></i>
                                        </button>
                                    </div>
                                </div>
                             </div>
                        </div>
                        
                        <div class="bg-white/5 p-6 rounded-xl border border-white/10 opacity-50">
                             <h3 class="text-sm font-bold text-white/90 mb-4 uppercase border-b border-white/10 pb-2">Próximos Pasos</h3>
                             <ul class="space-y-2 text-sm text-white/60">
                                 <li><i class="fa-solid fa-circle-check text-white/20 mr-2"></i>Guardar Datos Básicos</li>
                                 <li><i class="fa-solid fa-circle text-white/20 mr-2"></i>Cargar Domicilios</li>
                                 <li><i class="fa-solid fa-circle text-white/20 mr-2"></i>Cargar Contactos</li>
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
                                <h3 class="text-sm font-bold text-white/90"><i class="fa-solid fa-note-sticky mr-2 text-yellow-400"></i>Notas Internas</h3>
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
                                    <div class="h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400"><i class="fa-solid fa-check"></i></div>
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
                        <i class="fa-solid fa-copy mr-2"></i>Clonar
                    </button>
                    <button 
                        v-if="!isNew && form.activo"
                        @click="deleteCliente"
                        class="px-4 py-2 rounded-lg text-red-400 hover:bg-red-900/20 hover:text-red-300 text-sm font-medium transition-colors"
                    >
                        Dar de Baja
                    </button>
                    <button 
                        v-if="!isNew && !form.activo"
                        @click="activateCliente"
                        class="px-4 py-2 rounded-lg text-green-400 hover:bg-green-900/20 hover:text-green-300 text-sm font-medium transition-colors"
                    >
                        Activar
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
        <div class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
            <!-- Domicilios -->
            <section>
                <div class="flex items-center justify-between mb-3">
                    <h3 
                        class="text-sm font-bold text-cyan-400 bg-white/5 px-3 py-1.5 rounded-md border border-white/10 w-full block text-center mb-4 shadow-sm cursor-pointer select-none hover:bg-white/10 transition-colors relative group"
                        @contextmenu.prevent="handleDomicilioContextMenu($event)"
                        @dblclick="showDomicilioList = true"
                        title="Doble click para administrar"
                    >
                        LOGÍSTICA
                        <button 
                            @click.stop="showTransporteManager = true"
                            class="absolute right-2 top-1/2 -translate-y-1/2 text-white/30 hover:text-cyan-400 transition-colors"
                            title="Administrar Transportes"
                        >
                            <i class="fa-solid fa-truck"></i>
                        </button>
                    </h3>
                </div>
                <div class="space-y-2">
                    <div 
                        v-for="dom in domicilios.filter(d => d.activo !== false)" 
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
                            <button @click.stop="openDomicilioTab(dom)" class="text-[10px] text-white/30 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"><i class="fa-solid fa-pencil"></i></button>
                        </div>
                        <p class="text-sm font-medium text-white leading-tight">{{ dom.calle }} {{ dom.numero }}</p>
                        <p class="text-xs text-white/50">{{ dom.localidad }}</p>
                        <div class="mt-2 flex items-center gap-2 text-xs text-white/40">
                            <i class="fa-solid fa-truck"></i> {{ dom.transporte?.nombre || dom.transporte_nombre || 'Sin Transporte' }}
                        </div>
                    </div>
                    
                    <!-- Add Button -->
                    <button 
                        @click="openDomicilioTab()"
                        class="w-full py-2 border border-dashed border-white/10 rounded-lg text-white/30 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all flex items-center justify-center gap-2 text-xs font-bold uppercase"
                    >
                        <i class="fa-solid fa-plus"></i> Agregar Domicilio
                    </button>
                </div>
            </section>

            <!-- Contactos -->
            <section>
                <div class="flex items-center justify-between mb-3">
                    <h3 class="text-sm font-bold text-cyan-400 bg-white/5 px-3 py-1.5 rounded-md border border-white/10 w-full block text-center mb-4 shadow-sm">CONTACTOS</h3>
                    <button @click="addContacto" class="text-cyan-400 hover:text-cyan-300 text-xs"><i class="fa-solid fa-plus"></i></button>
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
                                    <button @click="editContacto(contact)" class="text-[10px] text-white/30 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"><i class="fa-solid fa-pencil"></i></button>
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

    <DomicilioList 
        v-if="showDomicilioList"
        :domicilios="domicilios"
        class="fixed inset-0 z-[60] m-4 rounded-lg shadow-2xl overflow-hidden"
        @close="showDomicilioList = false"
        @create="openDomicilioTab(); showDomicilioList = false"
        @edit="openDomicilioTab($event); showDomicilioList = false"
        @delete="handleDomicilioDelete($event)"
    />

    <div v-if="showTransporteManager" class="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-8">
        <div class="bg-[#0a253a] border border-white/10 rounded-xl w-full h-full shadow-2xl overflow-hidden">
            <TransporteManager :isModal="true" @close="showTransporteManager = false" />
        </div>
    </div>

    <ContactoForm 
        v-if="showContactoForm && form.id"
        :show="showContactoForm"
        :clienteId="String(form.id)"
        :contacto="selectedContacto"
        @close="showContactoForm = false"
        @saved="handleContactoSaved"
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
import DomicilioList from './components/DomicilioList.vue'
import TransporteManager from './components/TransporteManager.vue'
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
const activeTab = ref('CLIENTE') // 'CLIENTE', 'DOMICILIO', 'CONTACTO'

const form = ref({
    id: null,
    razon_social: '',
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

// Computed Helpers
const condicionesIva = computed(() => maestrosStore.condicionesIva)
const segmentos = computed(() => maestrosStore.segmentos)
const auditResult = computed(() => {
    // Construct a temporary client object from form data to reactive check
    const tempClient = {
        ...form.value,
        domicilios: domicilios.value, 
        domicilio_fiscal_resumen: null 
    }
    return evaluateCliente(tempClient)
})
const returnUrl = computed(() => route.query.returnUrl)

// [New] Fiscal Address Helper
const computedFiscalAddress = computed(() => {
    if (domicilios.value && domicilios.value.length > 0) {
        const fiscal = domicilios.value.find(d => d.es_fiscal)
        if (fiscal) return `${fiscal.calle} ${fiscal.numero}, ${fiscal.localidad}`
    }
    return 'Sin Domicilio Fiscal'
})

// --- Navigation Methods ---
const goToList = () => router.push('/hawe')
const goBackToSource = () => {
    if (returnUrl.value) router.push(returnUrl.value)
    else router.push('/hawe')
}
const goToNew = () => router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })

// --- Initialization ---
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
        if (route.query.search) {
             form.value.razon_social = route.query.search
        }
    } else {
        isNew.value = false
        await loadCliente(route.params.id)
    }
})

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

// --- Core Client Logic ---
const resetForm = () => {
    form.value = {
        id: null,
        razon_social: '',
        cuit: '',
        condicion_iva_id: null, // Should match 'Responsable Inscripto' ID ideally, or null
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
            domicilios.value = client.domicilios || []
            contactos.value = client.vinculos || [] 
            
            if (!client.cuit || client.cuit === '00-00000000-0') {
                 notificationStore.add(`ADVERTENCIA: Cliente cargado con CUIT inválido`, 'warning')
            }
        } else {
            notificationStore.add('Error: Cliente no encontrado', 'error')
        }
    } catch (e) {
        console.error(`[ClientCanvas] Exception in loadCliente:`, e)
        notificationStore.add('Error al cargar cliente', 'error')
    }
}

const saveCliente = async () => {
    try {
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
        
        goBackToSource()
    } catch (e) {
        notificationStore.add('Error al guardar cliente', 'error')
        console.error(e)
    }
}

const deleteCliente = async () => {
    if(!confirm('¿Está seguro de dar de baja este cliente?')) return
    try {
        await store.deleteCliente(form.value.id)
        notificationStore.add('Cliente dado de baja', 'success')
        router.push('/hawe')
    } catch (e) {
        notificationStore.add('Error al dar de baja', 'error')
    }
}

const activateCliente = async () => {
    try {
        form.value.activo = true
        await saveCliente()
    } catch (e) {
        notificationStore.add('Error al reactivar cliente', 'error')
        form.value.activo = false // Revert on error
    }
}

const cloneCliente = () => {
    form.value.id = null
    form.value.razon_social += ' (Copia)'
    form.value.codigo_interno = ''
    isNew.value = true
    router.push({ name: 'HaweClientCanvas', params: { id: 'new' } })
    notificationStore.add('Cliente clonado. Edite y guarde.', 'info')
}

// --- Specific Logic & UI Handlers ---
const handleCuitInput = (e) => {
    form.value.cuit = e.target.value.replace(/[^0-9]/g, '')
}

// Segmentos
const showAddSegmento = ref(false)
const newSegmentoName = ref('')
const showSegmentoList = ref(false)
const showSegmentoModal = ref(false)
const editingSegmentoId = ref(null)

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

const handleSegmentoContextMenu = (e) => {
    contextMenu.value.show = true
    contextMenu.value.x = e.clientX
    contextMenu.value.y = e.clientY
    contextMenu.value.actions = [
        {
            label: 'Nuevo Segmento',
            icon: 'plus', // FontAwesome class logic in component? Icon text for now
            handler: () => { 
                editingSegmentoId.value = null
                showSegmentoModal.value = true 
            }
        },
        {
            label: 'Administrar Segmentos',
            icon: 'list',
            handler: () => { showSegmentoList.value = true }
        }
    ]
}

const closeSegmentoModal = () => {
    showSegmentoModal.value = false
    editingSegmentoId.value = null
}
const handleSegmentoSaved = async () => {
    await maestrosStore.fetchSegmentos(null, true) 
}

// Domicilios
const showDomicilioList = ref(false)
const showTransporteManager = ref(false)
const selectedDomicilio = ref(null)
const selectedDomicilioId = ref(null)

const openDomicilioTab = (domicilio = null) => {
    selectedDomicilio.value = domicilio
    activeTab.value = 'DOMICILIO'
}

const handleDomicilioSaved = async (domicilioData) => {
    try {
        let savedDom;
        if (domicilioData.id) {
            savedDom = await store.updateDomicilio(form.value.id, domicilioData.id, domicilioData);
            notificationStore.add('Domicilio actualizado', 'success');
        } else {
            savedDom = await store.createDomicilio(form.value.id, domicilioData);
            notificationStore.add('Domicilio creado', 'success');
        }
        
        if (!savedDom.activo) savedDom.activo = true; 
        
        if (domicilioData.id) {
            const index = domicilios.value.findIndex(d => d.id === domicilioData.id);
            if (index !== -1) domicilios.value[index] = savedDom;
        } else {
            domicilios.value.push(savedDom);
        }
        
        await store.fetchClientes(); 
    } catch (error) {
        console.error(error);
        notificationStore.add('Error al guardar domicilio', 'error');
    }
    activeTab.value = 'CLIENTE'
}

const selectDomicilio = (dom) => {
    selectedDomicilioId.value = dom.id
}

const handleDomicilioDelete = async (dom) => {
    if (!confirm('¿Está seguro de eliminar este domicilio?')) return;
    try {
        await store.deleteDomicilio(form.value.id, dom.id);
        domicilios.value = domicilios.value.filter(d => d.id !== dom.id);
        notificationStore.add('Domicilio eliminado', 'success');
    } catch (error) {
        console.error(error);
        notificationStore.add('Error al eliminar domicilio', 'error');
    }
    if (selectedDomicilioId.value === dom.id) {
        selectedDomicilioId.value = null;
        selectedDomicilio.value = null;
    }
}

const handleDomicilioContextMenu = (e, dom = null) => {
    contextMenu.value.show = true
    contextMenu.value.x = e.clientX
    contextMenu.value.y = e.clientY
    
    if (dom) {
        contextMenu.value.actions = [
            {
                label: 'Editar Domicilio',
                icon: 'edit',
                handler: () => openDomicilioTab(dom)
            },
            {
                label: 'Eliminar',
                icon: 'trash',
                handler: () => handleDomicilioDelete(dom)
            }
        ]
    } else {
        contextMenu.value.actions = [
            {
                label: 'Nuevo Domicilio',
                icon: 'plus',
                handler: () => openDomicilioTab()
            },
            {
                label: 'Administrar Domicilios',
                icon: 'list',
                handler: () => { showDomicilioList.value = true }
            }
        ]
    }
}

// Contactos
const showContactoForm = ref(false)
const selectedContacto = ref(null)

const addContacto = () => {
    if (isNew.value) {
        notificationStore.add('Guarde el cliente antes de agregar contactos', 'warning')
        return
    }
    selectedContacto.value = null
    showContactoForm.value = true
}

const editContacto = (c) => {
    selectedContacto.value = c
    showContactoForm.value = true
}

const handleContactoSaved = async () => {
    await loadCliente(form.value.id)
}

// Global UI
const contextMenu = ref({
    show: false,
    x: 0,
    y: 0,
    actions: []
})

const handleKeydown = (e) => {
    // Global shortcuts
    if (e.key === 'Escape') {
        if (activeTab.value === 'DOMICILIO') {
             activeTab.value = 'CLIENTE'
             return
        }
        goBackToSource()
    }
    if (e.key === 'F10') {
        e.preventDefault()
        saveCliente()
    }
}

// Debug Info
const debugInfo = computed(() => {
    return JSON.stringify({
        id: form.value.id,
        cuit: form.value.cuit,
        razon_social: form.value.razon_social,
        domicilios_count: domicilios.value.length,
        params_id: route.params.id
    }, null, 2)
})
</script>
