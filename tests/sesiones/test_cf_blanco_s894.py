r"""S894, Carlos 28/10: «Es un error que un cliente Consumidor Final se trate como Rosa. Esa clasificación es legal y obliga a tratar al comprador
como B y depositar el IVA; es tan blanco a los efectos contables como un Responsable Inscripto». Caso real: Genesis Bag S.A. cargada como CF; al
guardar su domicilio, ClienteService._audit_sovereignty le prendió la medalla Rosa (Bit 19: «CF/Genéricos siempre tienen soberanía base (Rosa)»)
y nunca se apagaba. Ahora: un CF (por condición o por los CUIT 00000000000 y 11111111119) no recibe ni el Bit 19 ni el sello Rosa inferido (Bit 4);
la medalla la pierde todo el que no es Rosa; el CUIT reservado 11111111111 sigue siendo Rosa siempre. Las dos reglas de color de las pantallas,
igual. Sobre una COPIA de la base de P del 28/10 12:52 (antes de que Tomy corrigiera a Genesis con la lupa de ARCA)."""
import sys, os
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app   # carga todos los modelos
from backend.clientes.models import Cliente
from backend.clientes.service import ClienteService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261028_1252.db"
T = os.path.join(RAIZ, "scratch", "test_cf_blanco_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); s = sessionmaker(bind=eng)()
B4, B19 = 16, 524288
def cliente(nombre): return s.query(Cliente).filter(Cliente.razon_social == nombre).one()
def auditar(cl):
    ClienteService._audit_sovereignty(cl); return int(cl.flags_estado or 0)

g = cliente("GENESIS BAG S.A.")
check(f"partida: Genesis Bag cargada como Consumidor Final, nivel 13, sin la medalla todavía ({g.flags_estado})",
      "CONSUMIDOR FINAL" in g.condicion_iva.nombre.upper() and int(g.flags_estado) & 15 == 13 and not int(g.flags_estado) & B19)
f = auditar(g)
check(f"Genesis (CF con CUIT de S.A.): al recalcular NO recibe la medalla Rosa ({f}); antes la recibía por ser CF", not f & B19 and not f & B4)
g.flags_estado = int(g.flags_estado) | B19
check("y si arrastra la medalla de antes, la pierde al recalcular", not auditar(g) & B19)

mm = cliente("M&M ODONTOLÓGICOS LA PLATA")
check(f"CF con el CUIT genérico de CF (11111111119) y medalla vieja: la pierde ({auditar(mm)})", not int(mm.flags_estado) & B19)
de = cliente("DELICIA ALDERETES")
antes = int(de.flags_estado)
f = auditar(de)
check(f"CF 11111111119 sin Gold y con sello Rosa puesto antes: pierde la medalla; el sello (Bit 4) no lo toca la regla ({antes} -> {f})",
      not f & B19 and (f & B4) == (antes & B4))
de.flags_estado = int(de.flags_estado) & ~B4
check("y un CF 11111111119 sin Gold ya no recibe el sello Rosa inferido (Arlequín): tenía segmento y «sin CUIT real»", not auditar(de) & B4)

pao = cliente("Pao Tandil")
check(f"un Rosa de verdad (nivel 11, lista y segmento) conserva la medalla ({auditar(pao)})", int(pao.flags_estado) & B19)
r = Cliente(razon_social="ROSA RESERVADO PRUEBA", cuit="11111111111", flags_estado=13, condicion_iva=g.condicion_iva)
check(f"el CUIT reservado 11111111111 es Rosa siempre, aunque diga Consumidor Final ({auditar(r)})", int(r.flags_estado) & B19 and int(r.flags_estado) & B4)
if r in s: s.expunge(r)
s.rollback(); s.close(); eng.dispose()
try: os.remove(T)
except Exception: pass

ficha = open(os.path.join(RAIZ, "frontend", "src", "views", "Hawe", "ClientCanvas.vue"), encoding="utf-8").read()
lista = open(os.path.join(RAIZ, "frontend", "src", "views", "HaweView.vue"), encoding="utf-8").read()
for nombre, src, ret in (("la ficha del cliente", ficha, "'pink'"), ("la lista de clientes", lista, "'PINK'")):
    check(f"{nombre}: un CF no se pinta Rosa (ni por condición, ni por CUIT de CF, ni por medalla vieja); el 11111111111 sí",
          "const esCfBlanco = (isConsumidorFinal || ['00000000000', '11111111119'].includes(cuit)) && cuit !== '11111111111';" in src
          and "((flags & 524288) && !esCfBlanco)" in src and "cuit === '11111111111'" in src and "isGeneric || isConsumidorFinal ||" not in src)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
