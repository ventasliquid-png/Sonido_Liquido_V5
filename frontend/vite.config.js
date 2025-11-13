import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue' // La clave es que el archivo existe

// [V5.22: Sintaxis Estándar, Mínima]
export default defineConfig({
  plugins: [vue()], // Usamos la función de Vue directamente
  server: {
    host: '0.0.0.0',
    port: 5173,
  }
})