<template>
  <div class="relative">
    <Combobox v-model="selected" @update:modelValue="onSelect">
      <div class="relative mt-1">
        <div class="relative w-full cursor-default overflow-hidden rounded-lg bg-black/40 border border-white/10 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
          <ComboboxInput
            class="w-full border-none py-2 pl-3 pr-10 text-xs leading-5 text-white bg-transparent focus:ring-0 placeholder-white/30"
            :displayValue="(item) => item ? displayFunction(item) : ''"
            @change="query = $event.target.value"
            :placeholder="placeholder"
          />
          <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
            <i class="fas fa-chevron-down text-white/40 text-xs"></i>
          </ComboboxButton>
        </div>
        <TransitionRoot
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
          @after-leave="query = ''"
        >
          <ComboboxOptions
            class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-[#1a050b] py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm z-50 border border-white/10"
          >
            <div
              v-if="filteredPeople.length === 0 && query !== ''"
              class="relative cursor-pointer select-none px-4 py-2 text-white/70 italic hover:bg-white/5"
              @click="createNew"
            >
              Crear "{{ query }}"...
            </div>

            <ComboboxOption
              v-for="item in filteredPeople"
              as="template"
              :key="item[itemKey]"
              :value="item"
              v-slot="{ selected, active }"
            >
              <li
                class="relative cursor-default select-none py-2 pl-10 pr-4"
                :class="{
                  'bg-blue-600 text-white': active,
                  'text-white/90': !active,
                }"
              >
                <span
                  class="block truncate text-xs"
                  :class="{ 'font-medium': selected, 'font-normal': !selected }"
                >
                  {{ displayFunction(item) }}
                </span>
                <span
                  v-if="selected"
                  class="absolute inset-y-0 left-0 flex items-center pl-3 text-white"
                  :class="{ 'text-white': active, 'text-blue-400': !active }"
                >
                  <i class="fas fa-check"></i>
                </span>
              </li>
            </ComboboxOption>
          </ComboboxOptions>
        </TransitionRoot>
      </div>
    </Combobox>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue'

const props = defineProps({
  modelValue: [String, Number, Object], // ID or Object
  options: {
     type: Array,
     default: () => []
  },
  displayKey: {
    type: String,
    default: 'nombre'
  },
  itemKey: {
    type: String,
    default: 'id'
  },
  placeholder: {
      type: String,
      default: 'Seleccione...'
  }
})

const emit = defineEmits(['update:modelValue', 'create'])

// Internal selection handling
const selected = ref(null)
const query = ref('')

// Initialize selected based on modelValue (ID)
watch(() => props.modelValue, (newId) => {
    if (newId) {
        selected.value = props.options.find(o => o[props.itemKey] === newId) || null
    } else {
        selected.value = null
    }
}, { immediate: true })

const filteredPeople = computed(() =>
  query.value === ''
    ? props.options
    : props.options.filter((item) => {
        return item[props.displayKey]
          .toLowerCase()
          .replace(/\s+/g, '')
          .includes(query.value.toLowerCase().replace(/\s+/g, ''))
      })
)

const displayFunction = (item) => {
    return item[props.displayKey]
}

const onSelect = (val) => {
    if (val) {
        emit('update:modelValue', val[props.itemKey])
    }
}

const createNew = () => {
    emit('create', query.value)
    // Optionally assume creation will succeed and wait for prop update?
    // We update query to empty for now
    query.value = ''
}
</script>
