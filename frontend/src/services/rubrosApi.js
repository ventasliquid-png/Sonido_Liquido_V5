import api from './api';

export default {
    getAll() {
        return api.get('/rubros/rubros');
    },
    create(data) {
        return api.post('/rubros/rubros', data);
    },
    update(id, data) {
        return api.put(`/rubros/rubros/${id}`, data);
    },
    delete(id) {
        return api.delete(`/rubros/rubros/${id}`);
    }
};
