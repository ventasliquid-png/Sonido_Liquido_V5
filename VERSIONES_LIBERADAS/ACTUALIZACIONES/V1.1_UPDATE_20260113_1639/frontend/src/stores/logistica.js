import { defineStore } from 'pinia';
import { ref } from 'vue';
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

    return {
        empresas,
        nodos,
        loading,
        error,
        fetchEmpresas,
        createEmpresa,
        updateEmpresa,
        fetchNodos,
        createNodo,
        updateNodo
    };
});
