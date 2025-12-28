<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    modelValue: {
        type: [String, Number],
        default: null
    },
    options: {
        type: Array,
        default: () => []
    },
    label: {
        type: String,
        default: ''
    },
    allowCreate: {
        type: Boolean,
        default: true
    },
    placeholder: {
        type: String,
        default: 'Seleccionar...'
    },
    priorityIds: {
        type: Array,
        default: () => []
    },
    required: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'create-new']);

const isOpen = ref(false);
const searchQuery = ref('');
const highlightedIndex = ref(-1);
const inputRef = ref(null);
const listRef = ref(null);
const containerRef = ref(null);

// Initialize search query based on modelValue
watch(() => props.modelValue, (newVal) => {
    const selected = props.options.find(o => o.id === newVal);
    if (selected) {
        searchQuery.value = selected.nombre || selected.descripcion;
    } else {
        // Only clear if options are loaded, otherwise keep it (might be loading)
        if (props.options.length > 0) {
            searchQuery.value = '';
        }
    }
}, { immediate: true });

// Update query if options change
watch(() => props.options, () => {
    const selected = props.options.find(o => o.id === props.modelValue);
    if (selected) {
        searchQuery.value = selected.nombre || selected.descripcion;
    }
});

const filteredOptions = computed(() => {
    let opts = props.options;
    
    // Filter by search
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        // If exact match, show all (user is browsing)
        const selected = props.options.find(o => o.id === props.modelValue);
        if (!selected || (selected.nombre || selected.descripcion).toLowerCase() !== query) {
            opts = props.options.filter(opt => {
                const nombre = (opt.nombre || '').toLowerCase();
                const desc = (opt.descripcion || '').toLowerCase();
                const sku = opt.sku ? String(opt.sku).toLowerCase() : '';
                return nombre.includes(query) || desc.includes(query) || sku.includes(query);
            });
        }
    }

    // Group by Priority
    if (props.priorityIds.length > 0) {
        const priority = [];
        const others = [];
        opts.forEach(opt => {
            if (props.priorityIds.includes(opt.id)) {
                priority.push({ ...opt, _isPriority: true });
            } else {
                others.push(opt);
            }
        });
        
        // If searching, maybe we don't want headers? 
        // User requirement: "este debe aparecer PRIMERO... bajo un encabezado"
        // Let's return a flat list but with markers, or just sorted.
        // To render headers, we need a structure.
        // But for keyboard navigation, a flat list is better.
        // We can add "headers" as non-selectable items in the list?
        // Or just sort them to top and add a visual separator/badge.
        
        // Let's try adding headers as special items if we are not searching (or even if we are)
        const result = [];
        if (priority.length > 0) {
            result.push({ _type: 'header', label: 'HABITUALES DEL CLIENTE' });
            result.push(...priority);
            if (others.length > 0) {
                result.push({ _type: 'header', label: 'OTROS' });
            }
        }
        result.push(...others);
        return result;
    }

    return opts;
});

const toggleOpen = () => {
    if (isOpen.value) {
        close();
    } else {
        open();
    }
};

const open = () => {
    isOpen.value = true;
    highlightedIndex.value = -1;
    if (document.activeElement !== inputRef.value) {
        inputRef.value.focus();
    }
};

const close = () => {
    isOpen.value = false;
    highlightedIndex.value = -1;
    const selected = props.options.find(o => o.id === props.modelValue);
    if (selected) {
        searchQuery.value = selected.nombre || selected.descripcion;
    } else {
        searchQuery.value = '';
    }
};

const selectOption = (option) => {
    if (option._type === 'header') return;
    emit('update:modelValue', option.id);
    searchQuery.value = option.nombre || option.descripcion;
    isOpen.value = false;
};

const triggerCreate = () => {
    emit('create-new');
    close();
};

const handleInput = (e) => {
    if (!isOpen.value) isOpen.value = true;
    if (e.target.value === '') {
        emit('update:modelValue', null);
    }
};

const handleKeydown = (e) => {
    if (e.key === 'F4') {
        e.preventDefault();
        triggerCreate();
        return;
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!isOpen.value) {
            open();
            return;
        }
        // Skip headers
        let nextIndex = highlightedIndex.value + 1;
        while (nextIndex < filteredOptions.value.length) {
            if (!filteredOptions.value[nextIndex]._type) {
                highlightedIndex.value = nextIndex;
                scrollToHighlighted();
                return;
            }
            nextIndex++;
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        // Skip headers
        let prevIndex = highlightedIndex.value - 1;
        while (prevIndex >= 0) {
            if (!filteredOptions.value[prevIndex]._type) {
                highlightedIndex.value = prevIndex;
                scrollToHighlighted();
                return;
            }
            prevIndex--;
        }
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (isOpen.value && highlightedIndex.value >= 0) {
            selectOption(filteredOptions.value[highlightedIndex.value]);
        } else if (isOpen.value) {
             // Auto select first valid option if none highlighted
             const firstValid = filteredOptions.value.find(o => !o._type);
             if (firstValid) selectOption(firstValid);
        }
    } else if (e.key === 'Escape') {
        if (isOpen.value) {
            e.preventDefault();
            e.stopPropagation();
            close();
        }
    } else if (e.key === 'Tab') {
        if (isOpen.value) {
            close();
        }
    }
};

