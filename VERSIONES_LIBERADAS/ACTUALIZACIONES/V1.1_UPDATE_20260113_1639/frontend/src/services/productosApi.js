import api from './api';

export default {
    getAll(params = {}) {
        return api.get('/productos/', { params });
    },
    getById(id) {
        return api.get(`/productos/${id}`);
    },
    create(data) {
        return api.post('/productos/', data);
    },
    update(id, data) {
        return api.put(`/productos/${id}`, data);
    },
    toggleActive(id) {
        return api.post(`/productos/${id}/toggle`);
    },
    hardDelete(id) {
        return api.delete(`/productos/${id}/hard`);
    }
};
