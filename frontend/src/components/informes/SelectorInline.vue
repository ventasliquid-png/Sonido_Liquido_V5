// [IDENTIDAD] - frontend\src\components\informes\SelectorInline.vue
// [S876] Cartel de un valor (estado, circuito...) que se cambia desde el informe sin abrir la ficha del pedido. Es el
// comportamiento común de EstadoEditable y CircuitoEditable: cada uno le pasa sus opciones y decide qué hacer al elegir.
//
// Cómo se usa (todo con el teclado o con el mouse):
//   - clic en el cartel (o flecha abajo / arriba con el cartel enfocado) abre la lista de opciones;
//   - flechas arriba / abajo recorren la lista, Enter (o clic) confirma, Escape cancela;
//   - escribir una inicial salta a la opción que empieza con esa letra, y repetirla enseguida pasa a la siguiente que
//     también empieza así (P = PENDIENTE, P otra vez = PRESUPUESTO).
// Las flechas NUNCA eligen por sí solas: mover el resaltado no escribe nada, solo Enter o un clic.
// ------------------------------------------

<template>
  <span class="inline-block">
    <button ref="gatillo" type="button"
      @click.stop="abrir" @dblclick.stop @keydown="teclaGatillo"
      :disabled="guardando"
      class="inline-flex items-center gap-1 px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider cursor-pointer hover:brightness-125 focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-wait"
      :class="claseBadge" :title="titulo"
      aria-haspopup="listbox" :aria-expanded="abierto">
      {{ texto || valor }}
      <i class="fas text-[8px] opacity-60" :class="guardando ? 'fa-spinner fa-spin' : 'fa-caret-down'"></i>
    </button>

    <Teleport to="body">
      <!-- Capa transparente: un clic afuera cierra la lista y no hace nada más. -->
      <div v-if="abierto" class="fixed inset-0 z-[99998]" @click.stop="cerrar" @contextmenu.prevent="cerrar"></div>
      <div v-if="abierto" ref="lista" tabindex="-1" role="listbox" :aria-label="etiqueta"
        @keydown="teclaLista" @click.stop
        class="fixed z-[99999] min-w-[160px] rounded-lg border border-blue-500/30 bg-[#020617] shadow-2xl py-1 outline-none"
        :style="{ top: pos.top + 'px', left: pos.left + 'px' }">
        <div v-for="(o, i) in opciones" :key="o.value" role="option" :aria-selected="o.value === valor"
          @click.stop="elegir(o)" @mouseenter="resaltado = i"
          class="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider cursor-pointer flex items-center gap-2"
          :class="[o.clase, i === resaltado ? 'bg-white/10' : '']">
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          {{ o.label }}
          <i v-if="o.value === valor" class="fas fa-check ml-auto text-[9px]" title="Valor actual"></i>
        </div>
      </div>
    </Teleport>
  </span>
</template>

<script setup>
import { ref, reactive, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({
  opciones: { type: Array, required: true },   // [{ value, label, clase }]
  valor: { type: String, default: '' },        // valor actual
  texto: { type: String, default: '' },        // lo que se muestra en el cartel (si no, el valor)
  claseBadge: { type: String, default: '' },   // colores del cartel
  titulo: { type: String, default: '' },
  etiqueta: { type: String, default: 'Opciones' },
  guardando: { type: Boolean, default: false },
})
const emit = defineEmits(['elegido'])

const gatillo = ref(null)
const lista = ref(null)
const abierto = ref(false)
const resaltado = ref(-1)
const pos = reactive({ top: 0, left: 0 })

const ALTO_ITEM = 28
const altoLista = () => props.opciones.length * ALTO_ITEM + 12

// Para las iniciales: la última letra tecleada y cuándo (la misma letra enseguida = pasar a la siguiente opción).
let ultimaInicial = ''
let ultimaInicialTs = 0

const abrir = async () => {
  if (props.guardando) return
  const r = gatillo.value.getBoundingClientRect()
  pos.left = Math.max(8, Math.min(r.left, window.innerWidth - 176))
  // Si abajo no entra la lista, se abre hacia arriba.
  pos.top = r.bottom + 4 + altoLista() > window.innerHeight ? Math.max(8, r.top - altoLista() - 4) : r.bottom + 4
  resaltado.value = props.opciones.findIndex((o) => o.value === props.valor)
  ultimaInicial = ''
  abierto.value = true
  await nextTick()
  lista.value?.focus()
}

const cerrar = () => {
  abierto.value = false
  nextTick(() => gatillo.value?.focus())
}

const elegir = (opcion) => {
  cerrar()
  if (opcion.value !== props.valor) emit('elegido', opcion.value)
}

// Con el cartel enfocado y la lista cerrada, flecha abajo / arriba la abre (Enter y espacio ya disparan el clic).
const teclaGatillo = (e) => {
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault()
    abrir()
  }
}

const teclaLista = (e) => {
  const n = props.opciones.length
  if (e.ctrlKey || e.metaKey || e.altKey) return
  if (e.key === 'ArrowDown') { e.preventDefault(); resaltado.value = (resaltado.value + 1) % n }
  else if (e.key === 'ArrowUp') { e.preventDefault(); resaltado.value = resaltado.value <= 0 ? n - 1 : resaltado.value - 1 }
  else if (e.key === 'Home') { e.preventDefault(); resaltado.value = 0 }
  else if (e.key === 'End') { e.preventDefault(); resaltado.value = n - 1 }
  else if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    if (resaltado.value >= 0) elegir(props.opciones[resaltado.value])
    else cerrar()
  }
  else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); cerrar() }
  else if (e.key === 'Tab') { cerrar() }
  else if (e.key.length === 1 && /[a-záéíóúñ0-9]/i.test(e.key)) {
    // Inicial: la primera vez salta a la PRIMERA opción que empieza con esa letra (P -> PENDIENTE); si se repite la
    // misma letra enseguida pasa a la siguiente que también empieza así (P otra vez -> PRESUPUESTO) y da la vuelta.
    e.preventDefault()
    const inicial = e.key.toUpperCase()
    const coincidencias = props.opciones.map((o, i) => (o.label.toUpperCase().startsWith(inicial) ? i : -1)).filter((i) => i >= 0)
    const repetida = inicial === ultimaInicial && Date.now() - ultimaInicialTs < 1500
    ultimaInicial = inicial
    ultimaInicialTs = Date.now()
    if (coincidencias.length === 0) return
    resaltado.value = repetida ? (coincidencias.find((i) => i > resaltado.value) ?? coincidencias[0]) : coincidencias[0]
  }
}

onBeforeUnmount(() => { abierto.value = false })
</script>
