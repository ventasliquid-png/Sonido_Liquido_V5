<template>
    <!-- [Card #183, S888] Cartel «¿Querés seguir?» en los últimos minutos de la sesión. Si nadie contesta, la sesión se cierra sola y lleva al login. -->
    <div v-if="visible" data-aviso="sesion-por-vencer" class="fixed inset-0 z-[300] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="bg-[#0b1120] border border-amber-500/50 rounded-2xl p-6 w-[380px] max-w-[92vw] shadow-2xl text-center">
            <i class="fas fa-user-clock text-3xl text-amber-400 mb-3"></i>
            <p class="text-amber-300 font-bold text-lg">Tu sesión está por vencer</p>
            <p class="text-gray-300 text-sm mt-1 mb-5">¿Querés seguir? Si no contestás, se cierra en <b class="font-mono text-white">{{ restanteTexto }}</b>.</p>
            <div class="flex gap-3 justify-center">
                <button data-accion="seguir" @click="seguir" :disabled="renovandoAhora"
                        class="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm disabled:opacity-50">
                    <i class="fas fa-check mr-1"></i> Sí, seguir
                </button>
                <button data-accion="cerrar" @click="cerrar"
                        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 font-bold text-sm border border-gray-600">
                    No, cerrar sesión
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../../services/api';
import { leerToken, msHastaVencer, AVISO_ANTES_MS, renovarAhora, irAlLogin } from '../../services/sesion';

const visible = ref(false);
const restante = ref(0);
const renovandoAhora = ref(false);
let reloj = null;

const restanteTexto = computed(() => {
    const s = Math.max(0, Math.ceil(restante.value / 1000));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
});

const revisar = () => {
    const token = leerToken();
    if (!token || window.location.pathname.startsWith('/login')) { visible.value = false; return; }
    const ms = msHastaVencer(token);
    if (ms <= 0) { visible.value = false; irAlLogin('vencida'); return; }
    restante.value = ms;
    visible.value = ms <= AVISO_ANTES_MS;
};

const seguir = async () => {
    renovandoAhora.value = true;
    const ok = await renovarAhora(api);
    renovandoAhora.value = false;
    if (ok) { visible.value = false; revisar(); } else { irAlLogin('vencida'); }
};

const cerrar = () => { visible.value = false; irAlLogin('cerrada'); };

onMounted(() => { revisar(); reloj = setInterval(revisar, 1000); });
onUnmounted(() => clearInterval(reloj));
</script>
