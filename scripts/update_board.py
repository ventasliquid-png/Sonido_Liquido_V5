"""
update_board.py -- aplica actualizaciones y altas de cards en BOARD_V5.xlsx,
hoja "Board V5" explicita.

Fix Card #93 (2026-08-15, S855-CA): `wb.active` apuntaba a CSV_DUMP_ARCHIVADO en
vez de Board V5 -- causo al menos una perdida de registro confirmada (Card #102)
y es sospechoso de otra (dos entregas de S834 sin rastro). Ahora la hoja se
selecciona por nombre explicito y el guardado se verifica por relectura.

Es un MODULO DE BIBLIOTECA a proposito: no tiene `updates` hardcodeado en el
cuerpo y correrlo directo no escribe nada. La version anterior conservaba un
dict de S842 (cards 47/48/52/53) que, corrido mas tarde, habria cerrado la
Card #53 -- abierta -- con hashes de julio y fecha del dia. Esa clase de
escritura silenciosa es justamente lo que la Card #93 vino a erradicar.

Uso:
    import sys; sys.path.insert(0, "scripts")
    from update_board import aplicar_actualizaciones, agregar_cards
    aplicar_actualizaciones({93: {"Estado": "CERRADA", "Comentarios": "..."}})
    agregar_cards([{"ID": 116, "Título": "...", ...}])
"""
import openpyxl
from datetime import datetime

FILE_PATH = r"Q:\Mi unidad\V5_Silo_Claude\BOARD_V5.xlsx"
SHEET_NAME = "Board V5"


DIRECT_FIELDS = ("Título", "Tipo", "Prioridad", "Módulo", "Versión", "Estado",
                  "Fecha_cierre", "Depende_de", "Fecha_creacion",
                  # Ranking (S868): el barrido los carga con Q:\...\V5_Silo_Claude\board_barrido.py,
                  # que valida la escala y los temas. Acá solo se escriben tal cual.
                  "Toca", "Temas", "Daña", "Repite", "Bloquea", "Redescubierta")


def _get_col_map(ws):
    header_row_idx = 1
    for r in range(1, 10):
        if ws.cell(row=r, column=1).value == "ID":
            header_row_idx = r
            break
    col_map = {}
    for idx, cell in enumerate(ws[header_row_idx]):
        col_map[cell.value] = idx + 1
    return header_row_idx, col_map


def aplicar_actualizaciones(updates: dict) -> int:
    """
    updates: {card_id: {campo: valor, ...}}
    Campos directos (sobrescriben): Título, Tipo, Prioridad, Módulo, Versión,
    Estado, Fecha_cierre, Depende_de, Fecha_creacion, Toca, Temas, Daña, Repite,
    Bloquea, Redescubierta.
    Campos especiales sobre Comentarios (se pueden combinar, se aplican en
    este orden): "Comentarios_replace": (viejo, nuevo) substring dentro del
    comentario existente; "Comentarios_prepend": texto antes del existente;
    "Comentarios": texto agregado (append) al final.
    Devuelve la cantidad de cards actualizadas. Imprime una verificacion por
    relectura despues de guardar (Card #93).
    """
    wb = openpyxl.load_workbook(FILE_PATH)
    ws = wb[SHEET_NAME]  # Card #93: NUNCA wb.active -- apunta a CSV_DUMP_ARCHIVADO,
                         # ya se comio 2 registros (Card #102, dos cards de S834) en silencio.
    header_row_idx, col_map = _get_col_map(ws)
    comentarios_col = col_map.get("Comentarios")
    id_col = col_map.get("ID")

    updated_rows = {}
    for row in range(header_row_idx + 1, ws.max_row + 1):
        cell_id = ws.cell(row=row, column=id_col).value
        match_key = cell_id if cell_id in updates else str(cell_id) if str(cell_id) in updates else None
        if match_key is None:
            continue
        data = updates[match_key]

        for field in DIRECT_FIELDS:
            if field in data:
                ws.cell(row=row, column=col_map[field]).value = data[field]

        current = ws.cell(row=row, column=comentarios_col).value or ""
        if "Comentarios_replace" in data:
            old, new = data["Comentarios_replace"]
            current = current.replace(old, new)
        if "Comentarios_prepend" in data:
            current = f"{data['Comentarios_prepend']}\n{current}" if current else data["Comentarios_prepend"]
        if "Comentarios" in data:
            current = f"{current}\n{data['Comentarios']}" if current else data["Comentarios"]
        if any(k in data for k in ("Comentarios_replace", "Comentarios_prepend", "Comentarios")):
            ws.cell(row=row, column=comentarios_col).value = current

        updated_rows[match_key] = row

    wb.save(FILE_PATH)
    _verificar(updated_ids=list(updated_rows.keys()), esperado_estado={k: updates[k].get("Estado") for k in updated_rows})
    return len(updated_rows)


