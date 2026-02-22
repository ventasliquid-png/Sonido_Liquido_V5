<template>
  <div class="atenea-container">
    <!-- BARRA TÁCTICA CONFINADA -->
    <transition name="slide-down">
        <div v-if="quotaStatus.status === 'DEGRADADO' || quotaStatus.status === 'RESTORED'" 
             :class="['tactical-bar-mini', { 'restored': quotaStatus.status === 'RESTORED' }]">
            <div class="status-msg" :class="{ 'pulse': quotaStatus.status === 'DEGRADADO' }">
                {{ quotaStatus.status === 'DEGRADADO' ? 'MODO DEGRADADO - FLASH ACTIVO' : 'SISTEMA RESTABLECIDO' }}
            </div>
            <div class="timer">{{ formatTime(timeLeft) }}</div>
            <div class="progress-container">
                <div class="progress-fill" :style="{ width: (timeLeft / totalTime * 100) + '%' }"></div>
            </div>
        </div>
    </transition>

    <h2>Interfaz de Comando V5 (Atenea)</h2>
    
    <div class="input-area">
      <input
        v-model="query"
        @keyup.enter="invokeAtenea"
        type="text"
        placeholder="Ingrese la directiva estratégica..."
        :disabled="loading"
      />
      <button @click="invokeAtenea" :disabled="loading">
        <span v-if="loading">... Procesando ...</span>
        <span v-else>Invocar Atenea</span>
      </button>
    </div>

    <!-- BOTÓN DE TEST (SOLO EN ESTA VISTA) -->
    <button @click="triggerTest429" class="btn-test">TEST 429</button>

    <div v-if="response" class="response-area">
      <h3>Monitor de Bitácora:</h3>
      <div class="status-indicators">
        <span :class="['status-box', response.fue_doctrinal ? 'doctrinal' : 'tactical']">
          {{ response.fue_doctrinal ? '🏛️ DOCTRINAL' : '🛠️ TÁCTICO' }}
        </span>
        <span class="status-box">Contexto: {{ response.documentos_recuperados.length }}</span>
      </div>

      <pre class="generation-output">{{ response.respuesta_generada }}</pre>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const query = ref('');
const response = ref(null);
const loading = ref(false);
const error = ref(null);

// Lógica de Cuota (Confinada)
const quotaStatus = ref({ status: 'OK' });
const timeLeft = ref(0);
const totalTime = ref(60);
let quotaInterval = null;

const formatTime = (seconds) => {
    const s = seconds % 60;
    const m = Math.floor(seconds / 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const checkQuota = async () => {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/quota-status');
        const data = await res.json();
        quotaStatus.value = data;
        
        if (data.status === 'DEGRADADO') {
            const release = new Date(data.release_timestamp);
            const now = new Date();
            timeLeft.value = Math.max(0, Math.floor((release - now) / 1000));
            if (timeLeft.value === 0) {
                setTimeout(() => { quotaStatus.value.status = 'RESTORED'; }, 500);
            }
        }
    } catch (e) {}
};

const triggerTest429 = async () => {
    try {
        await axios.post('http://127.0.0.1:8000/api/test-429');
    } catch (e) {}
};

onMounted(() => {
    quotaInterval = setInterval(checkQuota, 1000);
});

onUnmounted(() => {
    clearInterval(quotaInterval);
});

const invokeAtenea = async () => {
  if (!query.value.trim()) return;
  loading.value = true;
  error.value = null;
  response.value = null;
  try {
    const res = await axios.post('http://127.0.0.1:8000/atenea/invoke', { query: query.value });
    response.value = res.data;
  } catch (err) {
    if (err.response && err.response.status === 429) {
        error.value = "⚠️ Cuota alcanzada. El Reloj Táctico se ha activado.";
    } else {
        error.value = `Falla: ${err.message}`;
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
  padding: 40px 20px 20px;
  border-radius: 10px;
  background-color: #1a1a1a;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
}

h2 { color: #8BE9FD; border-bottom: 2px solid #50FA7B; padding-bottom: 10px; margin-top: 10px; }

.input-area { display: flex; gap: 10px; margin-bottom: 20px; }
input { flex-grow: 1; padding: 12px; border: 1px solid #444; border-radius: 6px; background: #222; color: #fff; }
button { padding: 12px 20px; background: #50FA7B; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }

.response-area { padding: 15px; background: #222; border-radius: 6px; }
.status-indicators { margin-bottom: 10px; }
.status-box { display: inline-block; padding: 4px 10px; margin-right: 10px; border-radius: 4px; font-size: 0.85em; font-weight: bold; background: #444; color: #fff; }
.doctrinal { background: #BD93F9; color: #000; }
.tactical { background: #FF79C6; color: #000; }
.generation-output { white-space: pre-wrap; background: #111; padding: 15px; border-left: 3px solid #FF79C6; color: #F8F8F2; font-family: monospace; }
.error-message { padding: 15px; background: #FF5555; color: white; border-radius: 6px; margin-top: 15px; }

/* RELOJ TÁCTICO CONFINADO */
.tactical-bar-mini {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 30px;
    background: #000;
    border-bottom: 2px solid #ff9d00;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 15px;
    z-index: 10;
    box-shadow: 0 0 10px rgba(255,157,0,0.3);
}

.tactical-bar-mini.restored { border-color: #39ff14; background: #002200; }
.status-msg { font-size: 10px; font-weight: bold; color: #fff; }
.timer { font-family: monospace; font-size: 14px; color: #ff9d00; font-weight: bold; }
.restored .timer { color: #39ff14; }

.progress-container { position: absolute; bottom: 0; left: 0; width: 100%; height: 2px; background: rgba(255,157,0,0.1); }
.progress-fill { height: 100%; background: #ff9d00; transition: width 1s linear; }
.restored .progress-fill { background: #39ff14; width: 100% !important; }

.btn-test {
    background: rgba(255,157,0,0.1);
    color: #ff9d00;
    border: 1px solid #ff9d00;
    padding: 2px 8px;
    font-size: 9px;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 20px;
}

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
.pulse { animation: pulse 1s infinite; }

.slide-down-enter-active, .slide-down-leave-active { transition: transform 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { transform: translateY(-100%); }
</style>