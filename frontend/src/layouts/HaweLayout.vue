<template>
  <div class="bridge-layout-container">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
onMounted(() => {
  console.log('HaweLayout mounted');
});
</script>

<style>
/* Reset global styles specifically for this layout tree if needed */
.bridge-layout-container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #0a0a0a; /* Ensure dark background */
}
</style>
