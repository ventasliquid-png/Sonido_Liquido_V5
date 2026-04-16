<template>
  <div v-if="isDev" class="dev-badge-container">
    <div class="dev-badge">
      MODO DESARROLLO [D]
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const isDev = computed(() => {
  // Se muestra si el host es localhost o si la versión indica desarrollo
  return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
});
</script>

<style scoped>
.dev-badge-container {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 10000;
  pointer-events: none;
}

.dev-badge {
  background: #ff8c00; /* Naranja fuerte */
  color: white;
  text-align: center;
  font-weight: bold;
  font-size: 9px;
  padding: 2px 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255,255,255,0.3);
  pointer-events: auto;
}
</style>
