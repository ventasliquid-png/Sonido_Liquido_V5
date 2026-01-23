import api from './api'

const canteraService = {
    searchClientes(query) {
        return api.get(`/bridge/clientes/search`, {
            params: { q: query }
        })
    },

    searchProductos(query) {
        return api.get(`/bridge/productos/search`, {
            params: { q: query }
        })
    },

    getClientes(limit = 100, offset = 0) {
        return api.get(`/bridge/clientes`, {
            params: { limit, offset }
        })
    },

    getProductos(limit = 100, offset = 0) {
        return api.get(`/bridge/productos`, {
            params: { limit, offset }
        })
    },

    importCliente(clienteId) {
        return api.post(`/bridge/clientes/${clienteId}/import`)
    },

    async importProducto(productoId) {
        const response = await api.post(`/bridge/productos/${productoId}/import`)
        return response.data
    },

    async getProductoDetails(productoId) {
        const response = await api.get(`/bridge/productos/${productoId}/details`)
        return response.data
    },

    inactivateCliente(clienteId) {
        return api.post(`/bridge/clientes/${clienteId}/inactivate`)
    },

    inactivateProducto(productoId) {
        return api.post(`/bridge/productos/${productoId}/inactivate`)
    }
}

export default canteraService
