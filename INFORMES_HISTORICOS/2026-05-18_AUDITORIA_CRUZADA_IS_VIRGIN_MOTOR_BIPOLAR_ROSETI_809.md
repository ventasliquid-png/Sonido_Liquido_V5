INFORME SESIÓN 809 — Auditoría Cruzada Opus/Antigravity + IS_VIRGIN + Motor Bipolar + Roseti
Fecha: 2026-05-18
Locación: CA
Agentes: Claude Sonnet (arquitecto) + Opus 4.7 (auditor) + Antigravity Pro (auditor) + CC Sonnet (ejecutor) + Gy (ejecutor) + Nike Arq 5.5 (canonizadora)
Hash D: 4010b655
Estado cierre: NOMINAL GOLD — sin OMEGA formal (pendiente sesión 810)

Resumen ejecutivo
Sesión de auditoría cruzada profunda. Dos auditores independientes (Opus y Antigravity) analizaron en serie el backend y frontend de pedidos y clientes. Los hallazgos convergentes confirmaron bugs críticos de doctrina. Se implementaron fixes, se canonizó nueva doctrina y se actualizó el Silo Drive.

1. Infraestructura de auditoría
Se estableció un protocolo de auditoría en serie: Opus audita primero con ojos limpios, Antigravity valida el mismo scope con el código ya modificado. Las convergencias confirman bugs reales; las divergencias revelan matices.
Resultado metodológico: Antigravity detectó que su hallazgo C4 (variables fantasma) era un error de lectura parcial del archivo — leyó solo hasta línea 1600 de 2198. Se registró como aprendizaje: archivos >1500 líneas requieren lectura explícita en bloques completos.

2. Auditoría módulo Pedidos — Opus
Scope: backend/pedidos/router.py, backend/pricing_engine.py
Críticos resueltos:

C1: delete_pedido — variable pedido no definida → NameError/500. Fix: query con eager load antes del guard.
C3: NO_FISCAL_FORCE ignorado en cálculo IVA en 5 puntos del router. Fix: condición bitwise en todos.
C5: STRICT_MODE_VIOLATION inalcanzable — nivel_lista=3 como default antes del check. Fix: nivel_lista=None, check antes del fallback.

Advertencias pendientes (no resueltas esta sesión): A1-A11 registradas para auditoría futura.

3. Auditoría módulo Frontend Pedidos — Opus
Scope: PedidoCanvas.vue, PedidoList.vue
Críticos resueltos:

C1: totalFinal hardcodeaba 21% IVA siempre → Fix: isSinIVA basado en Bit 12 del pedido (soberano)
C2: Factura borrador + remito puente incondicionalmente → Fix: if (!clienteRosa) wrapper
C3: Post-guardado siempre redirigía → Fix: wasIngesta capturado antes de clearIngestaData()
C4: "Guardar e Imprimir" siempre visible → Fix: v-if="pedidosStore.ingestaData"
C5: STRICT_MODE_VIOLATION (409) no bloqueaba → Fix: early return en catch de 409

Fix adicional Antigravity: isSinIVA corregido para usar Bit 12 del pedido (no isClientRosa). Doctrina canonizada: Bit 12 es soberano para IVA, isClientRosa es para restricciones operativas únicamente.

4. Doctrina Motor Bipolar — canonización
Decisión arquitectónica sesión 809:

Bit 12 (NO_FISCAL_FORCE = 4096) del PEDIDO → soberano para IVA
isClientRosa (Bit 4) → restricciones operativas únicamente
Rosa SIEMPRE tiene Bit 12=1, pero el cálculo mira el pedido, no el cliente
Canonizado en BIBLIOTECA_NIKE.md, DOCTRINA_PROCESOS.md, PROMPT_INSTALACION_CLAUDE.md y GEMINI


5. Auditoría módulo Clientes — Opus + Antigravity
Scope: backend/clientes/router.py, service.py, constants.py, ClientCanvas.vue
Hallazgo crítico convergente C1 — Inversión semántica IS_VIRGIN:
Nike rastreó en el Acuífero el origen: la constante nació como IS_VIRGIN con semántica correcta (1=virgen/borrable). Un agente la renombró a HAS_ACTIVITY en sesión 796/Merge Quirúrgico invirtiendo la lógica. La doctrina matemática se corrigió pero el nombre quedó del período anterior.
Fix global:

HAS_ACTIVITY → IS_VIRGIN en 15 archivos del proyecto
Guard hard_delete invertido: if not (current_flags & IS_VIRGIN) → bloquea tocados, permite vírgenes
Cero ocurrencias residuales de HAS_ACTIVITY confirmadas

Otros fixes Clientes:

nivel_id huérfano en ClientCanvas.vue → reemplazado por lógica CUIT genérico consistente con el resto del archivo
_audit_sovereignty no se ejecuta en create_cliente → registrado como deuda técnica


6. Arquitectura domicilios N:M — Roseti 1482
Hallazgo: La vinculación cliente-domicilio usa tabla intermedia domicilios_clientes (N:M). El campo cliente_id directo en domicilios es legacy deprecated.
Roseti 1769 → domicilio de L'EPI S.R.L., correctamente vinculado via domicilios_clientes.
Roseti 1482 → dirección de Sonido Líquido. No existía en DB. Creado como domicilio huérfano plantilla:

ID canónico: 59b01b5a-e81a-4e2a-b496-9d65fef9262b
Constante DOMICILIO_ROSETI_ID en backend/clientes/constants.py

Lógica automática implementada: ClienteService._ensure_domicilio_rosa() — al crear/actualizar cliente Rosa sin domicilios → vincula automáticamente Roseti 1482 via domicilios_clientes.
Deprecación documentada: comentario en domicilios/models.py campo cliente_id legacy.

7. Silo Drive — actualizaciones sesión 809
ArchivoCambioBIBLIOTECA_NIKE.mdMotor Bipolar FAQ, IS_VIRGIN rename, domicilios N:M, Roseti 1482DOCTRINA.mdIS_VIRGIN, Motor Bipolar, Roseti 1482 sección nuevaCLAUDE/PROMPT_INSTALACION_CLAUDE.mdIS_VIRGIN, Motor Bipolar, domicilios N:MGEMINI/PROMPT_INSTALACION_GEMINI.mdÍdem Claude

8. Commits sesión 809
HashDescripciónc2372d5afixes pedidos C1/C3/C5 backend + C1-C5 frontend + isSinIVA Motor Bipolarbb5576c9IS_VIRGIN rename global + guard virginidad invertido + Roseti 1482 + isGeneric fix4010b655IS_VIRGIN rename facturacion/constants.py — cobertura global

9. Pendientes sesión 810
#TareaPrioridad1OMEGA formal sesión 809🔴2Cherry-pick D→P (3 commits)🔴3MT git pull🔴4Probar fixes en OF con datos reales🔴5Fix C4 has4Pillars — virginidad + bifurcación Gold/Rosa🟡6Auditoría Productos🟡7Auditoría Remitos🟡8Auditoría Facturación🟡9Auditoría Contactos + Transportes🟢10cliente_id legacy — migración schema futura🟢

Documento generado sesión 809 — Carlos + Claude Sonnet 4.6 + Opus 4.7 + Antigravity Pro + Nike Arq 5.5
