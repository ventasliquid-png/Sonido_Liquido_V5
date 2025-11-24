import api from './api';

export default {
    getAll(params) {
        return api.get('/clientes/', { params });
    },
    getById(id) {
        return api.get(`/clientes/${id}`);
    },
    create(data) {
        return api.post('/clientes/', data);
    },
    update(id, data) {
        return api.put(`/clientes/${id}`, data);
    },
    delete(id) {
        return api.delete(`/clientes/${id}`);
    },
    // Sub-recursos
    createDomicilio(clienteId, data) {
        return api.post(`/clientes/${clienteId}/domicilios`, data);
    },
    updateDomicilio(clienteId, domicilioId, data) {
        return api.put(`/clientes/${clienteId}/domicilios/${domicilioId}`, data);
    },
    deleteDomicilio(clienteId, domicilioId) {
        return api.delete(`/clientes/${clienteId}/domicilios/${domicilioId}`);
    },
    createVinculo(clienteId, data) {
        return api.post(`/clientes/${clienteId}/vinculos`, data);
    },
    deleteVinculo(clienteId, vinculoId) {
        return api.delete(`/clientes/${clienteId}/vinculos/${vinculoId}`);
    }
};
