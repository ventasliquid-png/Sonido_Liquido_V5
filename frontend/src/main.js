import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importar Pinia
import App from './App.vue'

// (Nota: Asumimos que 'router' aún no está implementado, se omite 'import router' por ahora)
// import router from './router'

// Importar el CSS principal (Doctrina Cromática)
import './styles/main.scss'

const app = createApp(App)

app.use(createPinia()) // Usar Pinia
// app.use(router) // (Línea deshabilitada hasta que se implemente el router)

app.mount('#app')
