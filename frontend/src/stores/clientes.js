import { defineStore } from 'pinia';
import { ref } from 'vue';
import clientesService from '../services/clientes';

export const useClientesStore = defineStore('clientes', () => {
    const clientes = ref([]);
    const currentCliente = ref(null);
    const loading = ref(false);
    const error = ref(null);

    async function fetchClientes(params = {}, force = false) {
        // Cache check: if we have data and not forcing, return early
        if (!force && clientes.value.length > 0 && Object.keys(params).length === 0) {
            console.log('Using cached clientes');
            return;
        }

        console.log('Fetching clientes from API');
        loading.value = true;
        error.value = null;
        try {
            const response = await clientesService.getAll(params);
            // Default sort: Alphabetical by razon_social
            clientes.value = response.data.sort((a, b) =>
                a.razon_social.localeCompare(b.razon_social)
            );
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

    // --- Domicilios Actions ---
    async function createDomicilio(clienteId, data) {
        loading.value = true;
        try {
            const response = await clientesService.createDomicilio(clienteId, data);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                if (!currentCliente.value.domicilios) currentCliente.value.domicilios = [];
                currentCliente.value.domicilios.push(response.data);
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al crear domicilio';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateDomicilio(clienteId, domicilioId, data) {
        loading.value = true;
        try {
            const response = await clientesService.updateDomicilio(clienteId, domicilioId, data);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                const index = currentCliente.value.domicilios.findIndex(d => d.id === domicilioId);
                if (index !== -1) currentCliente.value.domicilios[index] = response.data;
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al actualizar domicilio';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteDomicilio(clienteId, domicilioId) {
        loading.value = true;
        try {
            await clientesService.deleteDomicilio(clienteId, domicilioId);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                currentCliente.value.domicilios = currentCliente.value.domicilios.filter(d => d.id !== domicilioId);
            }
        } catch (err) {
            error.value = err.message || 'Error al eliminar domicilio';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    // --- Vinculos Actions ---
    async function createVinculo(clienteId, data) {
        loading.value = true;
        try {
            const response = await clientesService.createVinculo(clienteId, data);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                if (!currentCliente.value.vinculos) currentCliente.value.vinculos = []; // Note: API returns 'vinculos' but store might use 'contactos'? Check schema.
                // Schema says 'vinculos'. ClientCanvas uses 'contactos'. I need to align this.
                // In ClientCanvas loadCliente: contactos.value = cliente.contactos || []
                // But schema says 'vinculos'. I should check what the API actually returns.
                // Assuming API returns 'vinculos', I should update that.
                // If ClientCanvas maps it, I should update the mapped ref too.
                // For now, I'll update 'vinculos' in currentCliente.
                currentCliente.value.vinculos.push(response.data);
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al crear contacto';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateVinculo(clienteId, vinculoId, data) {
        loading.value = true;
        try {
            const response = await clientesService.updateVinculo(clienteId, vinculoId, data);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                const index = currentCliente.value.vinculos.findIndex(v => v.id === vinculoId);
                if (index !== -1) currentCliente.value.vinculos[index] = response.data;
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al actualizar contacto';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteVinculo(clienteId, vinculoId) {
        loading.value = true;
        try {
            await clientesService.deleteVinculo(clienteId, vinculoId);
            if (currentCliente.value && currentCliente.value.id === clienteId) {
                currentCliente.value.vinculos = currentCliente.value.vinculos.filter(v => v.id !== vinculoId);
            }
        } catch (err) {
            error.value = err.message || 'Error al eliminar contacto';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function incrementUsage(id) {
        try {
            await clientesService.incrementUsage(id);
        } catch (err) {
            console.error('Error incrementing usage:', err);
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
        approveCliente,
        createDomicilio,
        updateDomicilio,
        deleteDomicilio,
        createVinculo,
        updateVinculo,
        deleteVinculo
    };
});
