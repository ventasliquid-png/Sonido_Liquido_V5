#!/usr/bin/env python
"""
asignar_facturas_a_pedidos.py -- Propuesta de asignacion de las facturas emitidas (PDF de ARCA + CSV oficial) a los pedidos de V5 (S882, plan de saneamiento).

SOLO LECTURA: abre la base con mode=ro y escribe unicamente el Excel de salida. No decide nada: propone, con el motivo y el grado de confianza, y
deja la decision a Carlos. Reutiliza la lectura de PDF y de V5 de scripts/auditoria_facturas.py.

Para cada comprobante emitido (desde --desde) busca, entre los pedidos del MISMO cliente (por CUIT), el mas probable segun:
  - productos del PDF que existen en el pedido (clave canonica / parecido con medidas exactas),
  - cantidades iguales (o menores: facturacion parcial),
  - total del comprobante == total del pedido,
  - cercania de fechas (la factura suele ser del mismo dia o posterior al pedido).
Confianza: ALTA (puntaje alto y claramente por encima del segundo), MEDIA, BAJA (revisar a mano), SIN_PEDIDO (el cliente no existe en V5 o no hay pedido).
Las notas de credito se emparejan con la factura que anulan (mismo cliente, total igual o menor, fecha posterior) y heredan su pedido.

Uso: python scripts/asignar_facturas_a_pedidos.py --db <copia_de_P.db> --pdf <carpeta> [--pdf ...] [--arca-csv x.csv] --salida informe.xlsx
"""
import argparse
import datetime
import os
import re
import sqlite3
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))

import auditoria_facturas as af  # noqa: E402
from backend.productos.normalizacion import normalizar_producto, similitud, UMBRAL_SUGERENCIA  # noqa: E402


def cargar_pedidos(db):
    """pedidos no anulados con su cliente (CUIT), renglones y facturas que V5 ya les asigna."""
    por_cuit = defaultdict(list)
    cuit_de = {}
    for cid, cuit, razon in db.execute("select id, cuit, razon_social from clientes"):
        cuit_de[cid] = (re.sub(r"\D", "", str(cuit or "")), razon)
    facturas_v5 = defaultdict(list)
    for pid, num, cae, total, tipo in db.execute("select pedido_id, numero_comprobante, cae, total, tipo_comprobante from facturas where cae is not null and trim(cae)!=''"):
        if pid is not None:
            facturas_v5[str(pid)].append((num, total, tipo))
    for pid, cid, fecha, total, estado, tipo_f, origen in db.execute(
            "select id, cliente_id, fecha, total, estado, tipo_facturacion, origen from pedidos where estado != 'ANULADO'"):
        cuit, razon = cuit_de.get(cid, ("", ""))
        items = [{"id": i, "nombre": n, "cant": q or 0.0, "precio": p or 0.0}
                 for i, n, q, p in db.execute("select pi.id, pr.nombre, pi.cantidad, pi.precio_unitario from pedidos_items pi join productos pr on pr.id=pi.producto_id where pi.pedido_id=? order by pi.id", (pid,))]
        por_cuit[cuit].append({"id": pid, "fecha": str(fecha)[:10], "total": total or 0.0, "estado": estado, "tipo_fact": tipo_f, "origen": origen,
                               "razon": razon, "items": items, "facturas_v5": facturas_v5.get(str(pid), [])})
    return por_cuit, cuit_de


