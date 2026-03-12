import { computed } from 'vue';

/**
 * useAuditSemaphore
 * Lógica central de auditoría "Just-in-Time" para el Cargador Táctico.
 * Clasifica registros en tiempo real según su calidad y estado.
 */
export function useAuditSemaphore() {

    const STATUS = {
        VERDE: { code: 'VERDE', color: 'text-green-400', bg: 'bg-green-500/10', icon: 'fa-check-circle', label: 'Auditado' },
        ROJO: { code: 'ROJO', color: 'text-red-400', bg: 'bg-red-500/10', icon: 'fa-exclamation-triangle', label: 'Incompleto' },
        KILL: { code: 'KILL', color: 'text-gray-500', bg: 'bg-gray-500/10', icon: 'fa-trash', label: 'Basura' }
    };

    /**
     * Evalúa la calidad de un Cliente para determinar su color.
     * @param {Object} cliente 
     * @returns {Object} Estado (VERDE/ROJO/KILL)
     */
    const evaluateCliente = (cliente) => {
        if (!cliente) return { ...STATUS.KILL, reasons: ['Cliente vacío'] };

        // 1. Soft Deleted
        if (cliente.deleted_at) return { ...STATUS.KILL, reasons: ['Eliminado (Soft Delete)'] };

        // 2. Datos Críticos Faltantes
        const reasons = [];

        // CUIT
        if (!cliente.cuit || cliente.cuit.length < 11) reasons.push('Falta CUIT válido');

        // IVA
        if (!cliente.condicion_iva_id && !cliente.condicion_iva) reasons.push('Falta Condición IVA');

        // SEGMENTO
        if (!cliente.segmento_id && !cliente.segmento) reasons.push('Falta Segmento');

        // DIRECCION (Fiscal)
        // Check prop calculada O array de domicilios si está disponible
        const hasFiscalArr = cliente.domicilios && cliente.domicilios.some(d => d.es_fiscal && d.activo);
        const hasFiscalResumen = cliente.domicilio_fiscal_resumen && cliente.domicilio_fiscal_resumen.length > 5;

        if (!hasFiscalResumen && !hasFiscalArr) reasons.push('Falta Domicilio Fiscal');

        if (reasons.length > 0) {
            return { ...STATUS.ROJO, reasons };
        }

        // Default -> VERDE
        return { ...STATUS.VERDE, reasons: [] };
    };

    /**
     * Evalúa la calidad de un Producto.
     * @param {Object} producto 
     */
    const evaluateProducto = (producto) => {
        if (!producto) return { ...STATUS.KILL, reasons: ['Producto vacío'] };
        if (producto.deleted_at) return { ...STATUS.KILL, reasons: ['Eliminado'] };

        const reasons = [];

        // Reglas de Producto
        if (!producto.rubro_id) reasons.push('Falta Rubro');
        if (producto.precio_costo === null || producto.precio_costo === undefined) reasons.push('Sin Costo');
        if (!producto.activo) reasons.push('Inactivo');

        if (reasons.length > 0) {
            return { ...STATUS.ROJO, reasons };
        }

        return { ...STATUS.VERDE, reasons: [] };
    };

    return {
        STATUS,
        evaluateCliente,
        evaluateProducto
    };
}
