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
    },
    getDependencies(id) {
        return api.get('/bypass/check_rubro_deps', { params: { rubro_id: id } });
    },
    migrateAndDelete(id, data) {
        return api.post(`/productos/rubros/${id}/migrate_and_delete`, data);
    },
    bulkMove(data) {
        return api.post('/productos/rubros/bulk_move', data);
    }
};
