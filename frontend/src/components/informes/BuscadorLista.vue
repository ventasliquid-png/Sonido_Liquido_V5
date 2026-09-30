// [IDENTIDAD] - frontend\src\components\informes\BuscadorLista.vue
// [S875] Selector con búsqueda para los filtros de los informes (cliente, producto, rangos desde/hasta).
// Con 59 clientes y 42 productos una lista desplegable plana es lenta: acá se escribe un pedazo del nombre, del
// código o del CUIT y la lista se acota (sin acentos ni mayúsculas). `options`: [{ id, label, detalle? }].
// El valor que emite es el `id` de la opción elegida (null al limpiar).
// ------------------------------------------

<template>
  <div class="relative">
    <input :value="texto" @input="onInput" @focus="abrir" @blur="cerrar"
      @keydown.down.prevent="mover(1)" @keydown.up.prevent="mover(-1)"
      @keydown.enter.prevent="elegirResaltada" @keydown.esc="cerrar"
      :placeholder="placeholder" autocomplete="off"
      class="h-9 w-full rounded-lg border border-blue-900/30 bg-[#02050f] pl-3 pr-7 text-xs text-blue-100 focus:border-blue-500 focus:outline-none" />
    <button v-if="modelValue !== null && modelValue !== undefined" type="button" @mousedown.prevent="limpiar"
      class="absolute right-2 top-2.5 text-blue-400/50 hover:text-blue-200" title="Quitar">
      <i class="fas fa-times text-[10px]"></i>
    </button>
    <ul v-if="abierto"
      class="absolute z-30 mt-1 max-h-64 min-w-full w-max max-w-md overflow-auto rounded-lg border border-blue-900/40 bg-[#02050f] shadow-xl text-xs">
      <li v-if="!filtradas.length" class="px-3 py-2 text-blue-400/40">Sin coincidencias</li>
      <li v-for="(o, i) in filtradas" :key="o.id" @mousedown.prevent="elegir(o)"
        class="px-3 py-1.5 cursor-pointer text-blue-100 whitespace-nowrap"
        :class="i === resaltada ? 'bg-blue-900/40' : 'hover:bg-blue-900/20'">
        {{ o.label }}<span v-if="o.detalle" class="ml-2 text-blue-400/50">{{ o.detalle }}</span>
      </li>
      <li v-if="hayMas" class="px-3 py-1.5 text-[10px] text-blue-400/40">Seguí escribiendo para acotar…</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: null },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Buscar…' },
  // Para rangos desde/hasta: si lo escrito no coincide con ninguna opción, se toma tal cual como límite
  // ("hasta M", "hasta VS0010" aunque ese código exacto no exista).
  libre: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const LIMITE = 60
const normalizar = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

const texto = ref('')
const abierto = ref(false)
const resaltada = ref(0)
const buscando = ref(false)   // true mientras el usuario escribe: ahí se filtra; si no, se ve todo

const etiquetaDe = (id) => props.options.find((o) => o.id === id)?.label ?? (props.libre ? String(id) : '')
watch(() => [props.modelValue, props.options.length], () => {
  texto.value = props.modelValue === null || props.modelValue === undefined ? '' : etiquetaDe(props.modelValue)
  buscando.value = false
}, { immediate: true })

const coincidentes = computed(() => {
  const q = normalizar(texto.value)
  if (!buscando.value || !q) return props.options
  return props.options.filter((o) => normalizar(`${o.label} ${o.detalle ?? ''}`).includes(q))
})
const filtradas = computed(() => coincidentes.value.slice(0, LIMITE))
const hayMas = computed(() => coincidentes.value.length > LIMITE)

const abrir = () => { abierto.value = true; resaltada.value = 0 }
const cerrar = () => {
  abierto.value = false
  if (props.libre && buscando.value) {
    // Límite escrito a mano: se adopta lo tipeado (vacío = sin límite).
    const t = texto.value.trim()
    buscando.value = false
    emit('update:modelValue', t || null)
    texto.value = t
    return
  }
  buscando.value = false
  texto.value = props.modelValue === null || props.modelValue === undefined ? '' : etiquetaDe(props.modelValue)
}
const onInput = (e) => { texto.value = e.target.value; buscando.value = true; abierto.value = true; resaltada.value = 0 }
const mover = (d) => { abierto.value = true; resaltada.value = Math.max(0, Math.min(filtradas.value.length - 1, resaltada.value + d)) }
const elegir = (o) => { emit('update:modelValue', o.id); texto.value = o.label; buscando.value = false; abierto.value = false }
const elegirResaltada = () => {
  if (filtradas.value[resaltada.value]) elegir(filtradas.value[resaltada.value])
  else if (props.libre) cerrar()
}
const limpiar = () => { emit('update:modelValue', null); texto.value = ''; buscando.value = false }
</script>
