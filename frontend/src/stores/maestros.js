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
        transportes: [],
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
                    this.fetchTiposContacto(),
                    this.fetchTransportes()
                ]);
            } catch (error) {
                this.error = error;
            } finally {
                this.loading = false;
            }
        },

        // --- Segmentos ---
        async fetchSegmentos(filter = 'active', force = false) {
            // Cache check
            if (!force && this.segmentos.length > 0 && filter === 'active') {
                return;
            }
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
        async deleteSegmento(id) {
            try {
                await maestrosService.deleteSegmento(id);
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
        async createProvincia(data) {
            try {
                await maestrosService.createProvincia(data);
                await this.fetchProvincias();
            } catch (error) {
                throw error;
            }
        },
        async updateProvincia(id, data) {
            try {
                await maestrosService.updateProvincia(id, data);
                await this.fetchProvincias();
            } catch (error) {
                throw error;
            }
        },
        async deleteProvincia(id) {
            try {
                await maestrosService.deleteProvincia(id);
                await this.fetchProvincias();
            } catch (error) {
                throw error;
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
        async createCondicionIva(data) {
            try {
                const res = await maestrosService.createCondicionIva(data);
                await this.fetchCondicionesIva();
                return res.data;
            } catch (error) {
                throw error;
            }
        },
        async updateCondicionIva(id, data) {
            try {
                await maestrosService.updateCondicionIva(id, data);
                await this.fetchCondicionesIva();
            } catch (error) {
                throw error;
            }
        },
        async deleteCondicionIva(id) {
            try {
                await maestrosService.deleteCondicionIva(id);
                await this.fetchCondicionesIva();
            } catch (error) {
                throw error;
            }
        },
        async fetchTiposContacto() {
            try {
                const response = await maestrosService.getTiposContacto();
                this.tiposContacto = response.data;
            } catch (error) {
                console.error('Error fetching tipos contacto:', error);
            }
        },
        async createTipoContacto(data) {
            try {
                await maestrosService.createTipoContacto(data);
                await this.fetchTiposContacto();
            } catch (error) {
                throw error;
            }
        },
        async updateTipoContacto(id, data) {
            try {
                await maestrosService.updateTipoContacto(id, data);
                await this.fetchTiposContacto();
            } catch (error) {
                throw error;
            }
        },
        async deleteTipoContacto(id) {
            try {
                await maestrosService.deleteTipoContacto(id);
                await this.fetchTiposContacto();
            } catch (error) {
                throw error;
            }
        },

        // --- Transportes ---
        async fetchTransportes(filter = 'active') {
            try {
                const response = await maestrosService.getTransportes({ status: filter });
                this.transportes = response.data;
            } catch (error) {
                console.error('Error fetching transportes:', error);
            }
        },
        async createTransporte(data) {
            try {
                await maestrosService.createTransporte(data);
                await this.fetchTransportes();
            } catch (error) {
                throw error;
            }
        },
        async updateTransporte(id, data) {
            try {
                await maestrosService.updateTransporte(id, data);
                await this.fetchTransportes();
            } catch (error) {
                throw error;
            }
        }
    }
});
