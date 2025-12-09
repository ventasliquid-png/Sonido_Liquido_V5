import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import productosApi from '../services/productosApi';
import rubrosApi from '../services/rubrosApi';
import maestrosApi from '../services/maestros';
import proveedoresApi from '../services/proveedoresApi';
import { useNotificationStore } from './notification';

export const useProductosStore = defineStore('productos', () => {
    const productos = ref([]);
    const rubros = ref([]);
    const unidades = ref([]);
    const tasasIva = ref([]);
    const proveedores = ref([]);
    const currentProducto = ref(null);
    const loading = ref(false);

    const filters = reactive({
        search: '',
        rubro_id: null,
        activo: true
    });

    const notificationStore = useNotificationStore();

    async function fetchProductos() {
        loading.value = true;
        try {
            const params = { ...filters };
            // Limpiar params nulos o vacíos
            if (!params.search) delete params.search;
            if (params.rubro_id === null) delete params.rubro_id;

            const response = await productosApi.getAll(params);
            productos.value = response.data;
        } catch (error) {
            console.error('Error fetching productos:', error);
            notificationStore.add('Error al cargar productos', 'error');
        } finally {
            loading.value = false;
        }
    }

    async function fetchRubros() {
        try {
            const response = await rubrosApi.getAll();
            rubros.value = response.data;
        } catch (error) {
            console.error('Error fetching rubros:', error);
            notificationStore.add('Error al cargar rubros', 'error');
        }
    }

    async function fetchUnidades() {
        try {
            const response = await maestrosApi.getUnidades();
            unidades.value = response.data;
        } catch (error) {
            console.error('Error fetching unidades:', error);
            notificationStore.add('Error al cargar unidades', 'error');
        }
    }

    async function fetchTasasIva() {
        try {
            const response = await maestrosApi.getTasasIva();
            tasasIva.value = response.data;
        } catch (error) {
            console.error('Error fetching tasas iva:', error);
            notificationStore.add('Error al cargar tasas IVA', 'error');
        }
    }

    async function fetchProveedores() {
        try {
            const response = await proveedoresApi.getAll();
            proveedores.value = response.data;
        } catch (error) {
            console.error('Error fetching proveedores:', error);
            notificationStore.add('Error al cargar proveedores', 'error');
        }
    }

    async function fetchProductoById(id) {
        loading.value = true;
        try {
            const response = await productosApi.getById(id);
            currentProducto.value = response.data;
            return response.data;
        } catch (error) {
            console.error('Error fetching producto:', error);
            notificationStore.add('Error al cargar el producto', 'error');
            return null;
        } finally {
            loading.value = false;
        }
    }

    async function createProducto(payload) {
        loading.value = true;
        try {
            const response = await productosApi.create(payload);
            productos.value.push(response.data);
            notificationStore.add('Producto creado exitosamente', 'success');
            return response.data;
        } catch (error) {
            console.error('Error creating producto:', error);
            notificationStore.add('Error al crear producto', 'error');
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function updateProducto(id, payload) {
        loading.value = true;
        try {
            const response = await productosApi.update(id, payload);
            const index = productos.value.findIndex(p => p.id === id);
            if (index !== -1) {
                productos.value[index] = response.data;
            }
            if (currentProducto.value && currentProducto.value.id === id) {
                currentProducto.value = response.data;
            }
            notificationStore.add('Producto actualizado exitosamente', 'success');
            return response.data;
        } catch (error) {
            console.error('Error updating producto:', error);
            notificationStore.add('Error al actualizar producto', 'error');
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function toggleEstado(id) {
        loading.value = true;
        try {
            await productosApi.toggleActive(id);
            // Actualizar estado localmente
            const index = productos.value.findIndex(p => p.id === id);
            if (index !== -1) {
                productos.value[index].activo = !productos.value[index].activo;
            }
            if (currentProducto.value && currentProducto.value.id === id) {
                currentProducto.value.activo = !currentProducto.value.activo;
            }
            notificationStore.add('Estado del producto actualizado', 'success');
        } catch (error) {
            console.error('Error toggling producto status:', error);
            notificationStore.add('Error al cambiar estado del producto', 'error');
        } finally {
            loading.value = false;
        }
    }

    async function createRubro(payload) {
        try {
            const response = await rubrosApi.create(payload);
            rubros.value.push(response.data);
            notificationStore.add('Rubro creado correctamente', 'success');
            return response.data;
        } catch (error) {
            console.error('Error creating rubro:', error);
            notificationStore.add('Error al crear rubro', 'error');
            throw error;
        }
    }

    async function updateRubro(id, payload) {
        try {
            const response = await rubrosApi.update(id, payload);
            const index = rubros.value.findIndex(r => r.id === id);
            if (index !== -1) {
                rubros.value[index] = response.data;
            }
            notificationStore.add('Rubro actualizado correctamente', 'success');
            return response.data;
        } catch (error) {
            console.error('Error updating rubro:', error);
            notificationStore.add('Error al actualizar rubro', 'error');
            throw error;
        }
    }

    async function deleteRubro(id) {
        try {
            await rubrosApi.delete(id);
            rubros.value = rubros.value.filter(r => r.id !== id);
            notificationStore.add('Rubro eliminado', 'success');
        } catch (error) {
            console.error('Error deleting rubro:', error);
            notificationStore.add('Error al eliminar rubro', 'error');
            throw error;
        }
    }

    return {
        productos,
        rubros,
        unidades,
        tasasIva,
        proveedores,
        currentProducto,
        filters,
        loading,
        fetchProductos,
        fetchRubros,
        fetchUnidades,
        fetchTasasIva,
        fetchProveedores,
        fetchProductoById,
        createProducto,
        updateProducto,
        toggleEstado,
        createRubro,
        updateRubro,
        deleteRubro
    };
});
