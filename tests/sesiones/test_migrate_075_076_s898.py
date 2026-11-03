r"""S898, Card #144 (parser de ARCA ignoraba la bonificacion, CRITICA). El codigo ya estaba en produccion desde la S894; faltaban los DATOS que habian quedado guardados sin bonificar.
migrate_075 corrige los renglones de seis facturas (2549, 2589, 2601, 2616, 2617, 2620: Centro Pet y Wullich, 5 % por renglon; valores de los PDF de ARCA) para que el renglon sume el neto de la
factura; migrate_076 le agrega al pedido #94 de Centro Pet la bonificacion del 5 % que le faltaba para igualar a su factura 2582 (decision de Carlos: «el precio de la factura es el correcto»).
Sobre una COPIA de la base de P del 02/11 16:40 (estado previo a las dos migraciones); el arranque de P las aplica con auto_migrar."""
import sys, os, sqlite3, subprocess, hashlib
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261102_1640.db"
SEIS = (2549, 2589, 2601, 2616, 2617, 2620)
BONIFICADAS = (2534, 2549, 2574, 2582, 2589, 2601, 2616, 2617, 2620)
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); copiar_p(ORIG, p); return p
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(db, sql, *a):
    con = sqlite3.connect(db); con.execute(sql, a); con.commit(); con.close()
def correr(db, script):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", script)], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
def huella(db, sql, *a):
    return hashlib.md5(repr(q(db, sql, *a)).encode("utf-8")).hexdigest()
def renglon(db, n):
    return q(db, "select i.cantidad, i.precio_unitario_neto, i.subtotal_neto from facturas_items i join facturas f on f.id=i.factura_id where f.numero_comprobante=? order by i.id", n)
def suma_cierra(db, n):
    s = sum(r[2] or 0 for r in renglon(db, n)); neto = q(db, "select neto_gravado from facturas where numero_comprobante=?", n)[0][0]
    return abs(s - neto) < 0.02
F_SIN_NOTAS = "select id, cliente_id, pedido_id, tipo_comprobante, punto_venta, numero_comprobante, estado, neto_gravado, iva_21, iva_105, exento, percepciones, total, cae, flags_estado from facturas order by id"
ITEMS_OTRAS = "select * from facturas_items where factura_id not in (select id from facturas where numero_comprobante in (2549,2589,2601,2616,2617,2620)) order by id"

# ---------- partida ----------
a = copia("t075_a.db")
check("partida: las seis facturas tienen el renglon sin bonificar (no suma el neto) y la 2601 con precio 0; las otras tres bonificadas ya cierran",
      all(not suma_cierra(a, n) for n in SEIS) and renglon(a, 2601) == [(360.0, 0.0, 0.0)] and all(suma_cierra(a, n) for n in (2534, 2574, 2582)))
check("partida: el pedido #94 tiene 120 x 11.600 sin descuento y total 1.684.320; la factura 2582 da 1.600.104",
      q(a, "select total from pedidos where id='94'") == [(1684320.0,)] and q(a, "select cantidad, precio_unitario, descuento_porcentaje, subtotal from pedidos_items where pedido_id='94'") == [(120.0, 11600.0, 0.0, 1392000.0)]
      and q(a, "select total from facturas where numero_comprobante=2582") == [(1600104.0,)])
h_fact, h_otras, h_ped, h_pitems, h_rem = (huella(a, F_SIN_NOTAS), huella(a, ITEMS_OTRAS), huella(a, "select * from pedidos order by id"),
                                           huella(a, "select * from pedidos_items order by id"), huella(a, "select * from remitos order by id"))
notas_antes = {n: q(a, "select notas_auditoria from facturas where numero_comprobante=?", n)[0][0] for n in BONIFICADAS}

