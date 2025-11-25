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
    getListasPrecios() {
        return api.get('/maestros/listas-precios');
    },
    createListaPrecios(data) {
        return api.post('/maestros/listas-precios', data);
    },
    updateListaPrecios(id, data) {
        return api.put(`/maestros/listas-precios/${id}`, data);
    },

    // --- Ramos ---
    getRamos() {
        return api.get('/maestros/ramos');
    },
    createRamo(data) {
        return api.post('/maestros/ramos', data);
    },
    updateRamo(id, data) {
        return api.put(`/maestros/ramos/${id}`, data);
    },

    // --- Vendedores ---
    getVendedores() {
        return api.get('/maestros/vendedores');
    },
    createVendedor(data) {
        return api.post('/maestros/vendedores', data);
    },
    updateVendedor(id, data) {
        return api.put(`/maestros/vendedores/${id}`, data);
    }
};
