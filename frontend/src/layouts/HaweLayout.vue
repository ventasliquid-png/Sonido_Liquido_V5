<template>
  <div class="flex h-screen w-screen bg-[#0a0a0a] overflow-hidden">
    <!-- Global Sidebar -->
    <AppSidebar :theme="currentTheme" />

    <!-- Main Content Area -->
    <main class="flex-1 relative overflow-hidden">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from '../components/layout/AppSidebar.vue';

const route = useRoute();

const currentTheme = computed(() => {
    if (route.name === 'Rubros') return 'rose';
    if (['Transportes', 'Contactos'].includes(route.name)) return 'amber';
    if (['Pedidos'].includes(route.name)) return 'green';
    if (['HaweHome', 'HaweClientCanvas'].includes(route.name)) return 'cyan';
    return 'cyan'; // Default
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