# ---------- migrate_075 ----------
rc, out = correr(a, "migrate_075_renglones_facturas_bonificadas.py")
check(f"migrate_075 sale 0 y dice que corrigio las seis [{rc}]", rc == 0 and "corregidas 6" in out and "saltadas 0" in out and "con error 0" in out and "075_renglones_facturas_bonificadas registrada" in out)
esperado = {2549: (240.0, 11020.0, 2644800.0), 2589: (240.0, 11020.0, 2644800.0), 2601: (360.0, 11020.0, 3967200.0), 2616: (360.0, 11020.0, 3967200.0), 2617: (5.0, 44080.0, 220400.0), 2620: (144.0, 11020.0, 1586880.0)}
check("cada renglón queda con el precio por unidad ya bonificado y el subtotal que imprime ARCA (11.020 x 240, 11.020 x 360, 44.080 x 5, 11.020 x 144)", all(renglon(a, n) == [v] for n, v in esperado.items()))
check("con eso, el renglón de las NUEVE facturas bonificadas suma el neto de su factura", all(suma_cierra(a, n) for n in BONIFICADAS))
check("neto, IVA, percepciones, total, estado y CAE de TODAS las facturas no cambian; tampoco los renglones de las demás facturas", huella(a, F_SIN_NOTAS) == h_fact and huella(a, ITEMS_OTRAS) == h_otras)
check("no toca pedidos, renglones de pedido ni remitos", huella(a, "select * from pedidos order by id") == h_ped and huella(a, "select * from pedidos_items order by id") == h_pitems and huella(a, "select * from remitos order by id") == h_rem)
notas_desp = {n: q(a, "select notas_auditoria from facturas where numero_comprobante=?", n)[0][0] for n in BONIFICADAS}
check("las seis llevan una línea [SISTEMA] con el antes y el después (sin perder las notas anteriores); las otras tres, intactas",
      all((notas_desp[n] or "").startswith(notas_antes[n] or "") and "migrate_075, Card #144" in notas_desp[n] for n in SEIS) and all(notas_desp[n] == notas_antes[n] for n in (2534, 2574, 2582)))
check("la 2617 (bidón de 5 litros) dice 5 x 46.400,00 = 232.000,00 -> 5 x 44.080,00 = 220.400,00", "5 x 46,400.00 = 232,000.00 -> 5 x 44,080.00 = 220,400.00" in notas_desp[2617])
dump = (q(a, "select * from facturas_items order by id"), q(a, "select id, notas_auditoria from facturas order by id"))
rc2, out2 = correr(a, "migrate_075_renglones_facturas_bonificadas.py")
check(f"segunda corrida: SKIP, sale 0 y la base no cambia [{rc2}]", rc2 == 0 and "SKIP" in out2 and (q(a, "select * from facturas_items order by id"), q(a, "select id, notas_auditoria from facturas order by id")) == dump)
x(a, "delete from _migraciones_aplicadas where id='075_renglones_facturas_bonificadas'")
rc3, out3 = correr(a, "migrate_075_renglones_facturas_bonificadas.py")
check(f"aun sin el registro, lo ya corregido se reconoce («ya estaba como ARCA») y no se duplica la nota [{rc3}]",
      rc3 == 0 and "corregidas 0" in out3 and "ya estaban bien 6" in out3 and (q(a, "select * from facturas_items order by id"), q(a, "select id, notas_auditoria from facturas order by id")) == dump)

# ---------- guardas de migrate_075 ----------
b = copia("t075_b.db")
x(b, "update facturas_items set precio_unitario_neto=11000 where factura_id=(select id from facturas where numero_comprobante=2549)")                 # el renglon no es el auditado
x(b, "update facturas set neto_gravado=3967201 where numero_comprobante=2616")                                                                       # el neto no es el de ARCA
x(b, "insert into facturas_items (factura_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto) select id, 'otro', 1, 10, 21, 10 from facturas where numero_comprobante=2617")  # dos renglones
rc, out = correr(b, "migrate_075_renglones_facturas_bonificadas.py")
check(f"si una factura no esta como se audito (renglon distinto, neto distinto, dos renglones) se la informa y NO se toca; las otras tres se corrigen y la migracion sale 0 [{rc}]",
      rc == 0 and "corregidas 3" in out and "saltadas 3" in out and renglon(b, 2549) == [(240.0, 11000.0, 2784000.0)] and renglon(b, 2616) == [(360.0, 11600.0, 4176000.0)] and len(renglon(b, 2617)) == 2
      and all(renglon(b, n) == [esperado[n]] for n in (2589, 2601, 2620)))

# ---------- migrate_076 ----------
c = copia("t076_c.db")
OTROS = ("select * from pedidos where id != '94' order by id", "select * from pedidos_items where pedido_id != '94' order by id", "select * from facturas order by id",
         "select * from facturas_items order by id", "select * from remitos order by id", "select * from remitos_items order by id")
