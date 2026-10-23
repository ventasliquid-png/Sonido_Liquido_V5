// [S892] Búsqueda sin acentos ni mayúsculas: «lacteos» encuentra «Lácteos» (Carlos, 23/10, buscando los pedidos de Lácteos de Poblet
// en el Tablero). Una sola función para todos los buscadores: antes había diez copias sueltas y la mitad de los buscadores no la usaba.
export const normalizarBusqueda = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
