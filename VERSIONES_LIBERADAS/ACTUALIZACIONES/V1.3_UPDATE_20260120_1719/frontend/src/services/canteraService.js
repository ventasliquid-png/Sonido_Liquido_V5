import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const canteraService = {
    searchClientes(query) {
        return axios.get(`${API_URL}/bridge/clientes/search`, {
            params: { q: query }
        })
    },

    searchProductos(query) {
        return axios.get(`${API_URL}/bridge/productos/search`, {
            params: { q: query }
        })
    },

    getClientes(limit = 100, offset = 0) {
        return axios.get(`${API_URL}/bridge/clientes`, {
            params: { limit, offset }
        })
    },

    getProductos(limit = 100, offset = 0) {
        return axios.get(`${API_URL}/bridge/productos`, {
            params: { limit, offset }
        })
    },

    importCliente(clienteId) {
        return axios.post(`${API_URL}/bridge/clientes/${clienteId}/import`)
    },

    async importProducto(productoId) {
        const response = await axios.post(`${API_URL}/bridge/productos/${productoId}/import`)
        return response.data
    },

    async getProductoDetails(productoId) {
        const response = await axios.get(`${API_URL}/bridge/productos/${productoId}/details`)
        return response.data
    },

    inactivateCliente(clienteId) {
        return axios.post(`${API_URL}/bridge/clientes/${clienteId}/inactivate`)
    },

    inactivateProducto(productoId) {
        return axios.post(`${API_URL}/bridge/productos/${productoId}/inactivate`)
    }
}

export default canteraService
