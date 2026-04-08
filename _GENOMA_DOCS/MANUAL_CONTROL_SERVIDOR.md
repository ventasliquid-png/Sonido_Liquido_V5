# MANUAL DE CONTROL DE SERVIDOR (OPS)

**OBJETIVO:** Gestionar el encendido y apagado de la instancia de base de datos `v5-crisol-micro` para optimizar costos.

---

## OPCIÓN 1: AUTOMATIZACIÓN TOTAL (Nivel Dios)
*Recomendado para horarios fijos (ej. Lunes a Viernes de 9 a 18).*

Google Cloud tiene una función nativa para esto. No necesitas scripts.

1.  Entra a la [Consola de Cloud SQL](https://console.cloud.google.com/sql/instances).
2.  Haz clic en el nombre de tu instancia: **`v5-crisol-micro`**.
3.  En el menú lateral izquierdo, busca **"Programaciones de instancias" (Instance schedules)**.
4.  Haz clic en **"Crear programación"**.
5.  Configura tus horarios:
    *   **Inicio:** Ej. 08:00 AM
    *   **Fin:** Ej. 20:00 PM
    *   **Días:** Lunes a Viernes.
6.  ¡Listo! Google se encarga del resto.

---

## OPCIÓN 2: CONTROL MANUAL RÁPIDO (Nivel Táctico)
*Recomendado para sesiones de desarrollo fuera de hora o fines de semana.*

He creado dos "botones nucleares" en tu carpeta `scripts/control_db`.

### Para ENCENDER:
Ejecuta (doble clic):
`c:\dev\Sonido_Liquido_V5\scripts\control_db\encender_db.bat`

### Para APAGAR:
Ejecuta (doble clic):
`c:\dev\Sonido_Liquido_V5\scripts\control_db\apagar_db.bat`

> **Nota:** Estos scripts usan `gcloud` que ya tienes instalado y autenticado.

---

## NOTA SOBRE COSTOS
Una instancia `db-f1-micro` (o similar) apagada cobra **casi cero** (solo pagas el almacenamiento, que son centavos). Encendida 24/7 cuesta dinero real.
**¡APÁGALA SIEMPRE QUE NO LA USES!**
