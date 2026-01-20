import { createRouter, createWebHistory } from 'vue-router';
import SegmentoList from '../views/Maestros/SegmentoList.vue';
import VendedorList from '../views/Maestros/VendedorList.vue';
import ListaPreciosList from '../views/Maestros/ListaPreciosList.vue';
import Login from '../views/Login.vue';
import HaweLayout from '../layouts/HaweLayout.vue';
import DataCleaner from '../views/DataIntel/DataCleaner.vue';
import HaweView from '../views/HaweView.vue';

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
        redirect: '/hawe'
    },


    {
        path: '/agenda',
        name: 'Agenda',
        component: () => import('../views/Agenda/PersonaList.vue')
    },
    {
        path: '/agenda/contactos',
        name: 'Contactos',
        component: () => import('../views/Agenda/ContactosView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/hawe',
        component: HaweLayout,
        children: [
            {
                path: '',
                name: 'HaweHome',
                component: HaweView
            },
            {
                path: 'cliente/:id',
                name: 'HaweClientCanvas',
                component: () => import('../views/Hawe/ClientCanvas.vue'),
                props: true
            },
            {
                path: 'segmentos',
                name: 'Segmentos',
                component: SegmentoList
            },
            {
                path: 'productos',
                name: 'Productos',
                component: () => import('../views/Hawe/ProductosView.vue')
            },
            {
                path: 'rubros',
                name: 'Rubros',
                component: () => import('../views/Maestros/RubrosView.vue')
            },
            {
                path: 'pedidos',
                name: 'PedidoList',
                component: () => import('../views/Pedidos/PedidoList.vue')
            },
            {
                path: 'tactico-legacy',
                name: 'TacticalLoaderLegacy',
                component: () => import('../views/Ventas/GridLoader.vue')
            },
            {
                path: 'cantera',
                name: 'CanteraExplorer',
                component: () => import('../views/Maestros/CanteraExplorer.vue')
            },
            {
                path: 'transportes',
                name: 'Transportes',
                component: () => import('../views/Hawe/components/TransporteManager.vue')
            },
            {
                path: 'intel/cleaner',
                name: 'data-cleaner',
                component: DataCleaner
            },
            {
                path: 'listas-precios',
                name: 'ListasPrecios',
                component: ListaPreciosList
            },
            {
                path: 'vendedores',
                name: 'Vendedores',
                component: VendedorList
            },
            {
                path: 'pedidos/nuevo',
                name: 'PedidoCanvas',
                component: () => import('../views/Ventas/PedidoCanvas.vue')
            },
            {
                path: 'pedidos/editar/:id',
                name: 'PedidoEditar',
                component: () => import('../views/Ventas/PedidoCanvas.vue')
            }
        ]
    },

    {
        path: '/:pathMatch(.*)*',
        redirect: '/hawe'
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
