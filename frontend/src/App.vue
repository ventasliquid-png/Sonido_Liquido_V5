<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const menuItems = [
    { name: 'Clientes', path: '/clientes', icon: '👥' },
    { name: 'Transportes', path: '/transportes', icon: '🚚' },
    { name: 'Segmentos', path: '/segmentos', icon: '🏷️' },
    { name: 'Vendedores', path: '/vendedores', icon: '💼' },
    { name: 'Listas Precios', path: '/listas-precios', icon: '💲' },
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
  <div class="flex h-screen w-screen overflow-hidden bg-slate-100">
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

      <!-- MAIN CONTENT -->
      <main class="flex-1 flex flex-col overflow-hidden relative">
          <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                  <component :is="Component" />
              </transition>
          </router-view>
      </main>
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
</style>