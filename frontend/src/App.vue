<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ToastNotification from './components/ui/ToastNotification.vue';
import { useClientesStore } from './stores/clientes';
import { useProductosStore } from './stores/productos';
import { useMaestrosStore } from './stores/maestros';

const router = useRouter();
const route = useRoute();
const clientesStore = useClientesStore();
const productosStore = useProductosStore();
const maestrosStore = useMaestrosStore();

const ready = ref(false);
const booting = ref(true);
const bootStatus = ref('INICIALIZANDO SISTEMA...');

const initSystem = async () => {
    console.log('[Boot] Starting system initialization...');
    
    // Safety release: After 15 seconds, we release the UI no matter what.
    const safetyRelease = setTimeout(() => {
        if (booting.value) {
            console.warn('[Boot] Safety timeout reached. Releasing UI...');
            booting.value = false;
        }
    }, 15000);

    try {
        bootStatus.value = 'HIVE-MIND: CONECTANDO...';
        
        // Sequential fetch with detailed status
        await maestrosStore.fetchSegmentos();
        bootStatus.value = `SEGMENTOS: ${maestrosStore.segmentos.length} OK`;
        await new Promise(r => setTimeout(r, 200));

        bootStatus.value = 'Buscando Productos...';
        await productosStore.fetchProductos();
        bootStatus.value = `PRODUCTOS: ${productosStore.productos.length} OK`;
        await new Promise(r => setTimeout(r, 200));
        
        bootStatus.value = 'Buscando Rubros...';
        await productosStore.fetchRubros();
        bootStatus.value = `RUBROS: ${productosStore.rubros.length} OK`;
        await new Promise(r => setTimeout(r, 200));

        bootStatus.value = 'Buscando Clientes...';
        await clientesStore.fetchClientes();
        bootStatus.value = `CLIENTES: ${clientesStore.clientes.length} OK`;
        await new Promise(r => setTimeout(r, 200));
        
        bootStatus.value = 'SISTEMA OPERATIVO';
        setTimeout(() => {
            booting.value = false;
            clearTimeout(safetyRelease);
            console.log('[Boot] System fully synced and ready.');
        }, 800);
    } catch (e) {
        console.error('[Boot] Critical error during init:', e);
        bootStatus.value = 'FALLA TÁCTICA - VERIFIQUE BACKEND';
        setTimeout(() => {
            booting.value = false;
            clearTimeout(safetyRelease);
        }, 5000);
    }
};

onMounted(async () => {
    console.log('[App] Mounting...');
    await router.isReady();
    ready.value = true; 
    
    // Give Vue a moment to render the Splash screen before blocking with async calls
    setTimeout(async () => {
        await initSystem();
    }, 100);
});

const menuItems = [
    { name: 'Clientes', path: '/hawe/clientes', icon: '👥' },
    { name: 'Productos', path: '/hawe/productos', icon: '📦' },
    { name: 'Pedidos', path: '/hawe/pedidos', icon: '🛒' },
    { name: 'Transportes', path: '/hawe/transportes', icon: '🚚' },
    { name: 'Segmentos', path: '/hawe/segmentos', icon: '🏷️' },
    { name: 'Rubros', path: '/hawe/rubros', icon: '📚' },
    { name: 'Vendedores', path: '/hawe/vendedores', icon: '💼' },
    { name: 'Agenda', path: '/agenda', icon: '📒' },
];

const isLoginPage = computed(() => route.name === 'Login');

const navigate = (path) => {
    router.push(path);
};

const logout = () => {
    localStorage.removeItem('token');
    router.push('/login');
};
</script>

