import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const usePedidosStore = defineStore('pedidos', {
    state: () => ({
        isLoading: false,
        pedidos: [] // List for Dashboard
    }),

    actions: {
        async fetchPedidos(filters = {}) {
            this.isLoading = true;
            try {
                // filters: { estado: 'PENDIENTE', limit: 50, ... }
                const params = new URLSearchParams(filters);
                const res = await apiClient.get(`/pedidos/?${params.toString()}`);
                this.pedidos = res.data;
            } catch (error) {
                console.error("Error fetching pedidos:", error);
            } finally {
                this.isLoading = false;
            }
        },

        async getPedidoById(id) {
            try {
                const res = await apiClient.get(`/pedidos/${id}`);
                return res.data;
            } catch (error) {
                console.error("Error fetching pedido:", error);
                throw error;
            }
        },

        // [GY-MOD] Removed download logic. Now returns JSON.
        async createPedidoTactico(pedidoData) {
            this.isLoading = true;
            try {
                const response = await apiClient.post('/pedidos/tactico', pedidoData);
                return response.data;
            } catch (error) {
                console.error("Error creating tactico order:", error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async downloadExcel(pedidoId, filename = 'pedido.xlsx') {
            try {
                const response = await apiClient.get(`/pedidos/${pedidoId}/excel`, {
                    responseType: 'blob'
                });
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
            } catch (error) {
                console.error("Error downloading excel:", error);
                throw error;
            }
        },

        async getLastPrice(clienteId, productoId) {
            try {
                const res = await apiClient.get(`/pedidos/historial/${clienteId}/${productoId}`);
                return res.data; // { precio, fecha, ... } or null
            } catch (error) {
                return null;
            }
        },



        async updatePedido(id, data) {
            try {
                const res = await apiClient.patch(`/pedidos/${id}`, data);
                // Update local list
                const index = this.pedidos.findIndex(p => p.id === id);
                if (index !== -1) {
                    // Update object but keep reactivity structure if needed, or replace.
                    // Merging data from response (which is the full object) is safest.
                    this.pedidos[index] = res.data;
                }
                return res.data;
            } catch (error) {
                console.error("Error updating pedido:", error);
                throw error;
            }
        },

        async clonePedido(id) {
            try {
                const res = await apiClient.post(`/pedidos/${id}/clone`);
                // Add to beginning of list
                this.pedidos.unshift(res.data);
                return res.data;
            } catch (error) {
                console.error("Error cloning pedido:", error);
                throw error;
            }
        },

        async addPedidoItem(pedidoId, itemData) {
            try {
                const res = await apiClient.post(`/pedidos/${pedidoId}/items`, itemData);
                const updatedPedido = res.data;
                // Update local list with the FULL updated pedido returned by backend
                // This is safer than manual splicing for complex additions
                const index = this.pedidos.findIndex(p => p.id === pedidoId);
                if (index !== -1) {
                    this.pedidos[index] = updatedPedido;
                }
                return updatedPedido;
            } catch (error) {
                console.error("Error adding pedido item:", error);
                throw error;
            }
        },

        async updatePedidoItem(pedidoId, itemId, data) {
            try {
                const res = await apiClient.patch(`/pedidos/items/${itemId}`, data);
                const updatedPedido = res.data;
                // Enable reactivity
                const index = this.pedidos.findIndex(p => p.id === pedidoId);
                if (index !== -1) {
                    this.pedidos[index] = updatedPedido;
                }
                return updatedPedido;
            } catch (error) {
                console.error("Error updating pedido item:", error);
                throw error;
            }
        },

        async deletePedidoItem(pedidoId, itemId) {
            try {
                await apiClient.delete(`/pedidos/items/${itemId}`);

                // Update local list manually to reflect change without full reload
                const pedido = this.pedidos.find(p => p.id === pedidoId);
                if (pedido) {
                    const itemIndex = pedido.items.findIndex(i => i.id === itemId);
                    if (itemIndex !== -1) {
                        const item = pedido.items[itemIndex];
                        pedido.items.splice(itemIndex, 1);
                        // Update total locally (approximate)
                        pedido.total -= (item.cantidad * item.precio_unitario);
                    }
                }
            } catch (error) {
                console.error("Error deleting pedido item:", error);
                throw error;
            }
        },

    },
    async fetchLastUsedTransport(clienteId) {
        try {
            const res = await apiClient.get(`/pedidos/ultimo-transporte/${clienteId}`);
            return res.data.transporte_id;
        } catch (error) {
            console.error("Error fetching last used transport:", error);
            return null;
        }
    }
}
});
