# [IDENTIDAD] - scripts/sincronizar_historial_notas.py
"""
Sincronización de Historial de Notas — Espejo de Pedidos
Lee HISTORIAL_NOTAS_{ENTORNO}_A.csv / _B.csv en el Silo, aplica los pendientes
como append a Pedidos.nota, y marca las filas como sincronizadas.

Invocado por ALFA al arrancar en MT (o por Carlos a pedido) — no es un canal
de escritura de uso diario. Sin dependencia de openpyxl (csv estándar).

Uso:
  python scripts/sincronizar_historial_notas.py --check   # solo lectura, reporta pendientes
  python scripts/sincronizar_historial_notas.py --apply   # aplica — llamar solo tras PIN 1974
                                                            # ya confirmado por quien invoca

LIMITACIÓN CONOCIDA Y ACEPTADA: un número de pedido mal tipeado que coincida por
casualidad con otro pedido real no se detecta — no hay forma de distinguir un typo
válido de una referencia real usando solo el número. Riesgo residual bajo, aceptado
dado el bajo volumen y la naturaleza circunstancial de este canal.
"""
import csv
import os
import sqlite3
import sys
import argparse
from datetime import datetime

from _env_db import detectar_entorno_db, SILO_DIR

COLUMNAS = ['Pedido', 'Fecha/Hora', 'Nota', 'Sincronizado']


def _archivos_historial(entorno):
    """
    Los archivos oficiales viven en Q:\\...\\Silo\\P\\ — la carpeta sigue al dato
    (contenido real de producción/MT), no al código que lo genera. Corregido de
    B\\ a P\\ en S850 tras crear la carpeta P\\ para lo específico de MT.
    """
    carpeta = os.path.join(SILO_DIR, 'P')
    return [
        os.path.join(carpeta, f'HISTORIAL_NOTAS_{entorno}_A.csv'),
        os.path.join(carpeta, f'HISTORIAL_NOTAS_{entorno}_B.csv'),
    ]


def _leer_csv(path):
    if not os.path.isfile(path):
        return []
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def _escribir_csv(path, filas):
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        writer.writeheader()
        for fila in filas:
            writer.writerow({k: fila.get(k, '') for k in COLUMNAS})


def _asegurar_csv(path):
    """Crea el archivo con header si no existe. No destructivo — no toca uno existente."""
    if not os.path.isfile(path):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            _escribir_csv(path, [])
        except PermissionError:
            pass  # no bloquea la verificación — se reintenta en la próxima corrida


