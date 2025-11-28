<template>
  <div
    class="ficha-card group relative flex flex-col overflow-hidden rounded-xl border border-white/10 bg-white/10 p-4 transition-all duration-300 hover:border-cyan-400/50 hover:bg-white/20 hover:shadow-lg hover:shadow-cyan-500/20 cursor-pointer"
    :class="{ 'ring-2 ring-cyan-400 bg-white/20': selected }"
  >
    <!-- Status Indicator -->
    <div
      v-if="status"
      class="absolute right-3 top-3 h-2 w-2 rounded-full shadow-[0_0_8px]"
      :class="{
        'bg-green-500 shadow-green-500': status === 'active',
        'bg-red-500 shadow-red-500': status === 'inactive',
        'bg-yellow-500 shadow-yellow-500': status === 'pending'
      }"
    ></div>

    <!-- Icon / Thumbnail -->
    <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-gray-800 text-2xl text-gray-400 group-hover:text-cyan-400 transition-colors">
      <slot name="icon">
        <i class="fas fa-cube"></i>
      </slot>
    </div>

    <!-- Content -->
    <div class="flex flex-col">
      <h3 class="font-outfit text-lg font-semibold text-gray-100 group-hover:text-white truncate">{{ title }}</h3>
      <p class="text-sm text-gray-500 font-mono truncate">{{ subtitle }}</p>
    </div>

    <!-- Hover Actions (Optional) -->
    <div class="absolute bottom-2 right-2 opacity-0 transition-opacity group-hover:opacity-100">
      <button class="text-gray-400 hover:text-white">
        <i class="fas fa-ellipsis-h"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: null // 'active', 'inactive', 'pending'
  },
  selected: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.ficha-card {
  backdrop-filter: blur(10px);
}
</style>