<template>
  <div v-if="ready">
    <!-- GLOBAL SPLASH / BOOT SCREEN -->
    <transition name="fade">
        <div v-if="booting" class="fixed inset-0 z-[100] bg-[#020617] flex flex-col items-center justify-center overflow-hidden">
            <!-- HUD Background Effect -->
            <div class="absolute inset-0 opacity-20 pointer-events-none">
                <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-emerald-500/20 via-transparent to-transparent"></div>
                <div class="w-full h-full bg-[linear-gradient(rgba(16,185,129,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.05)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
            </div>

            <!-- Central Content -->
            <div class="relative flex flex-col items-center gap-8">
                <!-- Glowing Orb / Core -->
                <div class="relative h-24 w-24">
                    <div class="absolute inset-0 rounded-full bg-emerald-500/20 blur-xl animate-pulse"></div>
                    <div class="relative h-24 w-24 rounded-full border-2 border-emerald-500 flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.4)]">
                        <i class="fas fa-microchip text-3xl text-emerald-500 animate-pulse"></i>
                    </div>
                </div>

                <!-- Boot Text -->
                <div class="flex flex-col items-center gap-2">
                    <h2 class="text-xs font-mono font-bold tracking-[0.3em] text-emerald-500/60 uppercase">System Bootstrap v5.10</h2>
                    <div class="h-[2px] w-48 bg-emerald-950 rounded-full overflow-hidden">
                        <div class="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,1)] animate-[loading_2s_infinite]"></div>
                    </div>
                    <p class="text-[10px] font-mono font-bold text-emerald-400 mt-2 animate-pulse">{{ bootStatus }}</p>
                </div>
            </div>

            <!-- Decorative HUD corners -->
            <div class="absolute top-8 left-8 w-12 h-12 border-t-2 border-l-2 border-emerald-500/30"></div>
            <div class="absolute top-8 right-8 w-12 h-12 border-t-2 border-r-2 border-emerald-500/30"></div>
            <div class="absolute bottom-8 left-8 w-12 h-12 border-b-2 border-l-2 border-emerald-500/30"></div>
            <div class="absolute bottom-8 right-8 w-12 h-12 border-b-2 border-r-2 border-emerald-500/30"></div>
        </div>
    </transition>

    <!-- HAWE LAYOUT (Isolated) -->
    <div v-if="route.path.startsWith('/hawe') || route.path.startsWith('/agenda')" class="h-screen w-screen overflow-hidden bg-[#0f172a]">
        <router-view />
    </div>

    <!-- STANDARD LAYOUT -->
    <div v-else class="flex h-screen w-screen overflow-hidden bg-[#0f172a]">
        <ToastNotification />
        <!-- SIDEBAR -->
        <aside v-if="!isLoginPage" class="w-16 md:w-64 bg-slate-900 text-white flex flex-col transition-all duration-300">
            <div class="h-16 flex items-center justify-center md:justify-start md:px-6 border-b border-slate-800">
                <span class="text-2xl">💧</span>
                <span class="hidden md:block ml-3 font-bold tracking-wider text-sm">SONIDO LÍQUIDO</span>
            </div>

            <nav class="flex-1 py-6 space-y-2">
                <a 
                    v-for="item in menuItems" 
                    :key="item.path"
                    @click="navigate(item.path)"
                    class="flex items-center px-4 py-3 cursor-pointer transition-colors border-l-4"
                    :class="route.path.startsWith(item.path) ? 'bg-slate-800 border-[#54cb9b] text-white' : 'border-transparent text-slate-400 hover:bg-slate-800 hover:text-white'"
                >
                    <span class="text-xl">{{ item.icon }}</span>
                    <span class="hidden md:block ml-3 text-sm font-medium">{{ item.name }}</span>
                </a>
            </nav>

            <div class="p-4 border-t border-slate-800">
                <div class="flex items-center justify-center md:justify-start mb-2">
                    <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold">U</div>
                    <div class="hidden md:block ml-3">
                        <p class="text-xs font-bold">Admin</p>
                        <p class="text-[10px] text-slate-500">Administrador</p>
                    </div>
                </div>
                <button @click="logout" class="w-full flex items-center justify-center md:justify-start text-red-400 hover:text-red-300 text-sm">
                    <span class="text-xl">🚪</span>
                    <span class="hidden md:block ml-3">Cerrar Sesión</span>
                </button>
            </div>
        </aside>

        <!-- MAIN CONTENT (With Padding for Floating Effect) -->
        <main class="flex-1 flex flex-col overflow-hidden relative p-4 bg-black">
            <router-view v-slot="{ Component }">
                <transition name="fade" mode="out-in">
                    <component :is="Component" />
                </transition>
            </router-view>
        </main>
    </div>
  </div>
</template>

<style>
@keyframes loading {
    0% { transform: translateX(-100%); }
    50% { transform: translateX(0); }
    100% { transform: translateX(100%); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* --- HUD BORDER UTILITIES (HYPER GLOW - GLOBAL INJECTION) --- */
.hud-border-red {
    border: 3px solid #f43f5e !important;
    box-shadow: 0 0 25px rgba(244, 63, 94, 0.5), inset 0 0 15px rgba(244, 63, 94, 0.3) !important;
}

.hud-border-cyan {
    border: 3px solid #06b6d4 !important;
    box-shadow: 0 0 25px rgba(6, 182, 212, 0.5), inset 0 0 15px rgba(6, 182, 212, 0.3) !important;
}

.hud-border-green {
    border: 3px solid #10b981 !important;
    box-shadow: 0 0 25px rgba(16, 185, 129, 0.5), inset 0 0 15px rgba(16, 185, 129, 0.3) !important;
}

.hud-border-amber {
    border: 3px solid #f59e0b !important;
    box-shadow: 0 0 25px rgba(245, 158, 11, 0.5), inset 0 0 15px rgba(245, 158, 11, 0.3) !important;
}
</style>