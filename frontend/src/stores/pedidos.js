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

        // [GY-MOD] Removed download logic. Now returns JSON.
        async createPedidoTactico(pedidoData) {
            this.isLoading = true;
            try {
                // Return JSON { id, message, ... }
                const response = await apiClient.post('/pedidos/tactico', pedidoData);

                // Return the data so component can show Success Toast
                return response.data;

            } catch (error) {
                console.error("Error creating tactico order:", error);
                throw error;
            } finally {
                this.isLoading = false;
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

        async getHistorialCliente(clienteId) {
            try {
                const res = await apiClient.get(`/pedidos/historial/${clienteId}`);
                return res.data;
            } catch (error) {
                return [];
            }
        }
    }
});
