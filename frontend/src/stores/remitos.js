import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import remitosService from '../services/remitos';

export const useRemitosStore = defineStore('remitos', () => {
    const remitos = ref([]);
    const currentPedido = ref(null); // Pedido being worked on
    const loading = ref(false);
    const error = ref(null);

    // --- Actions ---

    async function fetchRemitos(pedidoId) {
        loading.value = true;
        error.value = null;
        try {
            const response = await remitosService.getRemitosByPedido(pedidoId);
            remitos.value = response.data;
        } catch (err) {
            console.error("Error fetching remitos:", err);
            error.value = "No se pudieron cargar los remitos.";
            // If backend misses endpoint, we might get 404.
            remitos.value = [];
        } finally {
            loading.value = false;
        }
    }

    async function createRemito(data) {
        loading.value = true;
        error.value = null;
        try {
            const response = await remitosService.createRemito(data);
            remitos.value.push(response.data);
            return response.data;
        } catch (err) {
            console.error("Error creating remito:", err);
            error.value = err.response?.data?.detail || "Error al crear remito.";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function despacharRemito(remitoId) {
        loading.value = true;
        try {
            await remitosService.despacharRemito(remitoId);
            // Update local state
            const r = remitos.value.find(i => i.id === remitoId);
            if (r) {
                r.estado = 'EN_CAMINO';
                r.fecha_salida = new Date().toISOString();
            }
        } catch (err) {
            error.value = err.response?.data?.detail || "Error al despachar.";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function addItemToRemito(remitoId, itemData) {
        loading.value = true;
        try {
            const res = await remitosService.addItem(remitoId, itemData);
            // Update state
            const r = remitos.value.find(i => i.id === remitoId);
            if (r) {
                // Check if item exists to update or push
                const existing = r.items.find(i => i.pedido_item_id === itemData.pedido_item_id);
                if (existing) {
                    existing.cantidad += itemData.cantidad;
                } else {
                    r.items.push(res.data);
                }
            }
        } catch (err) {
            error.value = err.response?.data?.detail || "Error al agregar ítem.";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    // --- Computed ---

    // Calculate "Pendientes" based on currentPedido and loaded remitos
    // This requires currentPedido to be set (passed from PedidoCanvas)
    const itemsPendientes = computed(() => {
        if (!currentPedido.value) return [];

        const pendientes = [];

        currentPedido.value.items.forEach(pItem => {
            // Sumar cantidad ya remitida en TODOS los remitos activos
            let remitido = 0;
            remitos.value.forEach(rem => {
                const rItem = rem.items.find(ri => ri.pedido_item_id === pItem.id);
                if (rItem) {
                    remitido += rItem.cantidad;
                }
            });

            const saldo = pItem.cantidad - remitido;
            if (saldo > 0) {
                pendientes.push({
                    ...pItem,
                    cantidad_original: pItem.cantidad,
                    cantidad_remitida: remitido,
                    cantidad_pendiente: saldo,
                    // For UI input
                    cantidad_a_remitir: saldo
                });
            }
        });
        return pendientes;
    });

    return {
        remitos,
        currentPedido,
        loading,
        error,
        fetchRemitos,
        createRemito,
        despacharRemito,
        addItemToRemito,
        itemsPendientes
    };
});