const scrollToHighlighted = () => {
    nextTick(() => {
        if (!listRef.value) return;
        const items = listRef.value.querySelectorAll('li[data-selectable="true"]');
        // We need to map highlightedIndex (which is index in filteredOptions) to DOM index?
        // Or just find the element with data-index matching highlightedIndex
        const item = listRef.value.querySelector(`li[data-index="${highlightedIndex.value}"]`);
        if (item) {
            item.scrollIntoView({ block: 'nearest' });
        }
    });
};

const handleClickOutside = (e) => {
    if (isOpen.value && containerRef.value && !containerRef.value.contains(e.target)) {
        close();
    }
};

onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
    <div class="w-full" ref="containerRef">
        <label v-if="label" class="block text-xs font-bold text-gray-600 mb-1" @click="inputRef?.focus()">
            {{ label }} <span v-if="required" class="text-red-500">*</span>
        </label>
        <div class="relative flex gap-2">
            <div class="relative flex-1">
                <input
                    ref="inputRef"
                    type="text"
                    v-model="searchQuery"
                    @input="handleInput"
                    @keydown="handleKeydown"
                    @focus="open"
                    class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-[#54cb9b] focus:ring-1 focus:ring-[#54cb9b] focus:outline-none bg-white"
                    :placeholder="placeholder"
                    autocomplete="off"
                />
                
                <div class="absolute inset-y-0 right-0 flex items-center px-2 text-gray-400 pointer-events-none">
                    <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </div>

                <div v-if="isOpen" class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto" ref="listRef">
                    <ul class="py-1">
                        <li 
                            v-if="allowCreate"
                            @click="triggerCreate"
                            class="px-3 py-2 text-sm text-[#54cb9b] font-bold hover:bg-green-50 cursor-pointer border-b border-gray-100 flex items-center gap-2"
                        >
                            <span>➕</span> Nuevo (F4)
                        </li>
                        
                        <li v-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-400 italic">
                            No hay coincidencias
                        </li>

                        <template v-for="(opt, index) in filteredOptions" :key="opt.id || index">
                            <!-- Header -->
                            <li v-if="opt._type === 'header'" class="px-3 py-1 text-[10px] font-bold text-gray-400 bg-gray-50 uppercase tracking-wider border-b border-gray-100 mt-1 first:mt-0">
                                {{ opt.label }}
                            </li>
                            
                            <!-- Option -->
                            <li 
                                v-else
                                :data-index="index"
                                data-selectable="true"
                                @click="selectOption(opt)"
                                class="px-3 py-2 text-sm cursor-pointer transition-colors flex justify-between items-center"
                                :class="{'bg-[#54cb9b] text-white': index === highlightedIndex, 'text-gray-700 hover:bg-gray-100': index !== highlightedIndex}"
                                @mouseenter="highlightedIndex = index"
                            >
                                <div class="flex items-center gap-2">
                                    <span v-if="opt._isPriority" class="text-xs">⭐</span>
                                    <span v-if="opt.sku" class="text-[10px] font-mono bg-gray-100 text-gray-500 px-1 rounded border border-gray-200" :class="{'bg-white/20 text-white border-white/30': index === highlightedIndex}">{{ opt.sku }}</span>
                                    <span>{{ opt.nombre || opt.descripcion }}</span>
                                </div>
                                <span v-if="opt.id === modelValue" class="text-xs font-bold" :class="index === highlightedIndex ? 'text-white' : 'text-[#54cb9b]'">✓</span>
                            </li>
                        </template>
                    </ul>
                </div>
            </div>
            
            <button 
                v-if="allowCreate"
                @click="triggerCreate"
                class="px-3 py-2 bg-gray-100 border border-gray-300 rounded text-gray-600 hover:bg-gray-200 hover:text-gray-800 transition-colors font-bold text-sm flex items-center justify-center"
                title="Crear Nuevo (F4)"
                type="button"
                tabindex="-1"
            >
                [+]
            </button>
        </div>
    </div>
</template>
