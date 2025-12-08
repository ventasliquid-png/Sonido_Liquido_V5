<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
        <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
            <div class="text-center mb-8">
                <span class="text-4xl">💧</span>
                <h2 class="mt-4 text-3xl font-bold text-gray-900">Sonido Líquido</h2>
                <p class="mt-2 text-gray-600">Inicia sesión para continuar</p>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-6">
                <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <span class="block sm:inline">{{ error }}</span>
                </div>

                <div>
                    <label for="username" class="block text-sm font-medium text-gray-700">Usuario</label>
                    <input 
                        id="username" 
                        v-model="username" 
                        type="text" 
                        required 
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">Contraseña</label>
                    <input 
                        id="password" 
                        v-model="password" 
                        type="password" 
                        required 
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                </div>

                <div>
                    <button 
                        type="submit" 
                        :disabled="loading"
                        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {{ loading ? 'Ingresando...' : 'Ingresar' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import api from '../services/api';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
    loading.value = true;
    error.value = '';
    
    try {
        const params = new URLSearchParams();
        params.append('username', username.value);
        params.append('password', password.value);

        // Usamos axios directo en lugar de la instancia 'api' para evitar
        // interferencias con headers globales (application/json) o interceptores.
        const response = await axios.post('http://localhost:8000/auth/token', params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const token = response.data.access_token;
        
        // Use AuthStore
        const authStore = useAuthStore();
        authStore.setToken(token);
        // Optionally fetch user details here if needed
        
        // Redirect to home
        router.push('/');
        
    } catch (err) {
        console.error(err);
        if (err.response && err.response.status === 401) {
            error.value = 'Usuario o contraseña incorrectos.';
        } else {
            error.value = 'Error al conectar con el servidor.';
        }
    } finally {
        loading.value = false;
    }
};
</script>
