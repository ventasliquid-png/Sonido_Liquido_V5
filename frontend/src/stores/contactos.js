import { defineStore } from 'pinia'
import axios from 'axios'
import { useNotificationStore } from './notification'

const API_URL = '/contactos'

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
        },

        async hardDeleteContacto(id) {
            try {
                await axios.delete(`${API_URL}/${id}/hard`)
                this.contactos = this.contactos.filter(c => c.id !== id)
                const notify = useNotificationStore()
                notify.add('Contacto eliminado definitivamente', 'success')
            } catch (error) {
                console.error('Error hard deleting contacto:', error)
                const notify = useNotificationStore()
                notify.add('Error al eliminar contacto físicamente', 'error')
                throw error
            }
        },

        async addVinculo(contactoId, vinculoData) {
            this.loading = true
            try {
                const response = await axios.post(`${API_URL}/${contactoId}/vinculos`, vinculoData)
                // Update local state if contact is loaded
                const contacto = this.contactos.find(c => c.id === contactoId)
                if (contacto && contacto.vinculos) {
                    contacto.vinculos.push(response.data)
                }
                const notify = useNotificationStore()
                notify.add('Vínculo comercial agregado', 'success')
                return response.data
            } catch (error) {
                console.error('Error adding vinculo:', error)
                const notify = useNotificationStore()
                notify.add('Error al agregar vínculo', 'error')
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteVinculo(contactoId, vinculoId) {
            try {
                await axios.delete(`${API_URL}/${contactoId}/vinculos/${vinculoId}`)
                // Update local state
                const contacto = this.contactos.find(c => c.id === contactoId)
                if (contacto && contacto.vinculos) {
                    contacto.vinculos = contacto.vinculos.filter(v => v.id !== vinculoId)
                }
                const notify = useNotificationStore()
                notify.add('Vínculo eliminado', 'success')
            } catch (error) {
                console.error('Error deleting vinculo:', error)
                const notify = useNotificationStore()
                notify.add('Error al eliminar vínculo', 'error')
                throw error
            }
        },

        async searchPersonas(query) {
            if (!query || query.length < 2) return []
            try {
                // Usamos el endpoint existente con parametro q
                // Limitamos a 5 resultados para typeahead ligero
                const response = await axios.get(`${API_URL}?q=${query}&limit=5`)
                return response.data
            } catch (error) {
                console.error('Error buscando personas:', error)
                return []
            }
        }
    }
})
    ```
