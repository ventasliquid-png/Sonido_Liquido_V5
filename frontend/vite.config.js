import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Importar 'path' de Node

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],

  // --- [INICIO PARCHE V10.E (Filtrado de Ruido)] ---
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    hmr: {
      // Force the browser to use the current host instead of localhost for HMR
      // This is critical for LAN access from other PCs (like Tomy's).
      clientPort: 5173
    },
    proxy: {
      // [GY-LAN-ARCH] Proxy API requests to Backend running on localhost:8000
      // This solves CORS and LAN IP configuration issues permanently.
      '/clientes': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/productos': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/pedidos': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/maestros': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/auth': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/logistica': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/agenda': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/proveedores': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/data_intel': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/docs': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/openapi.json': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/remitos': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/atenea': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/cantera': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/contactos': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/bridge': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
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