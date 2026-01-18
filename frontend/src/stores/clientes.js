import { defineStore } from 'pinia';
import clientesService from '../services/clientes';

export const useClientesStore = defineStore('clientes', {
    state: () => ({
        clientes: [],
        topClients: [],
        loading: false,
        error: null,
        total: 0
    }),

    actions: {
        async fetchClientes(params = {}) {
            this.loading = true;
            try {
                // Pass params (like { q: 'Bio' }) to the service
                const response = await clientesService.getAll(params);
                if (Array.isArray(response.data)) {
                    this.clientes = response.data;
                } else {
                    console.error("API Error: Expected Array but got", typeof response.data, response.data);
                    // [GY-FIX] Prevent App Crash if API returns HTML (Index.html)
                    this.clientes = [];
                }
            } catch (error) {
                this.error = error;
                console.error('Error fetching clientes:', error);
            } finally {
                this.loading = false;
            }
        },

        async fetchClienteById(id) {
            try {
                const response = await clientesService.getById(id);
                // Update local list cache to ensure Grid/List view is fresh
                const index = this.clientes.findIndex(c => c.id === id);
                if (index !== -1) {
                    this.clientes[index] = response.data;
                }
                return response.data;
            } catch (error) {
                console.error(`Error fetching cliente ${id}:`, error);
                throw error;
            }
        },

        async getTransportesHabituales(id) {
            try {
                const response = await clientesService.getTransportesHabituales(id);
                return response.data;
            } catch (error) {
                console.error(`Error fetching transportes habituales for ${id}:`, error);
                return [];
            }
        },

        async createCliente(data) {
            try {
                const response = await clientesService.create(data);
                this.clientes.push(response.data);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async updateCliente(id, data) {
            try {
                const response = await clientesService.update(id, data);
                // [GY-FIX] Use splice to guarantee Reactivity in Vue 3/Pinia for Array updates
                // Direct assignment (this.clientes[index] = ...) sometimes fails to trigger deep watchers
                const index = this.clientes.findIndex(c => c.id === id);
                if (index !== -1) {
                    this.clientes.splice(index, 1, response.data);
                }
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async deleteCliente(id) {
            try {
                await clientesService.delete(id);
                // Assuming soft delete just changes status, re-fetch or manual update?
                // Usually re-fetch or set active=false locally
                const index = this.clientes.findIndex(c => c.id === id);
                if (index !== -1) {
                    // clone to ensure reactivity
                    const updated = { ...this.clientes[index], activo: false };
                    this.clientes.splice(index, 1, updated);
                }
            } catch (error) {
                throw error;
            }
        },

        async hardDeleteCliente(id) {
            try {
                await clientesService.hardDelete(id);
                this.clientes = this.clientes.filter(c => c.id !== id);
            } catch (error) {
                throw error;
            }
        },

        // Check CUIT (Multi-sede V5)
        async checkCuit(cuit, excludeId = null) {
            try {
                const res = await clientesService.checkCuit(cuit, excludeId);
                return res.data;
            } catch (error) {
                console.error("Error Checking CUIT", error);
                return { status: 'ERROR', existing_clients: [] };
            }
        },

        // Domicilios
        async createDomicilio(clienteId, data) {
            try {
                const response = await clientesService.createDomicilio(clienteId, data);
                // [GY-FIX] Update local cache to reflect changes immediately in UI
                const index = this.clientes.findIndex(c => c.id === clienteId);
                if (index !== -1) {
                    this.clientes.splice(index, 1, response.data);
                }
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async updateDomicilio(clienteId, domicilioId, data) {
            try {
                const response = await clientesService.updateDomicilio(clienteId, domicilioId, data);
                // [GY-FIX] Update local cache to reflect changes immediately in UI
                const index = this.clientes.findIndex(c => c.id === clienteId);
                if (index !== -1) {
                    this.clientes.splice(index, 1, response.data);
                }
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async deleteDomicilio(clienteId, domicilioId) {
            try {
                await clientesService.deleteDomicilio(clienteId, domicilioId);
                // [GY-FIX] Refetch client to ensure state consistency (Backend returns 204)
                await this.fetchClienteById(clienteId);
            } catch (error) {
                throw error;
            }
        },

        // Vinculos
        async createVinculo(clienteId, data) {
            try {
                const response = await clientesService.createVinculo(clienteId, data);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async updateVinculo(clienteId, vinculoId, data) {
            try {
                const response = await clientesService.updateVinculo(clienteId, vinculoId, data);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async deleteVinculo(clienteId, vinculoId) {
            try {
                await clientesService.deleteVinculo(clienteId, vinculoId);
            } catch (error) {
                throw error;
            }
        },

        // Top Clients
        async fetchTopClients() {
            try {
                const response = await clientesService.getTopClients();
                this.topClients = response.data;
            } catch (error) {
                console.error(error);
            }
        },

        async incrementUsage(id) {
            try {
                await clientesService.incrementUsage(id);
                // Locally update?
                const c = this.clientes.find(cli => cli.id === id);
                if (c) {
                    c.contador_uso = (c.contador_uso || 0) + 1;
                }
            } catch (error) {
                console.error(error);
            }
        }
    }
});