def agregar_cards(cards: list) -> int:
    """
    cards: lista de dicts con las columnas del Board (ID incluido; desde S868 tambien Toca, Temas,
    Daña, Repite, Bloquea y Redescubierta -- una card nace rankeada, ver ALFA.md).
    Agrega filas nuevas al final de "Board V5". No toca filas existentes.
    """
    wb = openpyxl.load_workbook(FILE_PATH)
    ws = wb[SHEET_NAME]  # Card #93: NUNCA wb.active -- ver nota en aplicar_actualizaciones.
    header_row_idx, col_map = _get_col_map(ws)

    start_row = ws.max_row + 1
    for i, card in enumerate(cards):
        row = start_row + i
        for field, col in col_map.items():
            ws.cell(row=row, column=col).value = card.get(field)

    wb.save(FILE_PATH)
    nuevos_ids = [c["ID"] for c in cards]
    _verificar(updated_ids=nuevos_ids, esperado_estado={c["ID"]: c.get("Estado") for c in cards})
    return len(cards)


def _verificar(updated_ids, esperado_estado, esperado_max_row=None, esperado_max_row_otra=None):
    """Reabre el archivo desde disco (no reusa wb en memoria) y confirma que
    los IDs tocados están en 'Board V5' con el Estado esperado, y que
    CSV_DUMP_ARCHIVADO no se movió (Card #93)."""
    wb_check = openpyxl.load_workbook(FILE_PATH, data_only=True)
    ws_check = wb_check[SHEET_NAME]
    ws_otra = wb_check["CSV_DUMP_ARCHIVADO"]
    _, col_map = _get_col_map(ws_check)
    id_col, estado_col = col_map["ID"], col_map["Estado"]

    id_to_row = {}
    for row in range(2, ws_check.max_row + 1):
        val = ws_check.cell(row=row, column=id_col).value
        if val is not None:
            id_to_row[str(val)] = row

    ok = True
    for uid in updated_ids:
        row = id_to_row.get(str(uid))
        if row is None:
            print(f"Card #{uid}: NO ENCONTRADA en '{SHEET_NAME}' tras guardar -- MISMATCH")
            ok = False
            continue
        real_estado = ws_check.cell(row=row, column=estado_col).value
        expected = esperado_estado.get(uid)
        estado_ok = expected is None or real_estado == expected
        ok = ok and estado_ok
        print(f"Card #{uid}: fila {row} en '{SHEET_NAME}' -> Estado='{real_estado}' {'OK' if estado_ok else 'MISMATCH'}")

    print(f"'{SHEET_NAME}' max_row tras guardar: {ws_check.max_row}" + (f" (esperado {esperado_max_row})" if esperado_max_row else ""))
    print(f"'CSV_DUMP_ARCHIVADO' max_row (no debe cambiar): {ws_otra.max_row}" + (f" (esperado {esperado_max_row_otra})" if esperado_max_row_otra else ""))
    if esperado_max_row is not None:
        ok = ok and ws_check.max_row == esperado_max_row
    if esperado_max_row_otra is not None:
        ok = ok and ws_otra.max_row == esperado_max_row_otra
    print(f"Verificacion {'OK' if ok else 'FALLO'}")
    return ok


if __name__ == "__main__":
    print("Modulo de biblioteca -- importar aplicar_actualizaciones/agregar_cards desde otro script.")
