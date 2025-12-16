import api from './api';

export default {
    /**
     * Crea un pedido táctico y descarga el Excel generado.
     * @param {Object} pedidoData Payload del pedido
     * @returns {Promise<Blob>} Archivo Excel binario
     */
    async createTactico(pedidoData) {
        const response = await api.post('/pedidos/tactico', pedidoData);
        return response.data;
    },

    async getAll(params = {}) {
        const response = await api.get('/pedidos/', { params });
        return response.data;
    },

    async update(id, data) {
        const response = await api.patch(`/pedidos/${id}`, data);
        return response.data;
    },

    async clone(id) {
        const response = await api.post(`/pedidos/${id}/clone`);
        return response.data;
    },

    async addItem(id, itemData) {
        const response = await api.post(`/pedidos/${id}/items`, itemData);
        return response.data;
    },

    async deleteItem(itemId) {
        await api.delete(`/pedidos/items/${itemId}`);
    }
};
