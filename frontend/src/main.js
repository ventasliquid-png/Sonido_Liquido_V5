import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importar Pinia
import App from './App.vue'

// (Nota: Asumimos que 'router' aún no está implementado, se omite 'import router' por ahora)
import router from './router'

// Importar el CSS principal (Doctrina Cromática)
import './styles/main.scss'
import '@fortawesome/fontawesome-free/css/all.css'
import { excelDirective } from './directives/v-excel'

const app = createApp(App)

app.use(createPinia()) // Usar Pinia
app.use(router) // Usar Router
app.directive('excel', excelDirective) // [GY-UX] Calculadora Caliente

app.mount('#app')
