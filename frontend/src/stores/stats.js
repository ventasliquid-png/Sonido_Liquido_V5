import { defineStore } from 'pinia';
import statsService from '../services/statsService';

export const useStatsStore = defineStore('stats', {
    state: () => ({
        stats: null,
        loading: false,
        error: null
    }),

    actions: {
        async fetchStats() {
            this.loading = true;
            try {
                const response = await statsService.getDashboardStats();
                this.stats = response.data;
            } catch (error) {
                this.error = error;
                console.error('Error fetching dashboard stats:', error);
            } finally {
                this.loading = false;
            }
        }
    }
});
