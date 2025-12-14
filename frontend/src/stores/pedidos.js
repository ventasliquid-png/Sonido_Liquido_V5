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

        async createPedidoTactico(pedidoData) {
            this.isLoading = true;
            try {
                // The backend returns a BLOB (Excel file)
                const response = await apiClient.post('/pedidos/tactico', pedidoData, {
                    responseType: 'blob'
                });

                // Trigger Download
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'Pedido_Nuevo.xlsx'); // Fallback name

                // Try to get filename from header
                const contentDisposition = response.headers['content-disposition'];
                if (contentDisposition) {
                    const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (fileNameMatch && fileNameMatch.length === 2) {
                        link.setAttribute('download', fileNameMatch[1]);
                    }
                }

                document.body.appendChild(link);
                link.click();
                link.remove();

                return true;

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
