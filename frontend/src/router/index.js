import { createRouter, createWebHistory } from 'vue-router';
import ClienteList from '../views/Clientes/ClienteList.vue';
import TransporteList from '../views/Logistica/TransporteList.vue';
import SegmentoList from '../views/Maestros/SegmentoList.vue';
import VendedorList from '../views/Maestros/VendedorList.vue';
import ListaPreciosList from '../views/Maestros/ListaPreciosList.vue';
import Login from '../views/Login.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { public: true }
    },
    {
        path: '/',
        name: 'Home',
        redirect: '/clientes'
    },
    {
        path: '/clientes',
        name: 'Clientes',
        component: ClienteList
    },
    {
        path: '/transportes',
        name: 'Transportes',
        component: TransporteList
    },
    {
        path: '/segmentos',
        name: 'Segmentos',
        component: SegmentoList
    },
    {
        path: '/vendedores',
        name: 'Vendedores',
        component: VendedorList
    },
    {
        path: '/listas-precios',
        name: 'ListasPrecios',
        component: ListaPreciosList
    },
    {
        path: '/agenda',
        name: 'Agenda',
        component: () => import('../views/Agenda/PersonaList.vue')
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    if (!to.meta.public && !token) {
        next('/login');
    } else {
        next();
    }
});

export default router;
