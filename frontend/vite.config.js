import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Importar 'path' de Node

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],

  // --- [INICIO PARCHE V10.E (Filtrado de Ruido)] ---
  server: {
    watch: {
      // Ignorar directorios que generan "ruido" en la consola
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**',

        // Ignorar explícitamente las carpetas de AppData que causan ruido.
        // Usamos path.resolve para crear una ruta absoluta que el watcher entienda.
        path.resolve("C:/Users/USUARIO/AppData/Local/Microsoft/Edge/**"),
        path.resolve("C:/Users/USUARIO/AppData/Local/Google/Chrome/**")
      ],
    },
  },
  // --- [FIN PARCHE V10.E] ---

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})