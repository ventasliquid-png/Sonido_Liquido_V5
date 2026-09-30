// [S876] CUIT genéricos: no identifican a nadie (consumidor final, mostrador, contingencia AFIP). Mismo
// listado que backend/clientes/constants.py GENERIC_CUITS -- si cambia allá, cambia acá. Un remito con
// uno de estos CUIT nunca imprime el número (cualquier remito, no solo Rosa).
export const GENERIC_CUITS = ['00000000000', '11111111119', '11111111111', '99999999999'];

// Acepta el CUIT con o sin guiones.
export const esCuitGenerico = (cuit) => GENERIC_CUITS.includes(String(cuit ?? '').replace(/\D/g, ''));
