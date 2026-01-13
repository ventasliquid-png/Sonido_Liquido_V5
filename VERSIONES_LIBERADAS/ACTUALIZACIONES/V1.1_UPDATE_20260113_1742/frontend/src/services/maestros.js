import api from './api';

export default {
    // --- Read Only ---
    getCondicionesIva() {
        return api.get('/maestros/condiciones-iva');
    },
    createCondicionIva(data) {
        return api.post('/maestros/condiciones-iva', data);
    },
    updateCondicionIva(id, data) {
        return api.put(`/maestros/condiciones-iva/${id}`, data);
    },
    deleteCondicionIva(id) {
        return api.delete(`/maestros/condiciones-iva/${id}`);
    },
    getCondicionIvaUsage(id) {
        return api.get(`/maestros/condiciones-iva/${id}/usage`);
    },
    replaceCondicionIva(id, targetId) {
        return api.post(`/maestros/condiciones-iva/${id}/replace`, { target_id: targetId });
    },
    getProvincias() {
        return api.get('/maestros/provincias');
    },
    createProvincia(data) {
        return api.post('/maestros/provincias', data);
    },
    updateProvincia(id, data) {
        return api.put(`/maestros/provincias/${id}`, data);
    },
    deleteProvincia(id) {
        return api.delete(`/maestros/provincias/${id}`);
    },
    getTiposContacto() {
        return api.get('/maestros/tipos-contacto');
    },
    createTipoContacto(data) {
        return api.post('/maestros/tipos-contacto', data);
    },
    updateTipoContacto(id, data) {
        return api.put(`/maestros/tipos-contacto/${id}`, data);
    },
    deleteTipoContacto(id) {
        return api.delete(`/maestros/tipos-contacto/${id}`);
    },

    // --- Listas de Precios ---
    getListasPrecios(params = {}) {
        return api.get('/maestros/listas-precios', { params });
    },
    createListaPrecios(data) {
        return api.post('/maestros/listas-precios', data);
    },
    updateListaPrecios(id, data) {
        return api.put(`/maestros/listas-precios/${id}`, data);
    },

    // --- Segmentos ---
    getSegmentos(params = {}) {
        return api.get('/maestros/segmentos', { params });
    },
    createSegmento(data) {
        return api.post('/maestros/segmentos', data);
    },
    updateSegmento(id, data) {
        return api.put(`/maestros/segmentos/${id}`, data);
    },
    deleteSegmento(id) {
        return api.delete(`/maestros/segmentos/${id}`);
    },

    // --- Vendedores ---
    getVendedores(params = {}) {
        return api.get('/maestros/vendedores', { params });
    },
    createVendedor(data) {
        return api.post('/maestros/vendedores', data);
    },
    updateVendedor(id, data) {
        return api.put(`/maestros/vendedores/${id}`, data);
    },

    // --- Transportes (Logística) ---
    getTransportes(params = {}) {
        return api.get('/logistica/empresas', { params });
    },
    createTransporte(data) {
        return api.post('/logistica/empresas', data);
    },
    updateTransporte(id, data) {
        return api.put(`/logistica/empresas/${id}`, data);
    },

    // --- Industrial ---
    getTasasIva() {
        return api.get('/maestros/tasas-iva');
    },
    getUnidades() {
        return api.get('/maestros/unidades');
    }
};