def verificar_pendientes(archivos=None):
    """
    Solo lectura (salvo scaffold inicial del CSV si falta). Retorna:
      {
        'pendientes': [ {pedido, fecha_hora, nota, ubicaciones: [(archivo, fila_idx), ...]}, ... ],
        'huerfanos':  [ {pedido, fecha_hora, nota, ubicaciones: [...]}, ... ],  # Pedido no encontrado en DB
        'db_path': str, 'entorno': str,
      }
    Deduplica por (pedido, fecha/hora, nota) entre A y B — TODAS las ubicaciones donde
    aparece la misma clave se agrupan juntas, para poder marcar Sincronizado en cada
    una al aplicar (si solo se marcara la primera ocurrencia, la fila del otro archivo
    reaparecería como pendiente en la próxima corrida y duplicaría la nota en la DB).

    `archivos`: lista opcional de paths a usar en vez de los oficiales
    (`_archivos_historial(entorno)`) — para pruebas dirigidas a un CSV de test sin
    tocar el mecanismo real. Por defecto (None) usa siempre los archivos oficiales.
    """
    db_path, entorno = detectar_entorno_db()
    lista_archivos = archivos if archivos is not None else _archivos_historial(entorno)

    agrupados = {}   # clave -> {pedido, fecha_hora, nota, ubicaciones: [(archivo, idx), ...]}
    for archivo in lista_archivos:
        _asegurar_csv(archivo)
        filas = _leer_csv(archivo)
        for idx, fila in enumerate(filas):
            pedido       = (fila.get('Pedido') or '').strip()
            fecha_hora   = (fila.get('Fecha/Hora') or '').strip()
            nota         = (fila.get('Nota') or '').strip()
            sincronizado = (fila.get('Sincronizado') or '').strip()

            if sincronizado or not pedido or not nota:
                continue

            clave = (pedido, fecha_hora, nota)
            if clave not in agrupados:
                agrupados[clave] = {
                    'pedido': pedido,
                    'fecha_hora': fecha_hora,
                    'nota': nota,
                    'ubicaciones': [],
                }
            agrupados[clave]['ubicaciones'].append((archivo, idx))

    pendientes, huerfanos = [], []
    candidatos = list(agrupados.values())
    if candidatos and os.path.isfile(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for c in candidatos:
            try:
                pid = int(c['pedido'])
            except ValueError:
                huerfanos.append(c)
                continue
            cur.execute('SELECT id FROM pedidos WHERE id = ?', (pid,))
            if cur.fetchone():
                pendientes.append(c)
            else:
                huerfanos.append(c)
        conn.close()
    elif candidatos:
        huerfanos.extend(candidatos)

    return {'pendientes': pendientes, 'huerfanos': huerfanos, 'db_path': db_path, 'entorno': entorno}


def aplicar_sincronizacion(archivos=None):
    """
    Aplica los pendientes válidos: UPDATE pedidos.nota (append) + marca Sincronizado
    en el CSV de origen. No pide confirmación propia — se asume que quien invoca
    (ALFA, tras PIN 1974) ya autorizó la operación.

    `archivos`: ver verificar_pendientes() — mismo mecanismo de override para pruebas.
    """
    resultado = verificar_pendientes(archivos=archivos)
    pendientes = resultado['pendientes']
    db_path = resultado['db_path']

    if not pendientes:
        return {'aplicados': [], 'huerfanos': resultado['huerfanos']}

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    ts_sync = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    aplicados = []

    for p in pendientes:
        pid = int(p['pedido'])
        etiqueta_fecha = p['fecha_hora'] or ts_sync
        linea = f"\n[{etiqueta_fecha}] {p['nota']}"
        cur.execute(
            "UPDATE pedidos SET nota = COALESCE(nota, '') || ? WHERE id = ?",
            (linea, pid)
        )
        aplicados.append(p)

    conn.commit()
    conn.close()

    # Marcar Sincronizado en TODAS las ubicaciones de cada nota aplicada (A y B si
    # la misma clave apareció duplicada en ambos archivos — ver nota en verificar_pendientes).
    por_archivo = {}
    for p in aplicados:
        for archivo, idx in p['ubicaciones']:
            por_archivo.setdefault(archivo, []).append(idx)

    for archivo, idxs in por_archivo.items():
        filas = _leer_csv(archivo)
        for idx in idxs:
            if idx < len(filas):
                filas[idx]['Sincronizado'] = ts_sync
        try:
            _escribir_csv(archivo, filas)
        except PermissionError:
            print(f'[WARN] No se pudo marcar Sincronizado en {os.path.basename(archivo)} '
                  f'(archivo bloqueado). Los datos SI se aplicaron a la DB. '
                  f'El marcado se reintentará en la próxima corrida.')

    return {'aplicados': aplicados, 'huerfanos': resultado['huerfanos']}


def _reporte_texto(resultado):
    pendientes = resultado['pendientes']
    huerfanos = resultado['huerfanos']
    if not pendientes and not huerfanos:
        return None

    lineas = ['[HISTORIAL DE NOTAS] Pendientes de sincronizar:']
    for p in pendientes:
        lineas.append(f"  - Pedido {p['pedido']} | {p['fecha_hora'] or '(sin fecha)'} | {p['nota'][:80]}")
    if huerfanos:
        lineas.append('[HISTORIAL DE NOTAS] Filas con Pedido no encontrado en la DB (revisar a mano, NO se aplican):')
        for h in huerfanos:
            archivos = ', '.join(os.path.basename(a) for a, _ in h['ubicaciones'])
            lineas.append(f"  - '{h['pedido']}' | {h['fecha_hora'] or '(sin fecha)'} | "
                          f"{h['nota'][:80]} (archivo: {archivos})")
    lineas.append('[HISTORIAL DE NOTAS] Limitación conocida y aceptada: un número de pedido mal '
                  'tipeado que coincida por casualidad con otro pedido real no se detecta. '
                  'Riesgo residual bajo, aceptado por bajo volumen y uso circunstancial del canal.')
    return '\n'.join(lineas)


def main():
    parser = argparse.ArgumentParser(description='Sincronizar Historial de Notas del Espejo de Pedidos')
    parser.add_argument('--check', action='store_true', help='Solo lectura — reporta pendientes')
    parser.add_argument('--apply', action='store_true',
                        help='Aplica pendientes a la DB (requiere PIN 1974 ya confirmado por quien invoca)')
    args = parser.parse_args()

    if args.apply:
        resultado = aplicar_sincronizacion()
        if not resultado['aplicados']:
            print('[HISTORIAL DE NOTAS] Nada para aplicar.')
            sys.exit(0)
        print(f"[OK] {len(resultado['aplicados'])} nota(s) aplicada(s) a Pedidos.nota:")
        for a in resultado['aplicados']:
            print(f"  - Pedido {a['pedido']}: {a['nota'][:80]}")
        if resultado['huerfanos']:
            print(f"[WARN] {len(resultado['huerfanos'])} fila(s) con Pedido no encontrado — sin aplicar, revisar a mano.")
        sys.exit(0)

    # Default: --check (o sin flags)
    resultado = verificar_pendientes()
    texto = _reporte_texto(resultado)
    if texto:
        print(texto)
        sys.exit(2)   # código de salida distinto de 0 → hay pendientes (para detección fácil desde ALFA)
    sys.exit(0)


if __name__ == '__main__':
    main()
