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

    // Bridge RAR-V5 (ARCA)
    checkAfip: (cuit) => api.get(`/clientes/afip/${cuit}`),

    // Domicilios
    createDomicilio: (clienteId, data) => api.post(`/clientes/${clienteId}/domicilios`, data),
    updateDomicilio: (clienteId, domicilioId, data) => api.put(`/clientes/${clienteId}/domicilios/${domicilioId}`, data),
    deleteDomicilio: (clienteId, domicilioId) => api.delete(`/clientes/${clienteId}/domicilios/${domicilioId}`),

    // Vinculos (Redirected to Agenda API V5)
    createVinculo(clienteId, data) {
        // Data usually comes with client_id, but we ensure it matches
        const payload = { ...data, cliente_id: clienteId };
        return api.post(`/agenda/vinculos`, payload);
    },
    updateVinculo(clienteId, vinculoId, data) {
        // Standard Agenda Endpoint
        return api.put(`/agenda/vinculos/${vinculoId}`, data);
    },
    deleteVinculo(clienteId, vinculoId) {
        return api.delete(`/agenda/vinculos/${vinculoId}`);
    },

    // Usage Ranking (V5.2)
    getTopClients: () => api.get('/clientes/top'),
    incrementUsage: (id) => api.post(`/clientes/${id}/interaction`)
};
