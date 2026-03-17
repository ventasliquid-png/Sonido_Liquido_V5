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
      '/clientes': { target: 'http://localhost:8080', changeOrigin: true },
      '/productos': { target: 'http://localhost:8080', changeOrigin: true },
      '/pedidos': { target: 'http://localhost:8080', changeOrigin: true },
      '/maestros': { target: 'http://localhost:8080', changeOrigin: true },
      '/auth': { target: 'http://localhost:8080', changeOrigin: true },
      '/logistica': { target: 'http://localhost:8080', changeOrigin: true },
      '/agenda': { target: 'http://localhost:8080', changeOrigin: true },
      '/proveedores': { target: 'http://localhost:8080', changeOrigin: true },
      '/data_intel': { target: 'http://localhost:8080', changeOrigin: true },
      '/docs': { target: 'http://localhost:8080', changeOrigin: true },
      '/openapi.json': { target: 'http://localhost:8080', changeOrigin: true },
      '/remitos': { target: 'http://localhost:8080', changeOrigin: true },
      '/atenea': { target: 'http://localhost:8080', changeOrigin: true },
      '/cantera': { target: 'http://localhost:8080', changeOrigin: true },
      '/contactos': { target: 'http://localhost:8080', changeOrigin: true },
      '/bridge': { target: 'http://localhost:8080', changeOrigin: true },
      '/stats': { target: 'http://localhost:8080', changeOrigin: true },
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