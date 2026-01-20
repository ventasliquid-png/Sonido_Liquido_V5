<template>
  <div v-if="stats" class="w-full bg-[#0a151b] border-b border-cyan-900/30 px-6 py-3 flex items-center justify-between shrink-0 h-20 shadow-xl z-20">
    
    <!-- Left: Stats Ticker -->
    <div class="flex items-center gap-8 text-xs font-outfit uppercase tracking-widest text-white/50">
        
        <!-- Clientes -->
        <div 
            class="flex items-center gap-3 group cursor-pointer hover:text-cyan-400 transition-colors select-none"
            @dblclick="router.push({ name: 'HaweHome' })"
            title="Doble click para ir a Clientes"
        >
            <div class="h-8 w-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-500 group-hover:scale-110 transition-transform">
                <i class="fas fa-users"></i>
            </div>
            <div>
                <p class="text-[9px] mb-0.5">Clientes</p>
                <div class="flex items-baseline gap-1">
                    <span class="text-lg font-bold text-white">{{ stats.clientes.active }}</span>
                    <span class="text-[9px] text-cyan-500/50">/ {{ stats.clientes.total }}</span>
                </div>
            </div>
        </div>

        <div class="h-8 w-px bg-white/5"></div>

        <!-- Productos -->
        <div 
            class="flex items-center gap-3 group cursor-pointer hover:text-emerald-400 transition-colors select-none"
            @dblclick="router.push({ name: 'Productos' })"
             title="Doble click para ir a Productos"
        >
            <div class="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
                <i class="fas fa-box"></i>
            </div>
            <div>
                <p class="text-[9px] mb-0.5">Productos</p>
                <div class="flex items-baseline gap-1">
                    <span class="text-lg font-bold text-white">{{ stats.productos.total }}</span>
                    <span class="text-[9px] text-emerald-500/50">SKUs</span>
                </div>
            </div>
        </div>

        <div class="h-8 w-px bg-white/5"></div>

        <!-- Pedidos -->
        <div 
            class="flex items-center gap-3 group cursor-pointer hover:text-amber-400 transition-colors select-none"
            @dblclick="router.push({ name: 'PedidoList' })"
             title="Doble click para ir a Pedidos"
        >
             <div class="h-8 w-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-500 group-hover:scale-110 transition-transform">
                <i class="fas fa-clipboard-list"></i>
            </div>
             <div>
                <p class="text-[9px] mb-0.5">Pedidos Hoy</p>
                <div class="flex items-baseline gap-1">
                     <span class="text-lg font-bold text-white">{{ stats.pedidos.pending }}</span>
                     <span class="text-[9px] text-amber-500/50">Pendientes</span>
                </div>
             </div>
        </div>
    </div>

    <!-- Right: Context Info -->
    <div class="flex items-center gap-3">
         <div class="text-right hidden sm:block">
            <p class="text-xs font-bold text-white">Administración</p>
            <p class="text-[10px] text-white/40">Modo Táctico</p>
         </div>
         <div class="h-8 w-8 rounded-full bg-cyan-600 flex items-center justify-center text-xs font-bold ring-2 ring-black">G</div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import statsService from '../../services/statsService'

const stats = ref(null)
const router = useRouter()

onMounted(async () => {
    try {
        const res = await statsService.getDashboardStats()
        stats.value = res.data
    } catch (e) {
        console.error("Stats Bar Error:", e)
    }
})
</script>
