<template>
    <div class="flex h-full w-full bg-[#0e1f12] text-white overflow-hidden relative">
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-10 pointer-events-none">
            <div class="absolute top-0 left-0 w-full h-full" style="background-image: radial-gradient(#22c55e 1px, transparent 1px); background-size: 40px 40px;"></div>
        </div>

        <div class="flex-1 flex flex-col items-center justify-center p-8 z-10">
            <div class="bg-black/20 backdrop-blur-sm p-12 rounded-2xl border border-emerald-500/30 text-center shadow-2xl max-w-lg">
                <div class="w-24 h-24 bg-emerald-900/30 rounded-full flex items-center justify-center mx-auto mb-6 ring-4 ring-emerald-500/20">
                    <i class="fas fa-hard-hat text-5xl text-emerald-400"></i>
                </div>
                
                <h1 class="text-3xl font-bold text-white mb-2 font-outfit">Módulo Pedidos</h1>
                <p class="text-emerald-400/80 uppercase tracking-widest text-sm font-bold mb-6">En Construcción</p>
                
                <p class="text-gray-400 mb-8 leading-relaxed">
                    Estamos preparando el lienzo para la gestión inteligente de pedidos. 
                    Pronto podrás centralizar aquí todas las solicitudes.
                </p>

                <div class="flex gap-4 justify-center">
                    <button class="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors font-medium shadow-lg shadow-emerald-900/50">
                        <i class="fas fa-bell mr-2"></i> Notificarme
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
</script>
