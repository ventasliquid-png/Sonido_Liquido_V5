from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
print("--- [LOAD] Remitos Router (Soberanía Total V5.1) cargado con éxito ---")
from fastapi.responses import FileResponse
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.core.database import get_db
from .pdf_parser import process_pdf_ingestion
from backend.remitos import schemas, models
from backend.auth.dependencies import get_current_active_user
from backend.auth.models import Usuario

router = APIRouter(
    prefix="/remitos",
    tags=["Remitos (Logística)"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.RemitoResponse])
def list_remitos(db: Session = Depends(get_db)):
    """
    Lista todos los remitos del sistema con carga ansiosa y mapeo manual de visualización.
    """
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    
    remitos = db.query(models.Remito).order_by(models.Remito.fecha_creacion.desc()).all()

    return remitos

@router.get("/entregas")
def get_entregas(
    cliente_id: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    producto_id: Optional[int] = None,
    oc: Optional[str] = None,
    incluir_anulados: bool = False,
    db: Session = Depends(get_db),
):
    """
    [Reporte de Entregas — Zona Verde] Filas planas de qué remitos cubrieron qué
    renglón de pedido, más anomalías (remitos huérfanos, sobre-entregas, OC
    repetida entre pedidos, etc). Solo lectura.

    NOTA: esta ruta debe ir ANTES de GET /{remito_id} en este archivo — comparten
    la misma forma de path (un solo segmento) y FastAPI resuelve en orden de
    declaración, así que /{remito_id} la taparía si quedara antes.
    """
    from backend.remitos.service import RemitosService
    return RemitosService.get_entregas(
        db,
        cliente_id=cliente_id,
        desde=desde,
        hasta=hasta,
        producto_id=producto_id,
        oc=oc,
        incluir_anulados=incluir_anulados,
    )

@router.get("/resumen_por_pedido")
def resumen_por_pedido(db: Session = Depends(get_db)):
    """
    [S887, pedido de Carlos 15/10] Los remitos vigentes (sin anulados) de cada pedido, para que el Tablero de Pedidos
    muestre si un pedido ya tiene remito y cuál es, sin tener que buscarlo en el listado de Remitos.
    Devuelve {"<pedido_id>": [{"id", "numero_legal", "estado", "fecha_creacion"}, ...]}; un pedido sin remitos no figura.

    NOTA: va ANTES de GET /{remito_id} (misma forma de path: un solo segmento).
    """
    filas = (db.query(models.Remito)
             .filter(models.Remito.estado != "ANULADO")
             .order_by(models.Remito.fecha_creacion.asc()).all())
    salida = {}
    for r in filas:
        salida.setdefault(str(r.pedido_id), []).append({
            "id": r.id,
            "numero_legal": r.numero_legal,
            "estado": r.estado,
            "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
        })
    return salida

@router.get("/{remito_id}", response_model=schemas.RemitoResponse)
def get_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un remito específico.
    """
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    
    remito = db.query(models.Remito).options(
        joinedload(models.Remito.pedido).joinedload(Pedido.cliente),
        joinedload(models.Remito.items).joinedload(models.RemitoItem.pedido_item).joinedload(PedidoItem.producto)
    ).filter(models.Remito.id == remito_id).first()
    
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    return remito

@router.get("/por_pedido/{pedido_id}", response_model=List[schemas.RemitoResponse])
def get_remitos_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los remitos asociados a un pedido específico.
    """
    return db.query(models.Remito).filter(models.Remito.pedido_id == pedido_id).all()