def puntuar(doc, ped):
    """-> (puntaje 0..100, motivos). Ver el docstring del modulo."""
    usados, prod_ok, qty_ok = set(), 0, 0
    for it in doc["items"]:
        mejor, mejor_s = None, 0.0
        for ln in ped["items"]:
            if ln["id"] in usados:
                continue
            s = 1.0 if normalizar_producto(ln["nombre"]) == normalizar_producto(it["descripcion"]) else similitud(ln["nombre"], it["descripcion"])
            if s > mejor_s:
                mejor, mejor_s = ln, s
        if mejor is not None and mejor_s >= UMBRAL_SUGERENCIA:
            usados.add(mejor["id"]); prod_ok += 1
            if abs(mejor["cant"] - it["cantidad"]) <= 0.001:
                qty_ok += 1
    n = max(len(doc["items"]), 1)
    prod_frac, qty_frac = prod_ok / n, qty_ok / n
    total_igual = doc["total"] is not None and abs(ped["total"] - doc["total"]) <= 1.0
    try:
        d = (datetime.date.fromisoformat(doc["fecha"]) - datetime.date.fromisoformat(ped["fecha"])).days
    except ValueError:
        d = None
    if d is None:
        f_score = 0.0
    elif 0 <= d <= 3:
        f_score = 1.0
    elif -3 <= d < 0 or 3 < d <= 15:
        f_score = 0.7
    elif 15 < d <= 45:
        f_score = 0.4
    else:
        f_score = 0.1
    puntaje = 40 * prod_frac + 20 * qty_frac + 25 * (1 if total_igual else 0) + 15 * f_score
    motivos = []
    if prod_ok:
        motivos.append(f"{prod_ok}/{len(doc['items'])} productos")
    if qty_ok:
        motivos.append(f"{qty_ok} cantidades iguales")
    if total_igual:
        motivos.append("total igual")
    if d is not None:
        motivos.append(f"{d:+d} dias")
    # el pedido ya esta cubierto por otras facturas de V5: mala señal
    otras = [f for f in ped["facturas_v5"] if f[0] != doc["numero"]]
    if otras and sum(f[1] or 0 for f in otras) + (doc["total"] or 0) > ped["total"] * 1.01 + 1:
        puntaje -= 25
        motivos.append("OJO: ya tiene " + ",".join(str(f[0]) for f in otras))
    return max(puntaje, 0.0), motivos


