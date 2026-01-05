import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const canteraService = {
    searchClientes(query) {
        return axios.get(`${API_URL}/cantera/clientes/search`, {
            params: { q: query }
        })
    },

    searchProductos(query) {
        return axios.get(`${API_URL}/cantera/productos/search`, {
            params: { q: query }
        })
    },

    getClientes(limit = 100, offset = 0) {
        return axios.get(`${API_URL}/cantera/clientes`, {
            params: { limit, offset }
        })
    },

    getProductos(limit = 100, offset = 0) {
        return axios.get(`${API_URL}/cantera/productos`, {
            params: { limit, offset }
        })
    },

    importCliente(clienteId) {
        return axios.post(`${API_URL}/cantera/clientes/${clienteId}/import`)
    },

    importProducto(productoId) {
        return axios.post(`${API_URL}/cantera/productos/${productoId}/import`)
    },

    inactivateCliente(clienteId) {
        return axios.post(`${API_URL}/cantera/clientes/${clienteId}/inactivate`)
    },

    inactivateProducto(productoId) {
        return axios.post(`${API_URL}/cantera/productos/${productoId}/inactivate`)
    }
}

export default canteraService
