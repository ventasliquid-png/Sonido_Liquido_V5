import { defineStore } from 'pinia';
import agendaService from '../services/agenda';

export const useAgendaStore = defineStore('agenda', {
    state: () => ({
        personas: [],
        loading: false,
        error: null
    }),

    actions: {
        async fetchPersonas(params = {}) {
            this.loading = true;
            try {
                const response = await agendaService.getPersonas(params);
                this.personas = response.data;
            } catch (error) {
                this.error = error;
                console.error('Error fetching personas:', error);
            } finally {
                this.loading = false;
            }
        },

        async searchPersonas(query) {
            this.loading = true;
            try {
                const response = await agendaService.searchPersonas(query);
                this.personas = response.data;
            } catch (error) {
                this.error = error;
                console.error('Error searching personas:', error);
            } finally {
                this.loading = false;
            }
        },

        async createPersona(data) {
            try {
                const response = await agendaService.createPersona(data);
                this.personas.push(response.data);
                return response.data;
            } catch (error) {
                throw error;
            }
        },

        async updatePersona(id, data) {
            try {
                const response = await agendaService.updatePersona(id, data);
                // Update local state preserving the object reference for better reactivity
                const index = this.personas.findIndex(p => p.id === id);
                if (index !== -1) {
                    Object.assign(this.personas[index], response.data);
                }
                return response.data;
            } catch (error) {
                throw error;
            }
        }
    }
});
