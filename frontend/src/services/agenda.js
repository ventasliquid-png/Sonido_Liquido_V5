import api from './api';

export default {
    getPersonas(params = {}) {
        return api.get('/agenda/personas', { params });
    },
    searchPersonas(query) {
        return api.get('/agenda/personas/search', { params: { q: query } });
    },
    getPersona(id) {
        return api.get(`/agenda/personas/${id}`);
    },
    createPersona(data) {
        return api.post('/agenda/personas', data);
    },
    updatePersona(id, data) {
        return api.put(`/agenda/personas/${id}`, data);
    }
};
