import { defineStore } from 'pinia';
import maestrosService from '../services/maestros';

export const useMaestrosStore = defineStore('maestros', {
    state: () => ({
        segmentos: [],
        vendedores: [],
        listasPrecios: [],
        provincias: [],
        condicionesIva: [],
        tiposContacto: [],
        loading: false,
        error: null
    }),

    actions: {
        async fetchAll() {
            this.loading = true;
            try {
                await Promise.all([
                    this.fetchSegmentos(),
                    this.fetchVendedores(),
                    this.fetchListasPrecios(),
                    this.fetchProvincias(),
                    this.fetchCondicionesIva(),
                    this.fetchTiposContacto()
                ]);
            } catch (error) {
                this.error = error;
            } finally {
                this.loading = false;
            }
        },

        // --- Segmentos ---
        async fetchSegmentos(filter = 'active') {
            try {
                const response = await maestrosService.getSegmentos({ status: filter });
                this.segmentos = response.data;
            } catch (error) {
                console.error('Error fetching segmentos:', error);
            }
        },
        async createSegmento(data) {
            try {
                await maestrosService.createSegmento(data);
                await this.fetchSegmentos();
            } catch (error) {
                throw error;
            }
        },
        async updateSegmento(id, data) {
            try {
                await maestrosService.updateSegmento(id, data);
                await this.fetchSegmentos();
            } catch (error) {
                throw error;
            }
        },

        // --- Vendedores ---
        async fetchVendedores(filter = 'active') {
            try {
                const response = await maestrosService.getVendedores({ status: filter });
                this.vendedores = response.data;
            } catch (error) {
                console.error('Error fetching vendedores:', error);
            }
        },
        async createVendedor(data) {
            try {
                await maestrosService.createVendedor(data);
                await this.fetchVendedores();
            } catch (error) {
                throw error;
            }
        },
        async updateVendedor(id, data) {
            try {
                await maestrosService.updateVendedor(id, data);
                await this.fetchVendedores();
            } catch (error) {
                throw error;
            }
        },

        // --- Listas de Precios ---
        async fetchListasPrecios(filter = 'active') {
            try {
                const response = await maestrosService.getListasPrecios({ status: filter });
                this.listasPrecios = response.data;
            } catch (error) {
                console.error('Error fetching listas precios:', error);
            }
        },
        async createListaPrecios(data) {
            try {
                await maestrosService.createListaPrecios(data);
                await this.fetchListasPrecios();
            } catch (error) {
                throw error;
            }
        },
        async updateListaPrecios(id, data) {
            try {
                await maestrosService.updateListaPrecios(id, data);
                await this.fetchListasPrecios();
            } catch (error) {
                throw error;
            }
        },

        // --- Read Only ---
        async fetchProvincias() {
            try {
                const response = await maestrosService.getProvincias();
                this.provincias = response.data;
            } catch (error) {
                console.error('Error fetching provincias:', error);
            }
        },
        async fetchCondicionesIva() {
            try {
                const response = await maestrosService.getCondicionesIva();
                this.condicionesIva = response.data;
            } catch (error) {
                console.error('Error fetching condiciones iva:', error);
            }
        },
        async fetchTiposContacto() {
            try {
                const response = await maestrosService.getTiposContacto();
                this.tiposContacto = response.data;
            } catch (error) {
                console.error('Error fetching tipos contacto:', error);
            }
        }
    }
});
