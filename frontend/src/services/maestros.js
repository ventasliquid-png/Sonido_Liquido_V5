import api from './api';

export default {
    getCondicionesIva() {
        return api.get('/maestros/condiciones-iva');
    },
    getProvincias() {
        return api.get('/maestros/provincias');
    },
    getListasPrecios() {
        return api.get('/maestros/listas-precios');
    }
};
