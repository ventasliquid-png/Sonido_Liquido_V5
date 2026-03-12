import api from './api';

export default {
    getAll(params) {
        return api.get('/proveedores/', { params });
    },
    create(data) {
        return api.post('/proveedores/', data);
    },
    update(id, data) {
        return api.put(`/proveedores/${id}`, data);
    },
    delete(id) {
        return api.delete(`/proveedores/${id}`);
    }
};
