// [IDENTIDAD] - frontend\src\services\ingesta.js
// Versión: V5.6 GOLD | Sincronización: 20260508191600
// ------------------------------------------

import api from './api';

export default {
    /**
     * Sube un PDF para procesamiento inicial (Raw)
     * @param {FormData} formData 
     */
    uploadRaw(formData) {
        return api.post('/ingesta/raw', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    /**
     * Obtiene el preview del procesamiento y auditoría del Conserje
     * @param {String} rawId 
     */
    getPreview(rawId) {
        return api.get(`/ingesta/raw/${rawId}/preview`);
    },

    /**
     * Aprueba la ingesta y crea el registro de FacturaProcesada
     * @param {String} rawId 
     * @param {Object} payload Datos editados por el usuario
     */
    approve(rawId, payload) {
        return api.post(`/ingesta/raw/${rawId}/approve`, payload);
    },

    /**
     * Obtiene el detalle de una factura procesada y su audit_log
     * @param {String} procId 
     */
    getAudit(procId) {
        return api.get(`/ingesta/procesadas/${procId}`);
    }
};
