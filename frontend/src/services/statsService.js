// [IDENTIDAD] - frontend\src\services\statsService.js
// Versión: V5.6 GOLD | Sincronización: 20260407130827
// ------------------------------------------

import api from './api'

export default {
    getDashboardStats() {
        return api.get('/stats/dashboard')
    }
}
