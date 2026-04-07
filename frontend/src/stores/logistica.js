// [IDENTIDAD] - frontend\src\stores\logistica.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

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
            // BRIDGE: Map flags_estado to legacy 'activo' and new V5.8 flags
            empresas.value = response.data.map(emp => ({
                ...emp,
                activo: !!(emp.flags_estado & 2),
                recommended: !!(emp.flags_estado & 8) // Bit 3
            }));
        } catch (err) {
            error.value = err.message || 'Error al cargar empresas';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function createEmpresa(data) {
        // BRIDGE: Map 'activo' back to flags_estado for backend
        if (data.activo !== undefined) {
           if (!data.flags_estado) data.flags_estado = 1; 
           if (data.activo) data.flags_estado |= 2;
           else data.flags_estado &= ~2;
        }
        loading.value = true;
        try {
            const response = await logisticaService.createEmpresa(data);
            const newEmp = {
                ...response.data,
                activo: !!(response.data.flags_estado & 2),
                recommended: !!(response.data.flags_estado & 8)
            };
            empresas.value.push(newEmp);
            return newEmp;
        } catch (err) {
            error.value = err.message || 'Error al crear empresa';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateEmpresa(id, data) {
        // BRIDGE: Map 'activo' back to flags_estado for backend
        if (data.activo !== undefined) {
           if (!data.flags_estado) data.flags_estado = 1;
           if (data.activo) data.flags_estado |= 2;
           else data.flags_estado &= ~2;
        }
        loading.value = true;
        try {
            const response = await logisticaService.updateEmpresa(id, data);
            const updatedEmp = {
                ...response.data,
                activo: !!(response.data.flags_estado & 2),
                recommended: !!(response.data.flags_estado & 8)
            };
            const index = empresas.value.findIndex(e => e.id === id);
            if (index !== -1) {
                empresas.value[index] = updatedEmp;
            }
            return updatedEmp;
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
                    id: nodo.id, 
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