@router.post("/{remito_id}/despachar", response_model=schemas.RemitoResponse)
def despachar_remito(remito_id: str, payload: schemas.DespacharPayload = schemas.DespacharPayload(), db: Session = Depends(get_db)):
    """
    Cambia el estado del remito a EN_CAMINO, marca la fecha de salida y fija los bultos.
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")

    # [DISENO_CIRCUITO_PR_S869.md §9.3 / §2.4] El modelo documenta aprobado_para_despacho
    # como "GATEKEEPER FINANCIERO": si es False, Depósito no puede pasar a EN_CAMINO. Antes
    # este endpoint no lo consultaba -- la compuerta estaba escrita pero no enchufada.
    if not remito.aprobado_para_despacho:
        raise HTTPException(
            status_code=409,
            detail="DESPACHO_NO_APROBADO: el remito no está aprobado para despacho."
        )

    # [Etapa 3, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §5] "Despachar" exige que ya esté
    # impreso -- no se puede despachar algo que nunca se imprimió. Imprimir y despachar quedan
    # como dos acciones separadas y secuenciales (corrección de Carlos: Tomy imprime con
    # anticipación, el transporte puede pasar días después).
    if not remito.numero_legal:
        raise HTTPException(
            status_code=409,
            detail="REMITO_SIN_IMPRIMIR: el remito todavía no tiene número asignado -- imprimalo antes de despachar."
        )

    remito.estado = "EN_CAMINO"
    # [S890, Carlos 21/10] La fecha de salida se fija cuando el remito toma número (get_remito_pdf): despachar no la pisa.
    if remito.fecha_salida is None:
        remito.fecha_salida = datetime.now()
    if payload.bultos is not None:
        remito.bultos = payload.bultos
    db.commit()
    db.refresh(remito)
    return remito

@router.get("/{remito_id}/pdf")
def get_remito_pdf(remito_id: str, vista_previa: bool = False, db: Session = Depends(get_db)):
    """
    Genera y sirve el PDF de un remito.

    [S891, paquete 2, tramo 2 -- reglas de Carlos y Nike del 20 al 22/10]
    - VISTA PREVIA (`?vista_previa=1`) de un remito SIN número: sale con la marca «VISTA PREVIA - SIN VALIDEZ», no toma número, no
      se marca impreso ni se guarda. Sirve para revisar dirección, cantidades y bultos antes de gastar el número (lo que habría
      atajado el 3031). Un remito con número no tiene vista previa: su papel es la imagen guardada.
    - IMPRIMIR: si no tiene número lo toma (0015). El papel que se genera cuando el remito no tiene imagen guardada queda como LA
      IMAGEN DE LO IMPRESO (DOCUMENTOS_GENERADOS_RAR/Remitos emitidos/): al tomar número, más tarde si salió sin papel con su
      número, o la primera vez que se reimprime un remito de antes de esta regla. Desde ahí, REIMPRIMIR entrega siempre esa misma
      imagen, sin regenerarla: no reprocesa nada y no cambia aunque cambien los datos o las reglas del papel. Cada reimpresión
      deja una nota [SISTEMA].
    - La imagen solo se entrega si el remito ya está IMPRESO (bit 44): el primer papel siempre se genera, aunque haya un archivo
      con ese número (en D lo dejan otras copias de la base). Cambiar la fecha (PATCH /fecha) archiva la imagen: el próximo papel
      sale con la fecha nueva y pasa a ser la imagen.
    """
    import os
    try:
        remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
        if not remito:
            raise HTTPException(status_code=404, detail="Remito no encontrado")

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        carpeta_imagenes = os.path.join(base_dir, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
        es_vista_previa = bool(vista_previa) and not remito.numero_legal
        from backend.remitos.constants import RemitoFlags
        primer_papel = not (int(remito.flags_estado or 0) & int(RemitoFlags.IMPRESO))

        # [Etapa 3, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §5] "Imprimir" es la acción que
        # numera -- no cambia el estado, el remito puede seguir en BORRADOR con número asignado,
        # esperando a que el transporte pase. Idempotente: si ya tiene número (reimpresión), no
        # se vuelve a numerar.
        if not remito.numero_legal and not es_vista_previa:
            from backend.remitos.service import RemitosService
            # [S876, decisión de Carlos + Arq 30/09, confirmada en el prompt de remito/renglón §6] El
            # 0015 es el único talonario vivo y el 0017 queda abolido: ni Rosa ni no comercial numeran
            # por otra serie. Antes (DISENO_PEDIDO_NO_COMERCIAL_S873) "una sola serie para rosa y no
            # comerciales juntos" los mandaba al 17. Lo que distingue a un Rosa es que su PDF nunca
            # muestra precio (el motor no dibuja precios) y que su pedido no se factura.
            remito.numero_legal = RemitosService._siguiente_numero_0015(db)
            # [S891] Al tomar número se fijan la fecha de EMISIÓN (la del papel) y, salvo EN_DEPOSITO, la de salida: lo hace el
            # evento before_flush del modelo (backend/remitos/models.py), igual para cualquier camino que numere.
            _aclarar_si_rosa(db, remito)   # [S892] un Rosa con 0015 queda dicho: no se factura
            db.add(remito)
            db.commit()
            db.refresh(remito)

        # [S891] Reimpresión: un remito ya IMPRESO con imagen guardada recibe esa misma (con su nota) y no se regenera nada.
        if remito.numero_legal and not es_vista_previa and not primer_papel:
            imagen = os.path.join(carpeta_imagenes, f"remito_{remito.numero_legal.replace('-', '_')}.pdf")
            if os.path.exists(imagen):
                db.add(models.RemitoNota(remito_id=remito.id, texto=f"[SISTEMA] Reimpresión del remito ({datetime.now().strftime('%d/%m/%Y %H:%M')}): la misma imagen de lo impreso."))
                db.commit()
                return FileResponse(imagen, media_type='application/pdf', filename=os.path.basename(imagen))

        # Preparar datos para el motor
        if not remito.pedido:
            raise HTTPException(
                status_code=400, 
                detail="Remito sin pedido vinculado"
            )

        cliente = remito.pedido.cliente

        if not cliente:
            raise HTTPException(
                status_code=400, 
                detail="Pedido sin cliente vinculado"
            )
        items = []
        for r_item in remito.items:
            p_item = r_item.pedido_item
            
            # [FIX] Defensivo por si el p_item fue borrado (FK suelta) o no tiene producto
            codigo = ""
            desc = "ÍTEM DESCONOCIDO"
            
            if p_item:
                if p_item.producto:
                    codigo = p_item.producto.codigo_visual or ""
                    desc = p_item.producto.nombre or p_item.nota or "ÍTEM"
                else:
                    desc = p_item.nota or "ÍTEM MANUAL"
                    
            items.append({
                "codigo": codigo,
                "descripcion": desc,
                "cantidad": r_item.cantidad_remitida,
                "unidad": "UN" # Default
            })

        # [S868, regla de Carlos 17/09] El remito no tiene CAE propio: nunca se imprime remitos.cae
        # ni el bloque de validación ARCA del pie. Lo que sí imprime es la referencia a la factura
        # cuando existe y está vinculada, con el CAE de esa factura leído de la factura
        # (Remito.factura_vinculada / factura_vinculada_cae). Antes se decidía por el prefijo
        # 0015/0016, y sin vínculo se sacaba el número de la nota del pedido con una regex: una
        # referencia a una factura que podía no existir.
        cae_val = None
        vto_cae_val = None
        factura_vinculada_str = remito.factura_vinculada or ""

        # [Etapa 4, D5 + cabo suelto del anexo de OC -- PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md
        # §6] remito_engine.py ya tiene un campo "referencia" dibujado (REF:, cerca del domicilio)
        # pero nadie lo poblaba -- RemitoTemplate.vue sí mostraba "Ref. Pedido: #{id} (OC: {oc})",
        # mismo formato acá para que las dos vistas digan lo mismo. Condicionado por Carlos a que
        # entre en el talonario 0015 preimpreso -- el campo REF ya tenía posición y tamaño de
        # fuente calculados de antes, pero vale un chequeo de impresión real antes de confiar en
        # que el texto no se superpone a nada del papel preimpreso.
        # [S882, sugerencia de Tomy 08/10] La OC ya no va en esta linea chica (6 pt, "S/D" cuando no hay): tiene su propio
        # casillero en el talonario ("ORDEN DE COMPRA N°:", ver "oc" mas abajo y remito_engine.add_content).
        referencia_str = f"Pedido #{remito.pedido_id}"

        from backend.remitos.service import RemitosService
        cliente_data = {
            "razon_social": cliente.razon_social,
            "cuit": cliente.cuit,
            # [S890, regla de Carlos 20/10] La dirección del cliente (entrega, fiscal, y la oficina solo si no tiene ninguna).
            "domicilio_fiscal": RemitosService.domicilio_para_el_papel(db, remito),
            # [S891] La fecha del remito = la de EMISIÓN (cuando tomó número); los viejos sin ella, la de salida o la de creación.
            "fecha": (remito.fecha_emision or remito.fecha_salida or remito.fecha_creacion or datetime.now()).strftime("%d/%m/%Y"),
            # [S890] Casillero TRANSPORTISTA: la empresa del remito o, sin empresa, el método de la entrega.
            "transportista": RemitosService.transportista_para_el_papel(db, remito),
            "condicion_iva": "RESPONSABLE INSCRIPTO", # Default for now
            "referencia": referencia_str,
            "oc": remito.pedido.oc or "",   # [S882, sugerencia de Tomy] va al casillero "ORDEN DE COMPRA N°:" del talonario
            "factura_vinculada": factura_vinculada_str,
            "factura_vinculada_cae": remito.factura_vinculada_cae,
            "cae": cae_val,
            "vto_cae": vto_cae_val.strftime("%d/%m/%Y") if vto_cae_val else None,
            "bultos": getattr(remito, 'bultos', 1),
            "valor_declarado": getattr(remito, 'valor_declarado', 0.0),
            "observaciones": remito.pedido.nota or ""
        }
        
        from .remito_engine import generar_remito_pdf

        target_dir = os.path.join(base_dir, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
        os.makedirs(target_dir, exist_ok=True)

        if es_vista_previa:
            vista = os.path.join(target_dir, f"vista_previa_{str(remito.id).replace('-', '')}.pdf")
            generar_remito_pdf(cliente_data, items, is_preview=True, output_path=vista, numero_remito=None)
            return FileResponse(vista, media_type='application/pdf', filename="vista_previa_remito.pdf")

        safe_num = str(remito.numero_legal or remito_id).replace("-", "_")
        final_filename = f"remito_{safe_num}.pdf"
        final_path = os.path.join(target_dir, final_filename)
        
        generar_remito_pdf(
            cliente_data, 
            items, 
            is_preview=False, 
            output_path=final_path, 
            numero_remito=remito.numero_legal,
            cae=cae_val,
            vto_cae=vto_cae_val.strftime("%d/%m/%Y") if vto_cae_val else None
        )
        if remito.numero_legal:
            # [S891] la imagen de lo impreso: este PDF no se vuelve a generar (la vista previa ya salió más arriba)
            import shutil
            os.makedirs(carpeta_imagenes, exist_ok=True)
            shutil.copyfile(final_path, os.path.join(carpeta_imagenes, final_filename))
            if not primer_papel:
                db.add(models.RemitoNota(remito_id=remito.id, texto=(
                    f"[SISTEMA] Reimpresión del remito ({datetime.now().strftime('%d/%m/%Y %H:%M')}): no había imagen guardada (remito impreso "
                    "antes de guardar imágenes, o con la fecha cambiada); se regeneró con los datos de hoy y desde ahora esta es su imagen.")))
        # [S891, Nike: bit 44 IMPRESO] El remito se imprimió (se generó su PDF) al menos una vez: la marca no se apaga nunca.
        # Un 0015 sin esta marca es una salida sin papel (se fue solo con la factura).
        if not (int(remito.flags_estado or 0) & int(RemitoFlags.IMPRESO)):
            remito.flags_estado = int(remito.flags_estado or 0) | int(RemitoFlags.IMPRESO)
        db.commit()
        return FileResponse(
            final_path, 
            media_type='application/pdf', 
            filename=final_filename
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        log_path = os.path.join(os.getcwd(), "pdf_error.log")
        with open(log_path, "w") as f_err:
            f_err.write(f"FATAL ERROR: {str(e)}\n")
            traceback.print_exc(file=f_err)
        print(f"PDF FATAL (logged to {log_path}): {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")

@router.post("/ingesta-pdf")
async def ingest_invoice_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    [DEPRECATED V5.6] Use /ingesta/raw instead.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    result = await process_pdf_ingestion(file)

    # [CONSERJE] Factura duplicada — verificar antes de devolver al frontend
    if result.get("success") and result.get("data"):
        factura_numero = result["data"].get("factura", {}).get("numero")
        if factura_numero and "-" in factura_numero:
            from backend.facturacion.models import Factura
            partes = factura_numero.split("-")
            if len(partes) == 2:
                try:
                    pv, nc = int(partes[0]), int(partes[1])
                    factura_existente = db.query(Factura).filter(
                        Factura.punto_venta == pv,
                        Factura.numero_comprobante == nc
                    ).first()
                    if factura_existente:
                        raise HTTPException(
                            status_code=409,
                            detail={
                                "codigo": "FACTURA_DUPLICADA",
                                "mensaje": f"La factura {factura_numero} ya existe en el sistema.",
                                "factura_id": str(factura_existente.id),
                                "pedido_id": factura_existente.pedido_id,
                                "estado": factura_existente.estado
                            }
                        )
                except ValueError:
                    pass  # número no parseable, ignorar

    # [V5] ABM Workflow: Verify Client Status in DB
    if result.get("success") and result.get("data"):
        cuit = result["data"].get("cliente", {}).get("cuit")
        if cuit:
            from backend.clientes.models import Cliente
            cliente_db = db.query(Cliente).filter(Cliente.cuit == cuit).first()
            if cliente_db:
                result["data"]["cliente"]["id"] = str(cliente_db.id)
                result["data"]["cliente"]["db_status"] = "EXISTE"
                result["data"]["cliente"]["flags_estado"] = cliente_db.flags_estado
                result["data"]["cliente"]["razon_social"] = cliente_db.razon_social # Overrule PDF with DB truth
                result["data"]["cliente"]["domicilio"] = cliente_db.domicilio_fiscal_resumen or result["data"]["cliente"]["domicilio"]
                # [V5.8 GOLD] Heurística de Matching
                extracted_dom = result["data"]["cliente"]["domicilio"].replace("[EXTRACTED] ", "").upper()
                
                def calculate_score(d_obj, extracted_text):
                    score = 0
                    # Si la calle está contenida (Fuzzy Match simple)
                    if d_obj.calle and d_obj.calle.upper() in extracted_text: score += 50
                    # Si el número coincide perfectamente
                    if d_obj.numero and d_obj.numero in extracted_text: score += 30
                    # Prioridad por tipo
                    if d_obj.es_entrega: score += 10
                    if d_obj.es_fiscal: score += 5
                    return score

                domicilios_raw = []
                for d in cliente_db.domicilios:
                    if not d.activo: continue
                    d_dict = {
                        "id": str(d.id), 
                        "calle": d.calle, 
                        "numero": d.numero, 
                        "localidad": d.localidad, 
                        "es_fiscal": d.es_fiscal, 
                        "es_entrega": d.es_entrega, 
                        "alias": d.alias,
                        "score": calculate_score(d, extracted_dom)
                    }
                    domicilios_raw.append(d_dict)
                
                # Ordenar por score descendente
                domicilios_raw.sort(key=lambda x: x['score'], reverse=True)
                
                # Marcar el mejor como sugerido si supera el umbral
                if domicilios_raw and domicilios_raw[0]['score'] >= 50:
                    domicilios_raw[0]['is_suggested'] = True

                result["data"]["cliente"]["domicilios_disponibles"] = domicilios_raw
                result["data"]["suggested_action"] = "EDIT_CLIENT"
            else:
                result["data"]["cliente"]["db_status"] = "NO_EXISTE"
                result["data"]["cliente"]["flags_estado"] = 0
                result["data"]["suggested_action"] = "CREATE_CLIENT"
                
    return result

@router.post("/manual", response_model=schemas.RemitoResponse)
def create_manual_remito(payload: schemas.ManualRemitoPayload, db: Session = Depends(get_db)):
    """
    Crea un Remito de forma manual (sin PDF).
    Serie 0015-
    """
    try:
        from backend.remitos.service import RemitosService
        remito = RemitosService.create_manual(db, payload)
        return remito
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        # [S887] Los frenos del servicio (CANTIDAD_EXCEDE_PEDIDO, RENGLON_AJENO_AL_PEDIDO: 409) llegan tal cual, con su aviso.
        # Antes el «except Exception» de abajo los convertía en un 500 «Error interno: 409: ...» y el operador veía un error del sistema.
        raise
    except Exception as e:
        print(f"Error creating Manual Remito: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/armar", response_model=schemas.RemitoResponse)
def armar_remito(payload: schemas.ArmarRemitoPayload, db: Session = Depends(get_db)):
    """[Etapa 4, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §6] Arma un PR desde un pedido
    existente -- pantalla de armado (D3, primera pantalla). Renglones elegidos por
    pedido_item_id, nunca texto libre. Un movimiento sin pedido comercial se arma igual, contra
    un Pedido con PedidoFlags.ES_NO_COMERCIAL -- ver docstring de RemitosService.armar_remito.
    """
    try:
        from backend.remitos.service import RemitosService
        return RemitosService.armar_remito(db, payload)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error armando Remito: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/{remito_id}/notas", response_model=schemas.RemitoNotaResponse)
def crear_nota(
    remito_id: str,
    payload: schemas.RemitoNotaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """[Etapa 5, PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §7] Novedad fechada sobre un
    remito o un renglón puntual -- acumulativa, nunca editable (doctrina en el docstring de
    RemitoNota). El autor sale siempre de la sesión autenticada, nunca del payload -- mismo
    patrón que update_pedido_item/toggle_no_comercial.
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")

    if payload.remito_item_id is not None:
        item = next((i for i in remito.items if i.id == payload.remito_item_id), None)
        if not item:
            raise HTTPException(
                status_code=409,
                detail=f"RENGLON_AJENO_AL_REMITO: el renglón #{payload.remito_item_id} no pertenece al Remito {remito_id}."
            )

    nota = models.RemitoNota(
        remito_id=remito_id,
        remito_item_id=payload.remito_item_id,
        texto=payload.texto,
        autor_id=current_user.id,
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota

@router.patch("/{remito_id}/fecha", response_model=schemas.RemitoResponse)
def cambiar_fecha(
    remito_id: str,
    payload: schemas.RemitoFechaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """[S890, Carlos 20-21/10; S891] La fecha del remito es la de EMISIÓN (el día en que tomó número: fecha_emision).
    Se puede cambiar «por si el papel se perdió o hay que ajustar algo sin perder el remito original»: solo en un remito
    numerado y no anulado, con motivo, nunca a futuro, y queda una nota [SISTEMA] con la fecha anterior, la nueva,
    quién y por qué. Si la salida física se había asumido en la emisión (mismo día), se mueve con ella."""
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if not remito.numero_legal:
        raise HTTPException(status_code=409, detail="REMITO_SIN_NUMERO: la fecha del remito es la del día en que toma número; este todavía no lo tiene.")
    if remito.estado == "ANULADO":
        raise HTTPException(status_code=409, detail="REMITO_ANULADO: no se cambia la fecha de un remito anulado.")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(status_code=422, detail="MOTIVO_OBLIGATORIO: decí por qué cambia la fecha del remito.")
    try:
        nueva = datetime.strptime(payload.fecha.strip()[:10], "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="FECHA_INVALIDA: la fecha va como AAAA-MM-DD.")
    if nueva.date() > datetime.now().date():
        raise HTTPException(status_code=422, detail="FECHA_FUTURA: un remito no puede tener fecha posterior a hoy.")
    anterior = remito.fecha_emision or remito.fecha_salida or remito.fecha_creacion
    hora = anterior.time() if anterior else datetime.now().time()
    nueva_emision = datetime.combine(nueva.date(), hora)
    # la salida asumida en la emisión (mismo día) acompaña el cambio; una salida posterior registrada aparte no se toca, y un remito
    # que quedó en depósito (bit 37) sigue sin salida: la pone «Retiró el transporte» (S892)
    from backend.remitos.constants import RemitoFlags
    en_deposito = bool(int(remito.flags_estado or 0) & int(RemitoFlags.EN_DEPOSITO))
    if not en_deposito and (remito.fecha_salida is None or (anterior and remito.fecha_salida.date() == anterior.date())):
        remito.fecha_salida = nueva_emision
    remito.fecha_emision = nueva_emision
    texto = (f"[SISTEMA] Fecha del remito cambiada del {anterior.strftime('%d/%m/%Y') if anterior else 's/f'} "
             f"al {nueva.strftime('%d/%m/%Y')}. Motivo: {motivo}")
    # [S891] el papel cambia de fecha: la imagen guardada se archiva (no se borra) y el próximo papel sale con la fecha nueva
    import os
    carpeta = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
    imagen = os.path.join(carpeta, f"remito_{remito.numero_legal.replace('-', '_')}.pdf")
    if os.path.exists(imagen):
        archivada = f"remito_{remito.numero_legal.replace('-', '_')}__hasta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs(os.path.join(carpeta, "Reemplazadas"), exist_ok=True)
        os.replace(imagen, os.path.join(carpeta, "Reemplazadas", archivada))
        texto += ("" if texto.endswith(".") else ".") + f" La imagen del papel anterior quedó archivada (Reemplazadas/{archivada}); el próximo papel sale con la fecha nueva."
    db.add(models.RemitoNota(remito_id=remito.id, texto=texto, autor_id=current_user.id))
    db.commit()
    db.refresh(remito)
    return remito

EPS_CANTIDAD = 1e-6


def _pesos(x) -> str:
    return "$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _facturado_vigente(remito) -> list:
    """[S892, auditoría de CA de la S891] Qué factura todavía ampara al remito, neto de notas de crédito (lista vacía = ninguna).
    Una NC no borra el vínculo facturas_remitos (es historia); lo que libera al remito es que lo facturado, menos lo acreditado,
    llegue a cero. Antes la guarda miraba solo el vínculo y un remito facturado quedaba trabado para siempre aunque tuviera su NC.
    - Si algún renglón tiene lo facturado por renglón (cantidad_facturada > 0, el camino del conciliador nuevo), manda el neto de
      cada renglón (cantidad_facturada_neta): una NC que acredita esos renglones lo libera aunque la factura abarque otros remitos.
    - Si no (lo que hay en P: el vínculo existe y cantidad_facturada no está cargada), manda la factura: cada factura vinculada,
      numerada y no anulada, ampara al remito salvo que sus NC no anuladas (facturas_ajustes) cubran su total."""
    from backend.facturacion.constants import es_nota_credito
    renglones = [ri for ri in remito.items if (ri.cantidad_facturada or 0) > EPS_CANTIDAD]
    if renglones:
        return [f"«{ri.descripcion_display}» ({ri.cantidad_facturada_neta:g} facturado sin nota de crédito)"
                for ri in renglones if (ri.cantidad_facturada_neta or 0) > EPS_CANTIDAD]
    vigentes = []
    for vinculo in remito.vinculos_facturas or []:
        f = vinculo.factura
        if f is None or f.punto_venta is None or f.numero_comprobante is None or str(f.estado or "").upper().startswith("ANULAD"):
            continue
        acreditado = sum((a.monto_aplicado if a.monto_aplicado is not None else (a.nc_nd.total or 0))
                         for a in (f.ajustes_recibidos or [])
                         if a.nc_nd is not None and es_nota_credito(a.nc_nd.tipo_comprobante)
                         and not str(a.nc_nd.estado or "").upper().startswith("ANULAD"))
        if acreditado < (f.total or 0) - 0.01:
            vigentes.append(f"la factura {f.numero_completo}"
                            + (f" (notas de crédito por {_pesos(acreditado)} de {_pesos(f.total or 0)})" if acreditado > 0.01 else ""))
    return vigentes


@router.post("/{remito_id}/anular", response_model=schemas.RemitoResponse)
def anular_remito(remito_id: str, payload: schemas.RemitoMotivo, db: Session = Depends(get_db),
                  current_user: Usuario = Depends(get_current_active_user)):
    """[S891, Carlos + Nike 22/10] Un remito con número es inmortal: no se borra, se ANULA (el número queda quemado). Con motivo y nota
    [SISTEMA] con el estado anterior (para poder deshacerlo). Un remito sin número no se anula: se descarta (se borra). Un remito con
    algo ya facturado no se anula: primero va la nota de crédito. Las cantidades vuelven a quedar pendientes en el pedido."""
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if not remito.numero_legal:
        raise HTTPException(status_code=409, detail="REMITO_SIN_NUMERO: un remito sin número no se anula, se descarta (tacho).")
    if remito.estado == "ANULADO":
        raise HTTPException(status_code=409, detail="REMITO_YA_ANULADO: el remito ya está anulado.")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(status_code=422, detail="MOTIVO_OBLIGATORIO: decí por qué se anula el remito.")
    vigente = _facturado_vigente(remito)
    if vigente:
        raise HTTPException(status_code=409, detail=(f"REMITO_FACTURADO: el remito está amparado por {'; '.join(vigente)}; primero va la "
                                                     "nota de crédito por lo que falta y después se anula."))
    anterior = remito.estado
    remito.estado = "ANULADO"
    db.add(models.RemitoNota(remito_id=remito.id, autor_id=current_user.id,
                             texto=f"[SISTEMA] Remito anulado (estado anterior: {anterior}). Motivo: {motivo}"))
    db.flush()
    from backend.remitos.service import RemitosService
    if remito.pedido:
        RemitosService._recalcular_bits_entrega(db, remito.pedido)
    db.commit()
    db.refresh(remito)
    return remito


@router.post("/{remito_id}/deshacer-anulacion", response_model=schemas.RemitoResponse)
def deshacer_anulacion(remito_id: str, payload: schemas.RemitoMotivo, db: Session = Depends(get_db),
                       current_user: Usuario = Depends(get_current_active_user)):
    """[S891, Carlos + Nike 22/10] Deshacer una anulación es válido con nota forense, y se BLOQUEA si otro remito ya cubrió esas
    cantidades (sería contar dos veces una salida física). La guarda es por cantidades, sin campo de vínculo: para cada renglón, lo
    remitido en remitos vigentes más lo de este remito no puede superar lo pedido. Vuelve al estado que tenía antes de anularse; la
    cicatriz FUE_ANULADO (bit 43) queda para siempre."""
    import re
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if remito.estado != "ANULADO":
        raise HTTPException(status_code=409, detail="REMITO_NO_ANULADO: el remito no está anulado.")
    motivo = (payload.motivo or "").strip()
    if not motivo:
        raise HTTPException(status_code=422, detail="MOTIVO_OBLIGATORIO: decí por qué se deshace la anulación.")
    choques = []
    for ri in remito.items:
        pi = ri.pedido_item
        if pi is None or (ri.cantidad_remitida or 0) <= EPS_CANTIDAD:
            continue
        vigente = pi.cantidad_entregada or 0   # remitos no anulados (este no cuenta: está anulado)
        if vigente + ri.cantidad_remitida > (pi.cantidad or 0) + EPS_CANTIDAD:
            cubren = sorted({o.remito.numero_legal or "sin número" for o in pi.remitos_items
                             if o.remito and o.remito.estado != "ANULADO" and o.remito_id != remito.id})
            nombre = pi.producto.nombre if pi.producto else (pi.nota or f"renglón {pi.id}")
            choques.append(f"«{nombre}»: ya lo cubre {', '.join(cubren)} ({vigente:g} de {pi.cantidad:g} remitidos)")
    if choques:
        raise HTTPException(status_code=409, detail="REMITO_SUSTITUIDO: no se puede deshacer la anulación porque otro remito ya cubrió esas cantidades: "
                                                    + "; ".join(choques) + ".")
    nota_anul = (db.query(models.RemitoNota)
                 .filter(models.RemitoNota.remito_id == remito.id, models.RemitoNota.texto.like("[SISTEMA] Remito anulado (estado anterior:%"))
                 .order_by(models.RemitoNota.fecha.desc()).first())
    m = re.search(r"estado anterior: (\w+)", nota_anul.texto) if nota_anul else None
    remito.estado = m.group(1) if m and m.group(1) in ("BORRADOR", "EN_CAMINO", "ENTREGADO") else (
        "ENTREGADO" if remito.metodo_entrega == "MOSTRADOR" else "BORRADOR")
    db.add(models.RemitoNota(remito_id=remito.id, autor_id=current_user.id,
                             texto=f"[SISTEMA] Anulación revertida (vuelve a {remito.estado}). Motivo: {motivo}"))
    db.flush()
    from backend.remitos.service import RemitosService
    if remito.pedido:
        RemitosService._recalcular_bits_entrega(db, remito.pedido)
    db.commit()
    db.refresh(remito)
    return remito


def _dia_del_remito(texto: Optional[str]) -> datetime:
    """Fecha AAAA-MM-DD de una acción del remito, con la hora de ahora; sin dato, ahora. Nunca a futuro."""
    if not texto:
        return datetime.now()
    try:
        dia = datetime.strptime(texto.strip()[:10], "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="FECHA_INVALIDA: la fecha va como AAAA-MM-DD.")
    if dia.date() > datetime.now().date():
        raise HTTPException(status_code=422, detail="FECHA_FUTURA: no puede ser posterior a hoy.")
    return datetime.combine(dia.date(), datetime.now().time())


NOTA_REMITO_ROSA = "[SISTEMA] Remito de un pedido Rosa: no se factura."


def _aclarar_si_rosa(db, remito, autor_id=None) -> None:
    """[S892, Carlos 23/10] Un pedido Rosa SÍ puede salir con un 0015 (cuando lo despacha un transporte hace falta un remito de verdad), y
    ese remito es no facturable («quiero que quede aclarado»). Lo es de hecho (cantidad_facturada nace en NULL = no aplica, el conciliador
    no lo ofrece); esta nota lo deja dicho en el remito la primera vez que toma número, sin esperar a que haya una marca en el genoma."""
    from backend.pedidos.constants import PedidoFlags
    if remito.pedido and int(remito.pedido.flags_estado or 0) & int(PedidoFlags.NO_FISCAL_FORCE):
        db.add(models.RemitoNota(remito_id=remito.id, autor_id=autor_id, texto=NOTA_REMITO_ROSA))


@router.post("/{remito_id}/salida-sin-papel", response_model=schemas.RemitoResponse)
def salida_sin_papel(remito_id: str, payload: schemas.RemitoFechaMotivo = schemas.RemitoFechaMotivo(), db: Session = Depends(get_db),
                     current_user: Usuario = Depends(get_current_active_user)):
    """[S892, paquete 2 tramo 3; Carlos + Nike 22/10 y 23/10] La mercadería salió sin remito impreso (se fue con la factura, o el papel no
    hizo falta). El remito toma su número como si se imprimiera, pero sin papel: queda EMITIDO sin la marca IMPRESO (bit 44), con la
    salida asumida en la emisión. Si después lo piden, se imprime con ese mismo número y ese primer papel queda como imagen.
    La fecha del remito es la de la asignación del número, o sea AHORA (Carlos, 23/10: «el remito debe salir con la fecha de confección,
    que es la de la asignación de número»); si hace falta otra, se cambia después con el lápiz, con motivo y con nota.
    Cualquier color: un pedido Rosa también puede salir con un 0015 (si lo despacha un transporte hace falta un remito), y queda dicho en
    el remito que no se factura. «En depósito» y «Retiró el transporte» son modificaciones especiales que hace el operador."""
    from backend.remitos.service import RemitosService
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if remito.numero_legal:
        raise HTTPException(status_code=409, detail=f"REMITO_CON_NUMERO: el remito ya tiene número ({remito.numero_legal}): ya salió, con o sin papel.")
    if remito.estado == "ANULADO":
        raise HTTPException(status_code=409, detail="REMITO_ANULADO: un remito anulado no sale.")
    if sum((ri.cantidad_remitida or 0) for ri in remito.items) <= EPS_CANTIDAD:
        raise HTTPException(status_code=409, detail="REMITO_VACIO: el remito no tiene cantidades.")
    from backend.remitos.constants import RemitoFlags
    remito.fecha_emision = datetime.now()   # el evento del modelo pone la salida asumida en esta fecha
    remito.numero_legal = RemitosService._siguiente_numero_0015(db)
    # el operador declara que salió: salida CONFIRMADA (Nike, bit 47); la fecha sigue siendo la asumida de la emisión
    remito.flags_estado = int(remito.flags_estado or 0) | int(RemitoFlags.SALIDA_CONFIRMADA)
    motivo = (payload.motivo or "").strip()
    db.add(models.RemitoNota(remito_id=remito.id, autor_id=current_user.id,
                             texto=(f"[SISTEMA] Salió sin papel el {remito.fecha_emision.strftime('%d/%m/%Y')}: tomó el número "
                                    f"{remito.numero_legal} sin imprimirse." + (f" Motivo: {motivo}" if motivo else ""))))
    _aclarar_si_rosa(db, remito, current_user.id)
    db.flush()
    if remito.pedido:
        RemitosService._recalcular_bits_entrega(db, remito.pedido)
    db.commit()
    db.refresh(remito)
    return remito


@router.post("/{remito_id}/en-deposito", response_model=schemas.RemitoResponse)
def queda_en_deposito(remito_id: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_active_user)):
    """[S892, paquete 2 tramo 3; caso Rizobacter] El remito tiene número (impreso o sin papel) pero la mercadería sigue en el depósito
    esperando que la retire el transporte. Se borra la salida que se había asumido en la emisión y queda la marca EN_DEPOSITO (bit 37)
    hasta «Retiró el transporte». No aplica a un remito en camino o recibido."""
    from backend.remitos.constants import RemitoFlags
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if not remito.numero_legal:
        raise HTTPException(status_code=409, detail="REMITO_SIN_NUMERO: un remito sin número todavía no salió: no hace falta marcarlo.")
    if remito.estado in ("ANULADO", "EN_CAMINO", "ENTREGADO"):
        raise HTTPException(status_code=409, detail=f"REMITO_{remito.estado}: un remito {remito.estado.lower().replace('_', ' ')} no queda en depósito.")
    if int(remito.flags_estado or 0) & int(RemitoFlags.EN_DEPOSITO):
        raise HTTPException(status_code=409, detail="YA_EN_DEPOSITO: el remito ya figura en depósito.")
    asumida = remito.fecha_salida
    remito.fecha_salida = None
    remito.flags_estado = int(remito.flags_estado or 0) | int(RemitoFlags.EN_DEPOSITO)
    db.add(models.RemitoNota(remito_id=remito.id, autor_id=current_user.id,
                             texto=("[SISTEMA] Queda en depósito esperando que lo retire el transporte"
                                    + (f" (se borró la salida asumida del {asumida.strftime('%d/%m/%Y')})." if asumida else "."))))
    db.commit()
    db.refresh(remito)
    return remito


@router.post("/{remito_id}/retiro", response_model=schemas.RemitoResponse)
def retiro_del_transporte(remito_id: str, payload: schemas.RemitoFechaMotivo = schemas.RemitoFechaMotivo(), db: Session = Depends(get_db),
                          current_user: Usuario = Depends(get_current_active_user)):
    """[S892, paquete 2 tramo 3] El transporte retiró un remito que estaba en depósito: se registra la salida (hoy o la fecha que se
    indique, nunca antes de la emisión). Si es un día posterior a la emisión, el genoma marca SALIDA_DIFERIDA (bit 45)."""
    from backend.remitos.constants import RemitoFlags
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    if not (int(remito.flags_estado or 0) & int(RemitoFlags.EN_DEPOSITO)):
        raise HTTPException(status_code=409, detail="REMITO_NO_EN_DEPOSITO: el remito no figura en depósito.")
    salida = _dia_del_remito(payload.fecha)
    if remito.fecha_emision and salida.date() < remito.fecha_emision.date():
        raise HTTPException(status_code=422, detail=(f"SALIDA_ANTES_DE_EMISION: el remito se emitió el {remito.fecha_emision.strftime('%d/%m/%Y')}; "
                                                     "no puede haber salido antes."))
    remito.fecha_salida = salida
    remito.flags_estado = int(remito.flags_estado or 0) | int(RemitoFlags.SALIDA_CONFIRMADA)   # el operador lo registró (Nike, bit 47)
    # se lo llevó el transporte: está en camino (y ya no se puede volver a marcar «en depósito»)
    paso = ""
    if remito.estado == "BORRADOR":
        remito.estado = "EN_CAMINO"
        paso = " Pasa a EN CAMINO."
    db.add(models.RemitoNota(remito_id=remito.id, autor_id=current_user.id,
                             texto=f"[SISTEMA] Retiró el transporte el {salida.strftime('%d/%m/%Y')}.{paso}"))
    db.commit()
    db.refresh(remito)
    return remito


@router.get("/{remito_id}/notas", response_model=List[schemas.RemitoNotaResponse])
def listar_notas(remito_id: str, db: Session = Depends(get_db)):
    """[Etapa 5] Notas de un remito, más viejas primero -- lectura, sin sesión requerida."""
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")

    return (
        db.query(models.RemitoNota)
        .filter(models.RemitoNota.remito_id == remito_id)
        .order_by(models.RemitoNota.fecha)
        .all()
    )

@router.patch("/items/{remito_item_id}/recibido", response_model=schemas.RemitoItemResponse)
def actualizar_cantidad_recibida(
    remito_item_id: int,
    payload: schemas.CantidadRecibidaUpdate,
    db: Session = Depends(get_db)
):
    """[Etapa 5, dictamen Nike "Homologación de Techo y Reasignación en Puerta"] Ver docstring de
    RemitosService.set_cantidad_recibida para la regla completa (techo agregado por PedidoItem,
    no comparación renglón a renglón)."""
    try:
        from backend.remitos.service import RemitosService
        return RemitosService.set_cantidad_recibida(db, remito_item_id, payload.cantidad_recibida)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error actualizando cantidad_recibida: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/items/{remito_item_id}/resolver-no-facturable", response_model=schemas.RemitoItemResponse)
def resolver_no_facturable(
    remito_item_id: int,
    payload: schemas.ResolverNoFacturablePayload,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """[S876] Resuelve un renglón con motivo_no_facturable (consignación, muestra sin cargo, garantía):
    FACTURAR lo devuelve al camino normal de facturación. Devolver la mercadería no pasa por acá: es un
    PR de cantidad negativa (POST /remitos/armar). Ver RemitosService.resolver_no_facturable."""
    try:
        from backend.remitos.service import RemitosService
        return RemitosService.resolver_no_facturable(db, remito_item_id, payload.accion, current_user.id)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error resolviendo renglón no facturable {remito_item_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/interno/desde_factura/{factura_id}", response_model=schemas.RemitoResponse)
def originar_remito_interno_desde_factura(factura_id: str, metodo_entrega: str, db: Session = Depends(get_db)):
    """[S876] Remito interno (sin número, sin hoja de ruta) para una factura sellada que se entrega en
    MOSTRADOR o con el remito/etiqueta de un tercero (REMITO_EXTERNO). Siempre queda el movimiento
    registrado, se imprima o no el papel. Ver RemitosService.create_interno_desde_factura."""
    try:
        from backend.remitos.service import RemitosService
        return RemitosService.create_interno_desde_factura(db, factura_id, metodo_entrega)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error remito interno desde factura {factura_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/puente/desde_factura/{factura_id}", response_model=schemas.RemitoResponse)
def originar_remito_desde_factura(factura_id: str, db: Session = Depends(get_db)):
    """
    Crea o vincula un remito logístico a partir de una Factura sellada.
    Diseñado para el flujo: Sellar Factura AFIP -> Asistir Logística.
    """
    try:
        from backend.remitos.service import RemitosService
        remito = RemitosService.create_puente_factura(db, factura_id)
        return remito
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error bridge Factura->Remito {factura_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.patch("/{remito_id}", response_model=schemas.RemitoResponse)
def update_remito(remito_id: str, payload: schemas.RemitoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un remito existente (Cabecera).
    """
    try:
        from backend.remitos.service import RemitosService
        updated = RemitosService.update_remito(db, remito_id, payload)
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error updating Remito {remito_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar remito")

@router.delete("/{remito_id}")
def delete_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Elimina un remito en estado BORRADOR y su pedido asociado (si es huérfano de ingesta).
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
        
    if remito.estado != "BORRADOR":
        raise HTTPException(status_code=400, detail="Solo se pueden eliminar remitos en estado BORRADOR")
    # [S891, Carlos + Nike: el remito con número es inmortal] Antes el tacho borraba un BORRADOR aunque ya tuviera número, y el
    # número se volvía a usar en el remito siguiente (hallazgo H8 de CA, 0015-00003030). Ahora solo se borra lo que no tiene número.
    if remito.numero_legal:
        raise HTTPException(status_code=409, detail=f"REMITO_CON_NUMERO: el remito {remito.numero_legal} ya tiene número: no se borra, se anula.")
        
    pedido_id = remito.pedido_id

    # [FIX] La Factura "espejo" (MODO ESPEJO, ver RemitosService.create_from_ingestion)
    # vinculada a este remito quedaba huerfana en estado BORRADOR al borrar el
    # remito, bloqueando para siempre cualquier reintento de ingesta del mismo
    # numero de factura (choca contra el UNIQUE de facturas). Si la factura sigue
    # en BORRADOR (nunca se convirtio en un comprobante fiscal real), se borra
    # junto con el remito. [S882] Una factura con CAE ES un comprobante real aunque la ingesta vieja la haya
    # dejado en BORRADOR (el CAE no se puede regenerar): esa no se borra nunca.
    from backend.facturacion.models import Factura, FacturaItem, FacturaRemito
    for vinculo in db.query(FacturaRemito).filter(FacturaRemito.remito_id == remito.id).all():
        factura = db.query(Factura).filter(Factura.id == vinculo.factura_id).first()
        if factura and factura.estado == "BORRADOR" and not (factura.cae or "").strip():
            db.query(FacturaItem).filter(FacturaItem.factura_id == factura.id).delete()
            db.delete(factura)

    # Delete remito (cascades to remito_items y factura_remito)
    db.delete(remito)
    db.flush()
    
    # Check if we should delete the Pedido too
    from backend.pedidos.models import Pedido
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido and pedido.origen == "INGESTA_PDF":
        db.delete(pedido) # This cascades to pedido_items
    elif pedido:
        from backend.remitos.service import RemitosService
        RemitosService._recalcular_bits_entrega(db, pedido)

    db.commit()
    return {"message": "Remito eliminado correctamente"}
