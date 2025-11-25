import { defineStore } from 'pinia';
import { ref } from 'vue';
import clientesService from '../services/clientes';

export const useClientesStore = defineStore('clientes', () => {
    const clientes = ref([]);
    const currentCliente = ref(null);
    const loading = ref(false);
    const error = ref(null);

    async function fetchClientes(params = {}) {
        loading.value = true;
        error.value = null;
        try {
            const response = await clientesService.getAll(params);
            clientes.value = response.data;
        } catch (err) {
            error.value = err.message || 'Error al cargar clientes';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function fetchClienteById(id) {
        loading.value = true;
        error.value = null;
        try {
            const response = await clientesService.getById(id);
            currentCliente.value = response.data;
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al cargar cliente';
            console.error(err);
            return null;
        } finally {
            loading.value = false;
        }
    }

    async function createCliente(data) {
        loading.value = true;
        try {
            const response = await clientesService.create(data);
            clientes.value.push(response.data);
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al crear cliente';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateCliente(id, data) {
        loading.value = true;
        try {
            const response = await clientesService.update(id, data);
            const index = clientes.value.findIndex(c => c.id === id);
            if (index !== -1) {
                clientes.value[index] = response.data;
            }
            if (currentCliente.value && currentCliente.value.id === id) {
                currentCliente.value = response.data;
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al actualizar cliente';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteCliente(id) {
        loading.value = true;
        try {
            await clientesService.delete(id);
            const index = clientes.value.findIndex(c => c.id === id);
            if (index !== -1) {
                clientes.value[index].activo = false;
            }
            if (currentCliente.value && currentCliente.value.id === id) {
                currentCliente.value.activo = false;
            }
        } catch (err) {
            error.value = err.message || 'Error al dar de baja al cliente';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function hardDeleteCliente(id) {
        loading.value = true;
        try {
            await clientesService.hardDelete(id);
            clientes.value = clientes.value.filter(c => c.id !== id);
            if (currentCliente.value && currentCliente.value.id === id) {
                currentCliente.value = null;
            }
        } catch (err) {
            error.value = err.message || 'Error al eliminar cliente físicamente';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function approveCliente(id) {
        loading.value = true;
        try {
            await clientesService.approve(id);
            const index = clientes.value.findIndex(c => c.id === id);
            if (index !== -1) {
                clientes.value[index].requiere_auditoria = false;
            }
            if (currentCliente.value && currentCliente.value.id === id) {
                currentCliente.value.requiere_auditoria = false;
            }
        } catch (err) {
            error.value = err.message || 'Error al validar cliente';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    return {
        clientes,
        currentCliente,
        loading,
        error,
        fetchClientes,
        fetchClienteById,
        createCliente,
        updateCliente,
        deleteCliente,
        hardDeleteCliente,
        approveCliente
    };
});