def main():
    ap = argparse.ArgumentParser(description="Propuesta de asignacion de facturas emitidas a pedidos de V5 (solo lectura).")
    ap.add_argument("--db", required=True)
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--arca-csv")
    ap.add_argument("--desde", default="2026-01-01")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()

    db = sqlite3.connect("file:" + os.path.abspath(a.db).replace("\\", "/") + "?mode=ro", uri=True)
    docs, _ = af.recolectar_pdf(db, a.pdf, a.desde)
    v5, duplicadas = af.leer_v5(db, a.desde)
    arca = af.leer_csv_arca(a.arca_csv, a.desde) if a.arca_csv else []
    por_cuit, cuit_de = cargar_pedidos(db)
    clientes_por_cuit = {c: r for c, r in cuit_de.values() if c}
    primera_v5 = min((x["fecha"] for x in v5.values() if x["fecha"]), default="9999")
    primer_pedido = db.execute("select min(substr(fecha,1,10)) from pedidos").fetchone()[0]

    # NOTAS DE CREDITO primero: una factura anulada por una NC no "gasta" el total del pedido (patron: factura, NC, factura nueva por el mismo pedido)
    nc_aplicada, nc_de = defaultdict(float), {}
    facturas_docs = {k: d for k, d in docs.items() if not d["tipo"].startswith("NOTA_CREDITO")}
    for k, nc in sorted(((k, d) for k, d in docs.items() if d["tipo"].startswith("NOTA_CREDITO")), key=lambda kd: kd[1]["fecha"]):
        cands = [(fk, fd) for fk, fd in facturas_docs.items() if fd["cuit"] == nc["cuit"] and fd["fecha"] <= nc["fecha"]
                 and (fd["total"] or 0) - nc_aplicada[fk] >= (nc["total"] or 0) - 1]
        exactas = [c for c in cands if abs((c[1]["total"] or 0) - nc_aplicada[c[0]] - (nc["total"] or 0)) <= 1]
        elegido = max(exactas or cands, key=lambda c: c[1]["fecha"], default=None)
        if elegido:
            nc_aplicada[elegido[0]] += nc["total"] or 0
            nc_de[k] = (elegido[0], bool(exactas))

    propuestas = []   # una por documento
    pendientes = {}   # clave -> (base, doc, candidatos) de las facturas que compiten por un pedido
    for (pv, nro, cae), doc in sorted(docs.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        es_nc = doc["tipo"].startswith("NOTA_CREDITO")
        v = v5.get((pv, nro, cae))
        link_actual = v["pedido_id"] if v else None
        base = {"doc": doc, "numero": f"{pv:05d}-{nro:08d}", "es_nc": es_nc, "en_v5": bool(v), "link_actual": link_actual, "duplicada": (pv, nro, cae) in duplicadas, "clave": (pv, nro, cae)}
        if es_nc:
            propuestas.append({**base, "pedido": None, "confianza": "NC", "puntaje": 0, "motivos": [], "alternativas": [], "accion": "NC: emparejar con la factura que anula (abajo)"})
            continue
        if doc["fecha"] < primer_pedido:
            propuestas.append({**base, "pedido": None, "confianza": "ANTERIOR_A_V5", "puntaje": 0, "motivos": [f"emitida {doc['fecha']}; el primer pedido de V5 es del {primer_pedido}"],
                               "alternativas": [], "accion": "historia previa a V5: no hay pedido que asignar"})
            continue
        if not doc["cuit"] or doc["cuit"] not in clientes_por_cuit:
            propuestas.append({**base, "pedido": None, "confianza": "SIN_PEDIDO", "puntaje": 0, "motivos": ["el cliente no existe en V5"], "alternativas": [],
                               "accion": "alta del cliente + pedido retroactivo (contra natura) o dejar fuera de V5"})
            continue
        candidatos = []
        for ped in por_cuit.get(doc["cuit"], []):
            pt, mot = puntuar(doc, ped)
            if pt >= 20:
                candidatos.append((pt, mot, ped))
        candidatos.sort(key=lambda c: -c[0])
        pendientes[base["clave"]] = (base, doc, candidatos)

    # REPARTO GLOBAL: cada pedido cubre solo lo que su total admite; entre pedidos parecidos gana el mas cercano (antes de la factura)
    capacidad = {p_["id"]: p_["total"] + 1.0 for lista in por_cuit.values() for p_ in lista}
    pares = []
    for clave, (base, doc, cands) in pendientes.items():
        for pt, mot, ped in cands:
            if pt >= 40:
                try:
                    d = (datetime.date.fromisoformat(doc["fecha"]) - datetime.date.fromisoformat(ped["fecha"])).days
                except ValueError:
                    d = 999
                pares.append((-pt, d if d >= 0 else abs(d) + 30, clave, ped["id"]))
    pares.sort()
    asignado = {}
    por_id = {p_["id"]: p_ for lista in por_cuit.values() for p_ in lista}
    for neg, _prox, clave, pid in pares:
        if clave in asignado:
            continue
        doc = pendientes[clave][1]
        consumo = max((doc["total"] or 0) - nc_aplicada.get(clave, 0.0), 0.0)   # neto de las NC que la anulan
        if consumo <= capacidad[pid] + 0.5:
            asignado[clave] = (por_id[pid], -neg)
            capacidad[pid] -= consumo
    for clave, (base, doc, cands) in pendientes.items():
        v = v5.get(clave)
        if clave in asignado:
            ped, pt = asignado[clave]
            mot = next(m for s_, m, p_ in cands if p_["id"] == ped["id"])
            parecidos = [p_ for s_, m, p_ in cands if p_["id"] != ped["id"] and s_ >= pt - 5]
            if pt >= 80 and not parecidos:
                conf = "ALTA"
            elif pt >= 55:
                conf = "MEDIA"
            else:
                conf = "BAJA"
            if parecidos and conf == "ALTA":
                conf = "MEDIA"
            alts = [f"#{p_['id']} ({s_:.0f})" for s_, m, p_ in cands if p_["id"] != ped["id"]][:3]
            if parecidos:
                mot = mot + [f"AMBIGUO: pedidos parecidos {', '.join('#' + str(p_['id']) for p_ in parecidos)}; se eligio por fecha"]
            acc = {"ALTA": "asignar", "MEDIA": "revisar y asignar", "BAJA": "revisar a mano"}[conf]
            if v and str(base["link_actual"]) != str(ped["id"]):
                acc = f"CORREGIR el enlace actual (#{base['link_actual']}) -> #{ped['id']}"
            propuestas.append({**base, "pedido": ped, "confianza": conf, "puntaje": pt, "motivos": mot, "alternativas": alts, "accion": acc})
        else:
            mejor = cands[0] if cands else None
            if mejor and mejor[0] >= 40:
                nota = [f"los pedidos que se le parecen ya estan cubiertos por otras facturas ({', '.join('#' + str(p_['id']) for s_, m, p_ in cands[:3])})"]
            else:
                nota = ["el cliente existe pero ningun pedido se le parece"]
            propuestas.append({**base, "pedido": None, "confianza": "SIN_PEDIDO", "puntaje": 0, "motivos": nota, "alternativas": [f"#{p_['id']} ({s_:.0f})" for s_, m, p_ in cands[:3]],
                               "accion": "pedido retroactivo (contra natura) o dejar fuera de V5"})

    # notas de credito: heredan el pedido de la factura que anulan
    por_clave = {p_["clave"]: p_ for p_ in propuestas}
    for p_ in propuestas:
        if not p_["es_nc"]:
            continue
        par = nc_de.get(p_["clave"])
        if par:
            f = por_clave.get(par[0])
            p_["pedido"] = f["pedido"] if f else None
            p_["motivos"] = [("anula toda la factura " if par[1] else "anula parte de la factura ") + f["numero"] + f" ({f['doc']['fecha']}, ${f['doc']['total']:,.0f})"]
            p_["confianza"] = "NC_EMPAREJADA" if par[1] else "NC_PARCIAL"
            p_["accion"] = "registrar la NC y descontar del facturado de " + (f"pedido #{f['pedido']['id']}" if f and f["pedido"] else "(factura sin pedido)")
        else:
            p_["confianza"] = "NC_SIN_FACTURA"
            p_["accion"] = "no se encontro la factura que anula (puede ser anterior a 2026)"

    # pedidos sin ninguna factura asignada
    asignados = {str(p["pedido"]["id"]) for p in propuestas if p["pedido"] is not None and not p["es_nc"] and p["confianza"] in ("ALTA", "MEDIA", "BAJA")}
    asignados |= {str(x["pedido_id"]) for x in v5.values() if x["pedido_id"] is not None}
    sin_factura = []
    for cuit, peds in por_cuit.items():
        for ped in peds:
            if str(ped["id"]) not in asignados and ped["fecha"] >= "2026-01-01":
                sin_factura.append(ped)
    sin_factura.sort(key=lambda p: int(p["id"]))

    # ---------------- Excel
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    gris = PatternFill("solid", fgColor="EDEDED")
    col = {"ALTA": "E2F0D9", "MEDIA": "FFF2CC", "BAJA": "FCE4D6", "SIN_PEDIDO": "F8CBAD", "ANTERIOR_A_V5": "EDEDED", "NC_EMPAREJADA": "DDEBF7", "NC_PARCIAL": "DDEBF7", "NC_SIN_FACTURA": "F8CBAD", "NC": "DDEBF7"}
    ws = wb.active; ws.title = "RESUMEN"
    cuenta = defaultdict(int)
    for p in propuestas:
        cuenta[p["confianza"]] += 1
    ws.append(["Propuesta de asignacion de facturas a pedidos -- " + datetime.date.today().isoformat() + " -- SOLO LECTURA"]); ws["A1"].font = Font(bold=True, size=13)
    ws.append([f"Base: {os.path.basename(a.db)} | emitidas desde {a.desde} | comprobantes con PDF: {len(docs)} | del CSV de ARCA: {len(arca)} | primer pedido de V5: {primer_pedido}"])
    ws.append([])
    for k in ("ALTA", "MEDIA", "BAJA", "SIN_PEDIDO", "ANTERIOR_A_V5", "NC_EMPAREJADA", "NC_PARCIAL", "NC_SIN_FACTURA"):
        if cuenta.get(k):
            ws.append([k, cuenta[k]])
    ws.append([]); ws.append(["Pedidos de 2026 sin ninguna factura (ni en V5 ni propuesta)", len(sin_factura)])
    ws.append([]); ws.append(["ALTA = producto, cantidad, total y fecha apuntan a un solo pedido. MEDIA = probable, a confirmar. BAJA = revisar a mano. SIN_PEDIDO = ningun pedido (o el cliente no existe en V5). Nada se asigno: es una propuesta."])
    ws.column_dimensions["A"].width = 62
    h = wb.create_sheet("PROPUESTA")
    h.append(["Confianza", "Factura", "Tipo", "Fecha", "Cliente", "Total ARCA", "Estado en V5", "Enlace actual en V5", "Pedido propuesto", "Fecha pedido", "Total pedido", "Estado pedido",
              "Puntaje", "Motivos", "Otros candidatos", "Accion propuesta", "Duplicada en V5"])
    for c in h[1]:
        c.font = Font(bold=True); c.fill = gris; c.alignment = Alignment(wrap_text=True, vertical="top")
    for p in sorted(propuestas, key=lambda p: (["ALTA", "MEDIA", "BAJA", "SIN_PEDIDO", "NC_EMPAREJADA", "NC_PARCIAL", "NC_SIN_FACTURA", "NC", "ANTERIOR_A_V5"].index(p["confianza"]), p["numero"])):
        d, ped = p["doc"], p["pedido"]
        h.append([p["confianza"], p["numero"], d["tipo"], d["fecha"], d["receptor"], d["total"], "en V5" if p["en_v5"] else "NO esta en V5", p["link_actual"],
                  f"#{ped['id']}" if ped else None, ped["fecha"] if ped else None, ped["total"] if ped else None, ped["estado"] if ped else None,
                  round(p["puntaje"]), "; ".join(p["motivos"]), ", ".join(p["alternativas"]), p["accion"], "SI" if p["duplicada"] else ""])
        h.cell(row=h.max_row, column=1).fill = PatternFill("solid", fgColor=col.get(p["confianza"], "FFFFFF"))
    for i, w in enumerate([15, 16, 16, 11, 34, 14, 14, 12, 12, 11, 14, 13, 8, 60, 28, 56, 9], start=1):
        h.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    h.freeze_panes = "C2"
    s = wb.create_sheet("PEDIDOS_SIN_FACTURA")
    s.append(["Pedido", "Fecha", "Cliente", "Total", "Estado", "Tipo facturacion", "Origen", "Renglones"])
    for c in s[1]:
        c.font = Font(bold=True); c.fill = gris
    for p in sin_factura:
        s.append([int(p["id"]), p["fecha"], p["razon"], p["total"], p["estado"], p["tipo_fact"], p["origen"], "; ".join(f"{i['cant']:g} {i['nombre']}" for i in p["items"])[:200]])
    for i, w in enumerate([8, 11, 36, 14, 13, 16, 12, 100], start=1):
        s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    if arca:
        so = wb.create_sheet("ARCA_SIN_PDF")
        so.append(["Factura", "Tipo", "Fecha", "CUIT", "Receptor", "Total"])
        for r in arca:
            if (r["pv"], r["numero"], r["cae"]) not in docs:
                so.append([f"{r['pv']:05d}-{r['numero']:08d}", r["tipo"], r["fecha"], r["cuit"], r["receptor"], r["total"]])
    wb.save(a.salida)
    print(f"comprobantes analizados: {len(propuestas)} | " + " | ".join(f"{k}: {v}" for k, v in sorted(cuenta.items())))
    print(f"pedidos de 2026 sin factura: {len(sin_factura)} | Informe: {a.salida}")


if __name__ == "__main__":
    main()
