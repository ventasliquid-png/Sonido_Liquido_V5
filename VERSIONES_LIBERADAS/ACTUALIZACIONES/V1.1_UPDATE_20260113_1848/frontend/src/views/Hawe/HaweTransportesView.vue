<template>
  <div class="flex h-screen w-full bg-[var(--hawe-bg-main)] text-gray-200 overflow-hidden font-sans">
    <!-- Left Sidebar (Reused from HaweView) -->


    <!-- Main Content Area -->
    <TransporteManager />
  </div>
</template>

<script setup>
import TransporteManager from './components/TransporteManager.vue'
</script>
