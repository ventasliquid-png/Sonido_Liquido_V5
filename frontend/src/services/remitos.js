import api from './api';

export default {
    /**
     * Crea un nuevo remito (Cabecera)
     * @param {Object} data { pedido_id, domicilio_entrega_id, transporte_id, items: [], ... }
     */
    createRemito(data) {
        return api.post('/remitos/', data);
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
     */
    despacharRemito(remitoId) {
        return api.post(`/remitos/${remitoId}/despachar`);
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
    }
};
