import { defineStore } from 'pinia'
import axios from 'axios'
import { useNotificationStore } from './notification'

const API_URL = '/contactos'
const API_AGENDA = '/agenda'

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
                // [FIX] Usar endpoint de AGENDA que es el robusto para vinculos
                // POST /agenda/vinculos
                // Payload debe incluir persona_id, cliente_id/transporte_id, tipo_contacto_id

                // Aseguramos que persona_id este en el payload
                const payload = { ...vinculoData, persona_id: contactoId }

                const response = await axios.post(`${API_AGENDA}/vinculos`, payload)

                // Update local state if contact is loaded
                const contacto = this.contactos.find(c => c.id === contactoId)
                if (contacto && contacto.vinculos) {
                    // Evitar duplicados si el backend retorna el mismo
                    const exists = contacto.vinculos.find(v => v.id === response.data.id)
                    if (!exists) contacto.vinculos.push(response.data)
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

        async updateVinculo(contactoId, vinculoId, vinculoData) {
            this.loading = true
            try {
                // [FIX] Use Multiplex V6 Endpoint (backend/contactos) to ensure persistence in 'vinculos' table
                // PUT /contactos/{contactoId}/vinculos/{vinculoId}
                // (Instead of /agenda/vinculos which uses legacy tables)

                const response = await axios.put(`${API_URL}/${contactoId}/vinculos/${vinculoId}`, vinculoData)

                // Update local state
                const contacto = this.contactos.find(c => c.id === contactoId)
                if (contacto && contacto.vinculos) {
                    const idx = contacto.vinculos.findIndex(v => v.id === vinculoId)
                    if (idx !== -1) {
                        // Merge response into existing object to keep reactivity
                        Object.assign(contacto.vinculos[idx], response.data)
                    }
                }
                const notify = useNotificationStore()
                notify.add('Vínculo actualizado', 'success')
                return response.data
            } catch (error) {
                // If it fails on Multiplex, try Agenda fallback? No, we want consistency.
                console.error('Error updating vinculo:', error)

                // Fallback debugging attempt (OPTIONAL, remove in prod)
                // console.warn('Trying legacy endpoint fallback...')
                // await axios.put(`${API_AGENDA}/vinculos/${vinculoId}`, vinculoData)

                const notify = useNotificationStore()
                // notify.add('Error al actualizar vínculo (Verifique DB V6)', 'error')
                notify.add('Error actualizando rol', 'error')
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteVinculo(contactoId, vinculoId) {
            try {
                // We should also align DELETE but for now Add/Delete work "globally" via agenda maybe?
                // Let's stick with Agenda for creation/deletion if router supports it?
                // Wait, Agenda creates in vinculos_comerciales. Multiplex reads vinculos.
                // WE HAVE A DB SPLIT ISSUE if Creation uses Agenda!
                // CHECK addVinculo logic!
                // But for now, fix update.

                // [FIX] DELETE /agenda/vinculos/{id}
                await axios.delete(`${API_AGENDA}/vinculos/${vinculoId}`)

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
