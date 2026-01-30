# Lista de Tareas - Sonido Líquido V5 (Sesión Actual)

- [x] **Protocolo Alfa** <!-- id: 0 -->
    - [x] Cargar Identidad V14 y Doctrina. <!-- id: 1 -->
    - [x] Analizar informes históricos recientes. <!-- id: 2 -->
    - [x] Reportar estado "Listo". <!-- id: 3 -->

- [x] **Finalización Documentación (Pendiente 29/01)** <!-- id: 12 -->
    - [x] Actualizar LECCIONES_APRENDIDAS.md (Regla Contraste). <!-- id: 13 -->
    - [x] Clarificar BITACORA_DEV.md (Interfaz Contacto). <!-- id: 14 -->
    - [x] Git Push Final. <!-- id: 15 -->

- [x] **Misión: Testeo Táctico de Contactos** <!-- id: 4 -->
    - [x] **Refactor UI Vínculos** <!-- id: 16 -->
        - [x] Implementar Smart Input Group en `ContactCanvas.vue`. <!-- id: 17 -->
        - [x] Implementar Búsqueda Filtrada y Auto-Foco. <!-- id: 19 -->
        - [x] Verificar selección por coincidencia y colores.
    
- [x] **Protocolo Multiplex (Fase 1: Modelos)** <!-- id: 20 -->
    - [x] **Backend Refactor** <!-- id: 21 -->
        - [x] Modificar `backend/contactos/models.py` (Persona, Vinculo). <!-- id: 22 -->
        - [x] Crear `scripts/migrate_v6_multiplex.py`. <!-- id: 23 -->
        - [x] Ejecutar migración y verificar DB (1 registro migrado). <!-- id: 24 -->

- [x] **Protocolo Multiplex (Fase 2: Lógica)** <!-- id: 25 -->
    - [x] **Service Layer** <!-- id: 26 -->
        - [x] Actualizar `schemas.py` (VinculoRead). <!-- id: 27 -->
        - [x] Crear `service.py` (Get/Post con lógica N:M). <!-- id: 28 -->
        - [x] Adaptar `router.py` endpoints. <!-- id: 29 -->

- [x] **Protocolo Multiplex (Fase 3: Frontend)** <!-- id: 30 -->
    - [x] **Reescribir ContactCanvas.vue** <!-- id: 31 -->
        - [x] Implementar Cabecera Persona (Datos personales, Redes). <!-- id: 32 -->
        - [x] Implementar Billetera de Vínculos (Tarjetas por empresa). <!-- id: 33 -->
        - [x] Lógica de "Agregar Vínculo" y Guardado de Identidad. <!-- id: 34 -->

- [x] **Protocolo Multiplex (Fase 4: QA)** <!-- id: 35 -->
    - [x] **Test Escenario Pedro** <!-- id: 36 -->
        - [x] Crear script de simulación `tests/test_qa_pedro.py`. <!-- id: 37 -->
        - [x] Hotfix DB: Agregar columna `roles` JSON. <!-- id: 39 -->
        - [x] Validar persistencia e independencia de estados (ÉXITO). <!-- id: 38 -->
    - [x] **Test UI Feedback (Visual)** <!-- id: 40 -->
        - [x] Implementar Switch Interactivo en Tarjeta Vínculo. <!-- id: 41 -->
        - [x] Verificar reseteo de selectores tras adición. <!-- id: 42 -->
    - [x] **Pruebas de Robustez (Edge Cases)** <!-- id: 43 -->
        - [x] **Prueba 1: El Ataque de los Clones** (Detectar duplicados). <!-- id: 44 -->
            - [x] Implementar validación lógica en `service.py`. <!-- id: 45 -->
        - [x] **Prueba 2: Memoria de Elefante** (Persistencia Personal). <!-- id: 46 -->
            - [x] Verificado que Notas y Canales Personales se guardan. <!-- id: 47 -->

- [x] **Search & Link (Blindaje Identidad)** <!-- id: 48 -->
    - [x] **Backend Search Engine** <!-- id: 49 -->
        - [x] Optimizar `get_contactos` con búsqueda JSON (`canales_personales`). <!-- id: 50 -->
        - [x] Validar con script `test_qa_search.py`. <!-- id: 51 -->
    - [x] **Frontend UX (Typeahead)** <!-- id: 52 -->
        - [x] Implementar Store Action `searchPersonas`. <!-- id: 53 -->
        - [x] Componente `ContactCanvas`: Debounce 300ms + Dropdown UI. <!-- id: 54 -->
        - [x] Lógica de Apropiación (Readonly + Auto-Add Link). <!-- id: 55 -->

- [x] **Protocolo Omega (Cierre)** <!-- id: 9 -->
    - [x] Actualizar BOOTLOADER.md. <!-- id: 10 -->
    - [x] Generar Informe Histórico `2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS`. <!-- id: 11 -->
    - [x] Actualizar `CAJA_NEGRA.md` y `BITACORA_DEV.md`.
    - [x] Crear Manual Técnico `MANUAL_TECNICO_CONTACTOS_V6`.
