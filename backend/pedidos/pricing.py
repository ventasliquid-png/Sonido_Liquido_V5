from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.productos.models import Producto
from backend.clientes.models import Cliente
from backend.maestros.models import ListaPrecios, TasaIVA

# --- CONSTANTES DE ESCENARIOS (FACTORES K) ---
# K = Multiplicador sobre la BASE (Costo + PUB)
# Base = CostoReposicion * (1 + (MargenMayorista/100))

SCENARIOS = {
    'MAYORISTA_FISCAL': {
        'k_factor': Decimal('1.21'), # +IVA 21%
        'descripcion': 'Precio Mayorista con Factura A/B',
        'iva_implicito': Decimal('0.21')
    },
    'MAYORISTA_X': {
        'k_factor': Decimal('1.105'), # +10.5% (IVA Compartido)
        'descripcion': 'Precio Mayorista Interno (X)',
        'iva_implicito': Decimal('0.105')
    },
    'CF_LOCAL': {
        'k_factor': Decimal('1.573'), # (Base * 1.21) * 1.30 (+30% sobre el Iva Incluido) 
        # Matematica: 1.21 * 1.30 = 1.573
        'descripcion': 'Consumidor Final Mostrador'
    },
    'MELI_CLASICO': {
        'markup': Decimal('1.40'), # +40%
        'costo_fijo': Decimal('2100.00'),
        'base_iva': True, # Aplica sobre precio con IVA
        'descripcion': 'MercadoLibre Clásico'
    }
}

class PricingEngine:
    def __init__(self, db: Session):
        self.db = db

    def cotizar_producto(self, cliente_id: str, producto_id: int, cantidad: float = 1.0) -> Dict:
        """
        Calcula el precio sugerido para un producto/cliente específico
        usando la logica 'La Roca y La Máscara'.
        """
        # 1. Recuperar Entidades
        cliente = self.db.query(Cliente).get(cliente_id)
        producto = self.db.query(Producto).get(producto_id)
        
        if not cliente or not producto:
            return {"error": "Entidades no encontradas"}

        # 2. Determinar "La Roca" (Precio Base)
        # Jerarquía: PrecioFijoOverride > (Costo * PUB Producto) > (Costo * PUB General)
        
        costos = producto.costos
        if not costos:
             # Fallback si no hay registro de costos
             return self._respuesta_error("E001", "Producto sin estructura de costos", 0)

        precio_fijo = costos.precio_fijo_override
        costo_repo = costos.costo_reposicion or Decimal('0')
        margen = costos.margen_mayorista or Decimal('0') # Ej: 30.00
        
        es_override = False
        precio_base_rock = Decimal('0')

        if precio_fijo and precio_fijo > 0:
            # PRIORIDAD DIVINA
            precio_base_rock = precio_fijo
            es_override = True
        else:
            # FORMULA STANDARD
            # Rock = Costo * (1 + Margin%)
            if costo_repo == 0:
                return self._respuesta_error("E002", "Costo Cero - Requiere precio manual", 0, alerta=True)
            
            # Margen numerico (ej 30) a factor (1.30)
            factor_margen = Decimal('1') + (margen / Decimal('100'))
            precio_base_rock = costo_repo * factor_margen

        # 3. Aplicar Escenario (Sabor del Cliente)
        estrategia = cliente.estrategia_precio or 'MAYORISTA_FISCAL'
        scenario_config = SCENARIOS.get(estrategia, SCENARIOS['MAYORISTA_FISCAL'])
        
        precio_objetivo = Decimal('0')
        
        if 'k_factor' in scenario_config:
            # Multiplicador Directo
            precio_objetivo = precio_base_rock * scenario_config['k_factor']
        elif 'markup' in scenario_config:
            # Logica Compuesta (Ej MELI)
            base_calc = precio_base_rock
            if scenario_config.get('base_iva'):
                base_calc = base_calc * Decimal('1.21')
            
            precio_objetivo = (base_calc * scenario_config['markup']) + scenario_config.get('costo_fijo', 0)

        # 4. Redondeo Inteligente
        precio_objetivo = self._aplicar_redondeo(precio_objetivo)

        # 5. La Máscara (Ingeniería Inversa de Lista)
        # Si el cliente tiene lista con descuento (ej: Coef 0.80 -> 20% OFF),
        # mostramos un Precio de Lista inflado para que ((Lista * 0.80) == Objetivo)
        
        lista_coef = Decimal('1.0')
        if cliente.lista_precios:
            # Asumimos que coef almacenado es el multiplicador final (ej 0.90 es 10% off)
            lista_coef = cliente.lista_precios.coeficiente or Decimal('1.0')

        if lista_coef == 0: lista_coef = Decimal('1.0') # Evitar div zero

        # Precio Vidriera (Lista)
        # Objetivo = Vidriera * Coef
        # Vidriera = Objetivo / Coef
        precio_vidriera = precio_objetivo / lista_coef
        
        # Redondear Vidriera tambien para que se vea bonito
        precio_vidriera = self._aplicar_redondeo(precio_vidriera)
        
        # Recalcular un poquito el objetivo final real basado en la vidriera redondeada
        precio_final_real = precio_vidriera * lista_coef

        return {
            "producto_id": producto.id,
            "estrategia": estrategia,
            "origen": "OVERRIDE" if es_override else "FORMULA",
            "costo_base": float(costo_repo),
            "precio_lista_sugerido": float(precio_vidriera), # La Máscara
            "descuento_aplicado": float((1 - lista_coef) * 100),
            "precio_final_sugerido": float(precio_final_real), # Bolsillo
            "alerta": False,
            "info_debug": f"Rock: {precio_base_rock:.2f} | K: {scenario_config.get('k_factor', 0)}"
        }

    def _respuesta_error(self, codigo, msg, precio, alerta=False):
        return {
            "error_code": codigo,
            "mensaje": msg,
            "precio_final_sugerido": precio,
            "alerta": alerta
        }

    def _aplicar_redondeo(self, valor: Decimal) -> Decimal:
        """
        Regla Kiosco: < 1000 redondear a 10.
        Regla Boutique: > 1000 redondear a 100.
        """
        # Convertir a entero para analizar magnitud
        if valor < 1000:
            # Redondeo a 10
            # Ej: 112 -> 110, 118 -> 120
           return Decimal(round(valor / 10) * 10)
        else:
            # Redondeo a 100
            # Ej: 1240 -> 1200, 1260 -> 1300
            return Decimal(round(valor / 100) * 100)
