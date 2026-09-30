// [S876] Cómo salió una entrega (Remito.metodo_entrega) y por qué un renglón salió sin ser venta firme
// (RemitoItem.motivo_no_facturable). Las listas son las cerradas de backend/remitos/constants.py
// (METODOS_ENTREGA, MOTIVOS_NO_FACTURABLE): si cambian allá, cambian acá.
//
// No confundir con Domicilio.metodo_entrega / origen_logistico (V5.2 GOLD): esa es la configuración
// HABITUAL de una dirección; esto es el hecho de UNA entrega puntual, congelado al armar el remito.

export const METODOS_ENTREGA = [
    { value: 'MOSTRADOR',         label: 'Mostrador (retiro en planta)',       corto: 'Mostrador',         sinTransporte: true  },
    { value: 'FLETE_TERCERO',     label: 'Flete / transporte de terceros',     corto: 'Flete tercero',     sinTransporte: false },
    { value: 'TRANSPORTE_PROPIO', label: 'Transporte propio',                  corto: 'Transporte propio', sinTransporte: true  },
    { value: 'MOTO_CADETERIA',    label: 'Moto / cadetería',                   corto: 'Moto / cadetería',  sinTransporte: true  },
    { value: 'REMITO_EXTERNO',    label: 'Remito o etiqueta de un tercero (correo, MercadoLibre)', corto: 'Remito externo', sinTransporte: true },
];

export const MOTIVOS_NO_FACTURABLE = [
    { value: 'CONSIGNACION',       label: 'Consignación',          clase: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
    { value: 'MUESTRA_SIN_CARGO',  label: 'Muestra sin cargo',     clase: 'bg-sky-500/20 text-sky-300 border-sky-500/30' },
    { value: 'GARANTIA_REEMPLAZO', label: 'Garantía / reemplazo',  clase: 'bg-violet-500/20 text-violet-300 border-violet-500/30' },
];

export const metodoCorto = (v) => METODOS_ENTREGA.find(m => m.value === v)?.corto || null;
export const metodoLabel = (v) => METODOS_ENTREGA.find(m => m.value === v)?.label || null;
export const motivoLabel = (v) => MOTIVOS_NO_FACTURABLE.find(m => m.value === v)?.label || v || null;
export const motivoClase = (v) => MOTIVOS_NO_FACTURABLE.find(m => m.value === v)?.clase || 'bg-slate-500/20 text-slate-300 border-slate-500/30';

// La oficina (Roseti 1482): domicilio de todo remito de MOSTRADOR. No viaja el texto desde el backend
// porque el remito solo trae el id del domicilio.
export const ETIQUETA_OFICINA = 'Retiro en planta (Roseti 1482)';
