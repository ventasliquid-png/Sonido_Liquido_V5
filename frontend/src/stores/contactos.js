import { defineStore } from 'pinia'
import axios from 'axios'
import { useNotificationStore } from './notification'

const API_URL = '/contactos/'

export const useContactosStore = defineStore('contactos', {
    state: () => ({
        contactos: [],
        loading: false,
        error: null
    }),

    getters: {
        getContactoById: (state) => (id) => state.contactos.find(c => c.id === id),
    },

    actions: {
        async fetchContactos(params = {}) {
            this.loading = true
            this.error = null
            try {
                // Params puede ser { cliente_id: '...', q: 'Juan' }
                const response = await axios.get(API_URL, { params })
                this.contactos = response.data
                return this.contactos
            } catch (error) {
                console.error('Error fetching contactos:', error)
                this.error = error.message
                const notify = useNotificationStore()
                notify.add('Error cargando contactos', 'error')
                this.contactos = [] // [FIX] Limpiar estado corrupto/antiguo
                return []
            } finally {
                this.loading = false
            }
        },

        async createContacto(contactoData) {
            this.loading = true
            try {
                const response = await axios.post(API_URL, contactoData)
                this.contactos.push(response.data)
                const notify = useNotificationStore()
                notify.add('Contacto creado', 'success')
                return response.data
            } catch (error) {
                console.error('Error creating contacto:', error)
                const notify = useNotificationStore()
                notify.add('Error al crear contacto', 'error')
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateContacto(id, contactoData) {
            this.loading = true
            try {
                const response = await axios.put(`${API_URL}/${id}`, contactoData)
                const index = this.contactos.findIndex(c => c.id === id)
                if (index !== -1) {
                    this.contactos[index] = response.data
                }
                const notify = useNotificationStore()
                notify.add('Contacto actualizado', 'success')
                return response.data
            } catch (error) {
                console.error('Error updating contacto:', error)
                const notify = useNotificationStore()
                notify.add('Error al actualizar contacto', 'error')
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteContacto(id) {
            try {
                await axios.delete(`${API_URL}/${id}`)
                this.contactos = this.contactos.filter(c => c.id !== id)
                const notify = useNotificationStore()
                notify.add('Contacto eliminado', 'success')
            } catch (error) {
                console.error('Error deleting contacto:', error)
                const notify = useNotificationStore()
                notify.add('Error al eliminar contacto', 'error')
                throw error
            }
        }
    }
})