h_otros = [huella(c, s) for s in OTROS]
rc, out = correr(c, "migrate_076_pedido_94_bonificacion.py")
check(f"migrate_076 sale 0 y corrige el pedido #94 [{rc}]", rc == 0 and "OK -- pedido #94" in out and "076_pedido_94_bonificacion registrada (corregido)" in out)
check("el renglón del #94 queda 120 x 11.600 con 5 % (descuento 69.600), subtotal 1.322.400 y el pedido en 1.600.104, igual a la factura 2582; sigue CUMPLIDO",
      q(c, "select cantidad, precio_unitario, descuento_porcentaje, descuento_importe, subtotal from pedidos_items where pedido_id='94'") == [(120.0, 11600.0, 5.0, 69600.0, 1322400.0)]
      and q(c, "select total, estado from pedidos where id='94'") == [(1600104.0, "CUMPLIDO")] and q(c, "select total from facturas where numero_comprobante=2582") == [(1600104.0,)])
check("el pedido #94 lleva una nota [SISTEMA] con el antes y el después", "migrate_076, Card #144" in q(c, "select nota from pedidos where id='94'")[0][0] and "1,684,320.00 -> 1,600,104.00" in q(c, "select nota from pedidos where id='94'")[0][0])
check("no toca ningún otro pedido, renglón de pedido, factura (con sus notas), renglón de factura ni remito", [huella(c, s) for s in OTROS] == h_otros)
d94 = (q(c, "select total, nota from pedidos where id='94'"), q(c, "select * from pedidos_items where pedido_id='94'"))
rc2, out2 = correr(c, "migrate_076_pedido_94_bonificacion.py")
check(f"segunda corrida: SKIP, sale 0 y el #94 no cambia [{rc2}]", rc2 == 0 and "SKIP" in out2 and (q(c, "select total, nota from pedidos where id='94'"), q(c, "select * from pedidos_items where pedido_id='94'")) == d94)
x(c, "delete from _migraciones_aplicadas where id='076_pedido_94_bonificacion'")
rc3, out3 = correr(c, "migrate_076_pedido_94_bonificacion.py")
check(f"aun sin el registro, si el #94 ya está como la factura lo reconoce y no duplica la nota [{rc3}]", rc3 == 0 and "ya tiene la bonificacion" in out3 and (q(c, "select total, nota from pedidos where id='94'"), q(c, "select * from pedidos_items where pedido_id='94'")) == d94)
e = copia("t076_e.db")
x(e, "update pedidos_items set precio_unitario=12000 where pedido_id='94'")
rc, out = correr(e, "migrate_076_pedido_94_bonificacion.py")
check(f"si el #94 no esta como se audito (otro precio), se lo informa y no se toca [{rc}]", rc == 0 and "AVISO" in out and q(e, "select total from pedidos where id='94'") == [(1684320.0,)] and q(e, "select descuento_porcentaje from pedidos_items where pedido_id='94'") == [(0.0,)])

# ---------- el arranque de P las descubre solo ----------
# OJO: NO se corre auto_migrar.py en una prueba: lee DATABASE_URL del .env del proyecto (no de la variable de entorno) y migraria la base de desarrollo de D (pilot_v5x.db).
# Se comprueba, sin ejecutarlo, que lo que lee auto_migrar (solo texto) incluye las dos migraciones y que sobre la copia de P son las unicas nuevas de la serie 07x.
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
disp = dict(auto_migrar.migraciones_disponibles())
aplicadas = {row[0] for row in q(ORIG, "select id from _migraciones_aplicadas")}
pend07x = sorted(m for m in disp if m >= "070" and m not in aplicadas)
check("auto_migrar (el arranque de P) descubre la 075 y la 076, y sobre la base de P de hoy son las unicas migraciones nuevas de la serie 07x",
      pend07x == ["075_renglones_facturas_bonificadas", "076_pedido_94_bonificacion"] and disp["075_renglones_facturas_bonificadas"].endswith("migrate_075_renglones_facturas_bonificadas.py"))
check("y la 075 va antes que la 076 en el orden en que las corre", [m for m in sorted(disp, key=lambda m: os.path.basename(disp[m])) if m >= "075"] == ["075_renglones_facturas_bonificadas", "076_pedido_94_bonificacion"])
for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith(("t075_", "t076_")):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
