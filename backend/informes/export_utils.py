# backend/informes/export_utils.py
"""
Motor de exportación compartido del módulo Informes (S875,
DISENO_MODULO_INFORMES_S875_2026-09-26.md §2.2).

Recibe columnas + filas -- nunca un informe particular -- y devuelve CSV/Excel/PDF/TXT.
Se escribe una sola vez; los cinco informes de Nivel 1 y los de Nivel 2 lo reusan sin tocarlo.

`columnas`: lista de dicts {"key": "...", "label": "...", "width": opcional (Excel/PDF)}
`filas`: lista de dicts, cada uno con al menos las claves de `columnas` (ausentes -> vacío).
"""
import csv
import io
import unicodedata
from typing import Callable, List, Dict, Any, Optional

from fastapi.responses import StreamingResponse


def _valor(fila: Dict[str, Any], key: str) -> Any:
    v = fila.get(key)
    return "" if v is None else v


def _nombre_archivo(titulo: str, extension: str) -> str:
    seguro = "".join(c if (c.isalnum() or c in "-_") else "_" for c in titulo)
    return f"{seguro}.{extension}"


def exportar_csv(titulo: str, columnas: List[Dict], filas: List[Dict]) -> StreamingResponse:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([c["label"] for c in columnas])
    for fila in filas:
        writer.writerow([_valor(fila, c["key"]) for c in columnas])
    contenido = "﻿" + buf.getvalue()  # BOM -- Excel abre UTF-8 con acentos sin romperse
    return StreamingResponse(
        iter([contenido]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_nombre_archivo(titulo, "csv")}"'},
    )


def exportar_excel(titulo: str, columnas: List[Dict], filas: List[Dict]) -> StreamingResponse:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = (titulo or "Informe")[:31]  # límite de Excel para nombres de hoja

    for col_idx, col in enumerate(columnas, 1):
        celda = ws.cell(row=1, column=col_idx, value=col["label"])
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="1E3A8A")

    for row_idx, fila in enumerate(filas, 2):
        for col_idx, col in enumerate(columnas, 1):
            ws.cell(row=row_idx, column=col_idx, value=_valor(fila, col["key"]) or None)

    for col_idx, col in enumerate(columnas, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = col.get("width", 18)
    ws.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{_nombre_archivo(titulo, "xlsx")}"'},
    )


def exportar_pdf(titulo: str, columnas: List[Dict], filas: List[Dict]) -> StreamingResponse:
    from backend.remitos.remito_engine import PDFRemito

    safe = PDFRemito._pdf_safe
    orientacion = "L" if len(columnas) > 5 else "P"
    pdf = PDFRemito(orientation=orientacion)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, safe(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 6, safe(f"{len(filas)} fila(s)"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    ancho_pagina = pdf.w - 2 * pdf.l_margin
    ancho_col = ancho_pagina / len(columnas)

    def _header():
        pdf.set_font("Arial", "B", 8)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        for col in columnas:
            pdf.cell(ancho_col, 7, safe(col["label"]), border=1, fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 7)

    _header()
    for i, fila in enumerate(filas):
        if pdf.get_y() > pdf.h - 20:
            pdf.add_page()
            _header()
        for col in columnas:
            texto = safe(str(_valor(fila, col["key"])))
            pdf.cell(ancho_col, 6, texto[:60], border=1)
        pdf.ln()

    salida = bytes(pdf.output())
    return StreamingResponse(
        io.BytesIO(salida),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_nombre_archivo(titulo, "pdf")}"'},
    )


def exportar_txt(
    titulo: str,
    columnas: List[Dict],
    filas: List[Dict],
    formato_linea: Optional[Callable[[Dict], str]] = None,
) -> StreamingResponse:
    """Lista para leer o pegar (WhatsApp/mail), no una tabla -- un resultado por
    párrafo, en texto corrido. `formato_linea` permite que un informe (ej. E) arme
    su propio párrafo legible en vez del volcado genérico clave: valor."""
    buf = io.StringIO()
    buf.write(f"{titulo}\n{'=' * len(titulo)}\n\n")
    for fila in filas:
        if formato_linea:
            buf.write(formato_linea(fila) + "\n\n")
        else:
            partes = [f"{c['label']}: {_valor(fila, c['key'])}" for c in columnas]
            buf.write(" | ".join(partes) + "\n\n")
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_nombre_archivo(titulo, "txt")}"'},
    )


EXPORTADORES = {
    "csv": exportar_csv,
    "excel": exportar_excel,
    "pdf": exportar_pdf,
    "txt": exportar_txt,
}


def exportar(formato: str, titulo: str, columnas: List[Dict], filas: List[Dict], **kwargs) -> StreamingResponse:
    fn = EXPORTADORES.get(formato)
    if not fn:
        raise ValueError(f"Formato de exportación desconocido: {formato}")
    if formato == "txt":
        return fn(titulo, columnas, filas, formato_linea=kwargs.get("formato_linea"))
    return fn(titulo, columnas, filas)


def normalizar_texto(valor: Optional[str]) -> str:
    """[Informe E] Saca acentos para comparar sin distinguirlos (á->a, ñ->n, etc.)
    -- unicodedata, sin dependencia nueva. 'medico' debe encontrar 'médico'."""
    if not valor:
        return ""
    forma = unicodedata.normalize("NFKD", valor)
    return "".join(c for c in forma if not unicodedata.combining(c)).lower()
