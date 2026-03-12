import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import logisticaService from '../services/logistica';

export const useLogisticaStore = defineStore('logistica', () => {
    const empresas = ref([]);
    const nodos = ref([]);
    const loading = ref(false);
    const error = ref(null);

    async function fetchEmpresas(filter = 'active') {
        loading.value = true;
        try {
            const response = await logisticaService.getEmpresas({ status: filter });
            empresas.value = response.data;
        } catch (err) {
            error.value = err.message || 'Error al cargar empresas';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function createEmpresa(data) {
        loading.value = true;
        try {
            const response = await logisticaService.createEmpresa(data);
            empresas.value.push(response.data);
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al crear empresa';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateEmpresa(id, data) {
        loading.value = true;
        try {
            const response = await logisticaService.updateEmpresa(id, data);
            const index = empresas.value.findIndex(e => e.id === id);
            if (index !== -1) {
                empresas.value[index] = response.data;
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al actualizar empresa';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function fetchNodos(empresaId) {
        loading.value = true;
        try {
            const response = await logisticaService.getNodos(empresaId);
            nodos.value = response.data;
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al cargar nodos';
            console.error(err);
            return [];
        } finally {
            loading.value = false;
        }
    }

    async function createNodo(data) {
        loading.value = true;
        try {
            const response = await logisticaService.createNodo(data);
            nodos.value.push(response.data);
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al crear nodo';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateNodo(id, data) {
        loading.value = true;
        try {
            const response = await logisticaService.updateNodo(id, data);
            const index = nodos.value.findIndex(n => n.id === id);
            if (index !== -1) {
                nodos.value[index] = response.data;
            }
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al actualizar nodo';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteNodo(id) {
        loading.value = true;
        try {
            await logisticaService.hardDeleteNodo(id);
            nodos.value = nodos.value.filter(n => n.id !== id);
        } catch (err) {
            error.value = err.message || 'Error al eliminar nodo';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function fetchAllNodos() {
        loading.value = true;
        try {
            const response = await logisticaService.getNodos();
            nodos.value = response.data;
            return response.data;
        } catch (err) {
            error.value = err.message || 'Error al cargar todos los nodos';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    const transportOptions = computed(() => {
        const options = [];
        // Add Brands
        empresas.value.forEach(emp => {
            options.push({
                id: emp.id,
                nombre: emp.nombre,
                type: 'empresa',
                data: emp
            });
            // Add its nodes
            const empNodos = nodos.value.filter(n => n.empresa_id === emp.id);
            empNodos.forEach(nodo => {
                options.push({
                    id: nodo.id, // Careful with ID collision? No, UUIDs should be unique across tables usually, or we prefix
                    nombre: `${emp.nombre} (${nodo.nombre_nodo})`,
                    type: 'nodo',
                    empresa_id: emp.id,
                    provincia_id: nodo.provincia_id,
                    data: { ...emp, ...nodo, id: nodo.id, nombre_empresa: emp.nombre }
                });
            });
        });
        return options;
    });

    return {
        empresas,
        nodos,
        loading,
        error,
        fetchEmpresas,
        createEmpresa,
        updateEmpresa,
        fetchNodos,
        fetchAllNodos,
        createNodo,
        updateNodo,
        deleteNodo,
        transportOptions
    };
});
