<template>
  <div class="atenea-container">
    <h2>Interfaz de Comando V5 (Atenea)</h2>
    
    <div class="input-area">
      <input
        v-model="query"
        @keyup.enter="invokeAtenea"
        type="text"
        placeholder="Ingrese la directiva estratégica o la pregunta..."
        :disabled="loading"
      />
      <button @click="invokeAtenea" :disabled="loading">
        <span v-if="loading">... Procesando Juicio ...</span>
        <span v-else>Invocar Atenea V5</span>
      </button>
    </div>

    <div v-if="response" class="response-area">
      <h3>Monitor de Bitácora y Respuesta Final:</h3>
      <div class="status-indicators">
        <span :class="['status-box', response.fue_doctrinal ? 'doctrinal' : 'tactical']">
          {{ response.fue_doctrinal ? '🏛️ JUICIO DOCTRINAL' : '🛠️ TÁCTICA APLICADA' }}
        </span>
        <span class="status-box">RAG Docs: {{ response.documentos_recuperados.length }}</span>
      </div>

      <pre class="generation-output">{{ response.respuesta_generada }}</pre>

      <h4>Documentos V5 (Contexto Usado):</h4>
      <ul class="documents-list">
        <li v-for="(doc, index) in response.documentos_recuperados" :key="index">
          {{ doc.substring(0, 80) }}...
        </li>
      </ul>
    </div>

    <div v-if="error" class="error-message">
      ❌ ERROR CRÍTICO: {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Estado Local
const query = ref('');
const response = ref(null);
const loading = ref(false);
const error = ref(null);

// Endpoint de la API (Backend FastAPI)
const API_URL = 'http://127.0.0.1:8000/atenea/invoke';

// Lógica de Invocación del Cerebro
const invokeAtenea = async () => {
  if (!query.value.trim()) return;

  loading.value = true;
  error.value = null;
  response.value = null;

  try {
    const payload = { query: query.value };
    
    // El 'POST' al endpoint que creamos en main.py
    const res = await axios.post(API_URL, payload);
    
    // El servidor Fast API nos devuelve el JSON del grafo
    response.value = res.data;
    
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
        // Captura errores específicos de FastAPI/Pydantic
        error.value = `Falla de Validación: ${err.response.data.detail[0].msg}`;
    } else if (err.response && err.response.data && err.response.data.error) {
        // Captura el error del Lifespan o Grafo (ej. "Grafo no compilado")
        error.value = `Falla del Servidor: ${err.response.data.error}`;
    } else {
        error.value = `Falla de Conexión o Red (Verifica Uvicorn): ${err.message}`;
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.atenea-container {
  max-width: 900px;
  margin: 30px auto;
  padding: 20px;
  border-radius: 10px;
  background-color: #1e1e1e;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
}
h2 { color: #8BE9FD; border-bottom: 2px solid #50FA7B; padding-bottom: 10px; }
h4 { color: #BD93F9; margin-top: 20px; }

.input-area {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
input {
  flex-grow: 1;
  padding: 12px;
  border: 1px solid #6272A4;
  border-radius: 6px;
  background-color: #282A36;
  color: #F8F8F2;
  font-size: 16px;
}
button {
  padding: 12px 20px;
  background-color: #50FA7B;
  color: #282A36;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}
button:hover:not(:disabled) {
  background-color: #44E06A;
}
button:disabled {
  background-color: #6272A4;
  cursor: not-allowed;
}

.response-area {
  padding: 15px;
  background-color: #44475A;
  border-radius: 6px;
}

.status-indicators {
  margin-bottom: 10px;
}

.status-box {
  display: inline-block;
  padding: 4px 10px;
  margin-right: 10px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: bold;
}
.doctrinal { background-color: #BD93F9; color: #282A36; }
.tactical { background-color: #FF79C6; color: #282A36; }

.generation-output {
  white-space: pre-wrap;
  background-color: #282A36;
  padding: 15px;
  border-left: 3px solid #FF79C6;
  color: #F8F8F2;
  font-family: monospace;
}

.documents-list {
  list-style-type: none;
  padding-left: 0;
  color: #F8F8F2;
}
.documents-list li {
  margin-bottom: 5px;
  border-left: 2px solid #6272A4;
  padding-left: 8px;
}
.error-message {
  padding: 15px;
  background-color: #FF5555;
  color: white;
  border-radius: 6px;
  margin-top: 15px;
}
</style>