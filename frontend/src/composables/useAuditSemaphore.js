// [IDENTIDAD] - frontend\src\composables\useAuditSemaphore.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

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

    // [ARLEQUÍN V2] Bits de cliente
    const GOLD_ARCA   = 4;   // Bit 2 — formal, validado AFIP
    const OPERATOR_OK = 16;  // Bit 4 — sello Rosa, informal operativo

    /**
     * Evalúa la calidad de un Cliente para determinar su color.
     * Doctrina Arlequín V2: Gold → verde, Rosa → verde si tiene segmento,
     * Amarillo → rojo si faltan campos para Blanco.
     * @param {Object} cliente
     * @returns {Object} Estado (VERDE/ROJO/KILL)
     */
    const evaluateCliente = (cliente) => {
        if (!cliente) return { ...STATUS.KILL, reasons: ['Cliente vacío'] };
        if (cliente.deleted_at) return { ...STATUS.KILL, reasons: ['Eliminado (Soft Delete)'] };

        const flags = cliente.flags_estado || 0;
        const reasons = [];

        if (flags & GOLD_ARCA) {
            // Gold/Blanco: siempre verde
            return { ...STATUS.VERDE, reasons: [] };
        }

        if (flags & OPERATOR_OK) {
            // Rosa: solo segmento obligatorio
            if (!cliente.segmento_id && !cliente.segmento) reasons.push('Falta Segmento');
        } else {
            // Amarillo/sin clasificar: exigir todo (camino a Blanco)
            if (!cliente.cuit || cliente.cuit.length < 11) reasons.push('Falta CUIT válido');
            if (!cliente.condicion_iva_id && !cliente.condicion_iva) reasons.push('Falta Condición IVA');
            if (!cliente.segmento_id && !cliente.segmento) reasons.push('Falta Segmento');
            const hasFiscalArr = cliente.domicilios && cliente.domicilios.some(d => d.es_fiscal && d.activo);
            const hasFiscalResumen = cliente.domicilio_fiscal_resumen && cliente.domicilio_fiscal_resumen.length > 5;
            if (!hasFiscalResumen && !hasFiscalArr) reasons.push('Falta Domicilio Fiscal');
        }

        if (reasons.length > 0) return { ...STATUS.ROJO, reasons };
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
