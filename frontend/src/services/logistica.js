import api from './api';

export default {
    // Empresas
    getEmpresas: () => api.get('/logistica/empresas'),
    getEmpresaById: (id) => api.get(`/logistica/empresas/${id}`),
    createEmpresa: (data) => api.post('/logistica/empresas', data),
    updateEmpresa: (id, data) => api.put(`/logistica/empresas/${id}`, data),

    // Nodos
    getNodos: (empresaId = null) => {
        const params = {};
        if (empresaId) params.empresa_id = empresaId;
        return api.get('/logistica/nodos', { params });
    },
    createNodo: (data) => api.post('/logistica/nodos', data),
    updateNodo: (id, data) => api.put(`/logistica/nodos/${id}`, data)
};
