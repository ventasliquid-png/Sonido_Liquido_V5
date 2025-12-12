import api from './api';

export default {
    /**
     * Crea un pedido táctico y descarga el Excel generado.
     * @param {Object} pedidoData Payload del pedido
     * @returns {Promise<Blob>} Archivo Excel binario
     */
    async createTactico(pedidoData) {
        const response = await api.post('/pedidos/tactico', pedidoData, {
            responseType: 'blob' // Importante para descargar archivos
        });
        return response.data; // Retorna el Blob
    }
};
