<template>
  <div v-if="appEnv" class="dev-badge-container">
    <div class="dev-badge" :class="appEnv">
      MODO {{ appEnv === 'desarrollo' ? 'DESARROLLO [D]' : 'PRODUCCION [P]' }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
const appEnv = computed(() => import.meta.env.VITE_APP_ENV || null);
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
.dev-badge.desarrollo { background: #ff8c00; }
.dev-badge.produccion { background: #7c3aed; }
</style>
