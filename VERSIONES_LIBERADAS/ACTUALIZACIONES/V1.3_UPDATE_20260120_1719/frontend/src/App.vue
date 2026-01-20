<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ToastNotification from './components/ui/ToastNotification.vue';

const router = useRouter();
const route = useRoute();
const ready = ref(false);

onMounted(async () => {
    await router.isReady();
    ready.value = true;
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
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