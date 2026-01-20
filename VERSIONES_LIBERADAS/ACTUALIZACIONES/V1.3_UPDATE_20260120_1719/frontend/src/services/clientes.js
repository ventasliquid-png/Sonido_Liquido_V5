import api from './api';

export default {
    getAll: (params) => api.get('/clientes/', { params }),
    getById: (id) => api.get(`/clientes/${id}`),
    checkCuit: (cuit, excludeId = null) => {
        const params = {};
        if (excludeId) params.exclude_id = excludeId;
        return api.get(`/clientes/check-cuit/${cuit}`, { params });
    },
    getTransportesHabituales: (id) => api.get(`/clientes/${id}/transportes-habituales`),
    create: (data) => api.post('/clientes/', data),
    update: (id, data) => api.put(`/clientes/${id}`, data),
    delete: (id) => api.delete(`/clientes/${id}`),
    approve: (id) => api.put(`/clientes/${id}/aprobar`),
    hardDelete: (id) => api.delete(`/clientes/${id}/hard`),

    // Domicilios
    createDomicilio: (clienteId, data) => api.post(`/clientes/${clienteId}/domicilios`, data),
    updateDomicilio: (clienteId, domicilioId, data) => api.put(`/clientes/${clienteId}/domicilios/${domicilioId}`, data),
    deleteDomicilio: (clienteId, domicilioId) => api.delete(`/clientes/${clienteId}/domicilios/${domicilioId}`),

    // Vinculos
    createVinculo(clienteId, data) {
        return api.post(`/clientes/${clienteId}/vinculos`, data);
    },
    updateVinculo(clienteId, vinculoId, data) {
        return api.put(`/clientes/${clienteId}/vinculos/${vinculoId}`, data);
    },
    deleteVinculo(clienteId, vinculoId) {
        return api.delete(`/clientes/${clienteId}/vinculos/${vinculoId}`);
    },

    // Usage Ranking (V5.2)
    getTopClients: () => api.get('/clientes/top'),
    incrementUsage: (id) => api.post(`/clientes/${id}/interaction`)
};
