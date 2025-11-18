<script setup>
// 1. Eliminamos AteneaChat (temporalmente)
// import AteneaChat from './views/AteneaChat.vue'

// 2. Importamos el componente de Rubros
import Rubros from './views/Rubros.vue'
</script>

<template>
  <main class="app-container">
    <!-- 3. Mostramos el componente de Rubros -->
    <Rubros />
    
    <!-- <AteneaChat /> -->
  </main>
</template>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding-top: 2rem;
}
</style>