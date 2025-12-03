import api from './api';

export default {
    getAll() {
        return api.get('/productos/rubros');
    },
    create(data) {
        return api.post('/productos/rubros', data);
    },
    update(id, data) {
        return api.put(`/productos/rubros/${id}`, data);
    },
    delete(id) {
        return api.delete(`/productos/rubros/${id}`);
    }
};
