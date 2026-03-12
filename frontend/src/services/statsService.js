import api from './api'

export default {
    getDashboardStats() {
        return api.get('/stats/dashboard')
    }
}
