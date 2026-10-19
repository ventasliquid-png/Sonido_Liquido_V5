# Pruebas de las sesiones S876 a S888 (47 pruebas, 1.101 comprobaciones)

Versionadas en la S888 por la auditoría de CA (H1 y H2 del 15/10): hasta entonces vivían en la carpeta temporal de una sesión de Claude Code y se perdían con ella.
Son **scripts independientes** (no pytest): cada uno imprime `[OK]`/`[FAIL]` por comprobación y termina con `RESULTADO: n/m checks OK` y código de salida 0 o 1.

## Cómo correrlas
- **Todas contra D:** `backend\venv\Scripts\python.exe tests\sesiones\correr_en_D.py` (tarda unos minutos). La lista y los resultados esperados salen de `PRUEBAS` en `correr_en_B.py`.
- **Todas contra el código del clon de B** (`C:\dev\_porte_B_ensayo\current`): `backend\venv\Scripts\python.exe tests\sesiones\correr_en_B.py`. Reescribe solo las rutas de entrada de cada prueba (`sys.path.insert` y `os.chdir`) y compara con lo que dieron en D. La prueba del espejo mensual apunta a la raíz de B (`scripts/`), que es donde vive ese script.
- **Una sola:** `backend\venv\Scripts\python.exe tests\sesiones\test_guardia_roles_s885.py` (cwd = la raíz de D).

## Lo que suponen (rutas fijas de OF)
- D en `C:\dev\Sonido_Liquido_V5` y su `backend\venv`; el clon de B en `C:\dev\_porte_B_ensayo`; el Silo en `Q:\Mi unidad\V5_Silo_Claude`. En otra PC hay que ajustar `RAIZ`, `PY` y la ruta del Silo.
- **30 pruebas parten de una copia de la base de P** que está en el Silo (`BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_AAAAMMDD_HHMM.db`, el nombre exacto está en cada archivo): trabajan sobre una copia temporal dentro de `scratch\` (ignorada por git) y nunca escriben en el Silo ni en P.
- `nc_sintetica.py` es un auxiliar de `test_etapa7d_nc_nd.py` (arma una nota de crédito sintética): tiene que estar en la misma carpeta.
- Tres pruebas (`test_etapa7b`, `7c`, `7d`) entran con el usuario `admin` de la copia de prueba (clave de desarrollo conocida, ya presente en el historial del repo).
- Las pruebas estáticas de pantalla leen los `.vue` de `frontend\src` (en B, de `current\frontend\src`).

## Qué cubre cada una
Los nombres llevan la sesión o la Card (`_s876` … `_s887`, `etapa7b`…). Para saber qué verifica una, leer el docstring de su primera línea. Las de la S887: `test_espejo_mensual_s887` (18), `test_remitos_ui_s887` (27), `test_remito_existente_s887` (15) y `test_remito_existente_ui_s887` (17). De la S888: `test_renglones_duplicados_s888` (21; Card #179: dos renglones del mismo producto en el Remito Manual y en la ingesta parcial; agrega renglones a los pedidos 48, 123 y 82 de la copia de P). Kits del pedido (Card #177 v3): `test_migrate_063_s888` (12; la columna `pedidos_items.kit_grupo`, sobre la copia CRUDA) y `test_kit_grupo_s888` (60; el bit ES_KIT que calcula el servidor, el reparto del precio del kit y las guardas de renglón facturado).

## El ayudante `_esquema_p.py` (S888)
Cuando el modelo declara una columna nueva, toda consulta ORM sobre una copia VIEJA de P falla con «no such column». Las pruebas que copian una base de P usan `copiar_p(origen, destino)` en vez de `shutil.copyfile`: copia y le agrega a la COPIA las columnas posteriores a ese backup (hoy `pedidos_items.kit_grupo`). Si una migración futura suma una columna al modelo, se agrega a `COLUMNAS_NUEVAS` en ese archivo (una sola vez para todas). Las pruebas de migración parten de la copia cruda a propósito.
