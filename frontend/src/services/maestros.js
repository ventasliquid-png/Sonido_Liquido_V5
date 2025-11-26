import api from './api';

export default {
    // --- Read Only ---
    getCondicionesIva() {
        return api.get('/maestros/condiciones-iva');
    },
    getProvincias() {
        return api.get('/maestros/provincias');
    },
    getTiposContacto() {
        return api.get('/maestros/tipos-contacto');
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

    // --- Vendedores ---
    getVendedores(params = {}) {
        return api.get('/maestros/vendedores', { params });
    },
    createVendedor(data) {
        return api.post('/maestros/vendedores', data);
    },
    updateVendedor(id, data) {
        return api.put(`/maestros/vendedores/${id}`, data);
    }
};
