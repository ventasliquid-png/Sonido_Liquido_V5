// [IDENTIDAD] - frontend\src\services\agenda.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import api from './api';

export default {
    getPersonas(params = {}) {
        return api.get('/contactos', { params });
    },
    searchPersonas(query) {
        return api.get('/contactos', { params: { q: query } });
    },
    getPersona(id) {
        return api.get(`/contactos/${id}`);
    },
    createPersona(data) {
        return api.post('/contactos', data);
    },
    updatePersona(id, data) {
        return api.put(`/contactos/${id}`, data);
    }
};
