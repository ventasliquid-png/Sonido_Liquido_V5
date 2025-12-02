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
        // Asumiendo que el endpoint DELETE hace Soft Delete (toggle activo)
        return api.delete(`/productos/${id}`);
    }
};
