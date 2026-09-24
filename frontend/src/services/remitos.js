// [IDENTIDAD] - frontend\src\services\remitos.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import api from './api';

export default {

    /**
     * Lista todos los remitos del sistema
     */
    getRemitos() {
        return api.get('/remitos/');
    },

    /**
     * Obtiene los remitos asociados a un pedido
     * @param {Number} pedidoId 
     */
    getRemitosByPedido(pedidoId) {
        // Backend doesn't have this specific endpoint yet, but maybe we filter by generic get?
        // Or we should add it.
        // For now, let's assume we might need to add `GET /remitos?pedido_id=X` 
        // to backend routers/remitos.py OR `GET /pedidos/{id}/remitos`
        // I'll stick to a query param or separate endpoint.
        // Let's implement generic get on backend first? 
        // Actually, for now let's try to get them via a specific endpoint I will add or existing structure.
        // I missed adding `GET /remitos/por_pedido/{id}`. 
        // I will add it to the service assuming I'll fix backend in a moment.
        return api.get(`/remitos/por_pedido/${pedidoId}`);
    },

    /**
     * Despacha un remito (Cambio de estado y stock físico)
     * @param {String} remitoId UUID
     * @param {Number|null} bultos Opcional -- [Etapa 3] si no se manda, conserva el valor que ya tenía
     */
    despacharRemito(remitoId, bultos = null) {
        return api.post(`/remitos/${remitoId}/despachar`, { bultos });
    },

    /**
     * Obtiene detalle de un remito
     * @param {String} remitoId 
     */
    getRemito(remitoId) {
        return api.get(`/remitos/${remitoId}`);
    },

    /**
     * Agrega items a un remito existente
     * @param {String} remitoId 
     * @param {Object} itemData { pedido_item_id, cantidad }
     */
    addItem(remitoId, itemData) {
        return api.post(`/remitos/${remitoId}/items`, itemData);
    },

    uploadInvoice(formData) {
        return api.post('/remitos/ingesta-pdf', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    confirmIngesta(rawId, payload) {
        return api.post(`/ingesta/raw/${rawId}/approve`, payload);
    },

    updateRemito(remitoId, data) {
        return api.patch(`/remitos/${remitoId}`, data);
    }
};
