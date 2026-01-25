<template>
  <div class="h-full flex flex-col bg-[#0f172a] text-white">
    
    <!-- GATED ACCESS -->
    <div v-if="!isAuthenticated" class="flex-1 flex items-center justify-center bg-[#0d1321]">
         <div class="bg-[#1e293b] p-8 rounded-2xl border-2 border-indigo-500/30 shadow-[0_0_50px_rgba(79,70,229,0.1)] max-w-md w-full text-center">
            <div class="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                 <i class="fas fa-user-shield text-4xl text-indigo-500"></i>
            </div>
            
            <h2 class="text-2xl font-bold text-white mb-2">UTILIDADES MAESTRAS</h2>
            <p class="text-gray-400 mb-8 text-sm">Zona restringida (Nivel 4).<br>Ingrese Clave de Administrador.</p>
            
            <!-- HONEYPOT (Catch browser autofill) -->
            <div class="h-0 w-0 overflow-hidden opacity-0">
                 <input type="text" name="username_honey" tabindex="-1" aria-hidden="true" />
                 <input type="password" name="password_honey" tabindex="-1" aria-hidden="true" />
            </div>
            
            <!-- ACTUAL PIN INPUT (Type=text + CSS Masking) -->
            <input 
                ref="pinInputRef"
                type="text" 
                inputmode="numeric"
                pattern="[0-9]*"
                autocomplete="off"
                v-model="pinInput" 
                @keydown.enter="verifyPin"
                class="w-full bg-black/50 border border-gray-700 rounded-xl px-4 py-3 text-center text-2xl tracking-[0.5em] text-white font-mono focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all mb-4"
                style="-webkit-text-security: disc;"
                placeholder="PIN"
                maxlength="8"
            />
            
            <button @click="verifyPin" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl transition-colors mb-4">
                ACCEDER
            </button>
            <p v-if="authError" class="text-red-400 text-xs animate-pulse font-bold">{{ authError }}</p>
         </div>
    </div>

    <!-- UNLOCKED INTERFACE -->
    <div v-else class="flex-1 flex flex-col h-full">
        <!-- TOOLBAR -->
        <div class="h-16 bg-[#1e293b] border-b border-indigo-500/20 flex items-center px-4 justify-between shrink-0">
            <h1 class="text-lg font-bold text-indigo-400 flex items-center gap-2">
                <i class="fas fa-tools"></i>
                <span class="tracking-widest">MASTER TOOLS</span>
            </h1>
            
            <div class="flex gap-2">
                <button 
                    v-for="tab in tabs" 
                    :key="tab.id"
                    @click="currentTab = tab.id"
                    class="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
                    :class="currentTab === tab.id ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'"
                >
                    <i :class="tab.icon"></i> {{ tab.label }}
                </button>
            </div>

            <button @click="lock" class="text-gray-500 hover:text-red-400 transition-colors" title="Bloquear">
                <i class="fas fa-lock"></i>
            </button>
        </div>

        <!-- CONTENT AREA -->
        <div class="flex-1 overflow-hidden relative">
            <component :is="activeComponent" />
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, defineAsyncComponent } from 'vue';

// --- AUTH ---
const CONST_ADMIN_PIN = "1974"; // Hardcoded for V5
const isAuthenticated = ref(false);
const pinInput = ref('');
const authError = ref('');
const pinInputRef = ref(null);

const verifyPin = () => {
    if (pinInput.value === CONST_ADMIN_PIN) {
        isAuthenticated.value = true;
        authError.value = '';
    } else {
        authError.value = 'ACCESO DENEGADO';
        pinInput.value = '';
        setTimeout(() => authError.value = '', 2000);
    }
};

const lock = () => {
    isAuthenticated.value = false;
    pinInput.value = '';
    nextTick(() => pinInputRef.value?.focus());
};

// --- TABS & COMPONENTS ---
const currentTab = ref('purgatorio');

const tabs = [
    { id: 'purgatorio', label: 'Gestión de Bajas', icon: 'fas fa-dumpster-fire' },
    // Future expansion: { id: 'users', label: 'Usuarios', icon: 'fas fa-users-cog' }
];

// Lazy load components
const HardDeleteManager = defineAsyncComponent(() => import('../DataIntel/HardDeleteManager.vue'));

const activeComponent = computed(() => {
    if (currentTab.value === 'purgatorio') return HardDeleteManager;
    return null;
});

onMounted(() => {
    nextTick(() => {
        if (!isAuthenticated.value) pinInputRef.value?.focus();
    });
});

</script>
