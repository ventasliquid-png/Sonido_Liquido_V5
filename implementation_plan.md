# Plan de Ejecución: Protocolo Omega (Fase 1 & 2 - Documental)

## Objetivo
Cerrar formalmente la sesión de reingeniería de Contactos (Multiplex N:M) y Search & Link, documentando los cambios estructurales profundos y preparando el terreno para la siguiente fase.

## 1. Actualización de Bitácora (`BITACORA_DEV.md`)
- [ ] Registrar el hito "Reingeniería N:M y Blindaje de Identidad".
- [ ] Documentar la solución a la "Paradoja de Pedro" (Modelo Persona-Vínculo).
- [ ] Mencionar el hotfix de dependencias circulares en scripts de QA.
- [ ] Registrar la implementación de Search & Link (Typeahead + Debounce).

## 2. Actualización de Caja Negra (`CAJA_NEGRA.md`)
- [ ] Incrementar contador de sesiones (+1).
- [ ] Actualizar estado del módulo Contactos a "🟢 N:M MULTIPLEX".
- [ ] Registrar incidentes resueltos (Error 500 en `joinedload`).

## 3. Manual Técnico (Nueva Sección en `MANUAL_TECNICO_V5.md` o Anexo)
- [ ] **Modelo Persona-Vínculo**: Diagrama conceptual.
- [ ] **Eschema de Canales**: Explicación de `canales_personales` (JSON en Persona) vs `canales_laborales` (JSON en Vinculo).
- [ ] **Lógica de Búsqueda**: Documentar el endpoint de búsqueda profunda en JSON y el debounce de 300ms en Frontend.

## 4. Informe Histórico (`INFORMES_HISTORICOS/2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS.md`)
- [ ] Contexto: La necesidad de romper la relación 1:1.
- [ ] Detalle Técnico:
    -   Refactor de `models.py` (Polimorfismo).
    -   Servicio `get_contactos` con `joinedload` para evitar N+1 y Error 500.
    -   Solución a Dependencias Circulares (Imports dentro de métodos/scripts).
    -   Script de Migración `migrate_v6_multiplex.py`.
- [ ] Resultado QA: Éxito en tests de Pedro y Robustez (Duplicados).

## 5. Bootloader (`_GY/BOOTLOADER.md`)
- [ ] Definir objetivo táctico siguiente: "Validación de Billetera de Vínculos bajo estrés".

## Solicitud de Aprobación
Este plan cubre todas las directivas del PIN 1974.
Una vez aprobado (o tácitamente aceptado al ver este archivo), procederé a la escritura de los documentos.
