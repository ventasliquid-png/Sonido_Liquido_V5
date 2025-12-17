
import os

append_text = """
## Pendientes para esta sesión (Rescatado de OF)

### Hallazgos y Pendientes
1.  **Campo OC (Orden de Compra):** Existe en BD (pedidos.oc) pero falta en:
    *   Schema PedidoResponse (Backend).
    *   UI PedidoTacticoView (Input explícito).
    *   UI PedidoInspector (Edición).
2.  **UX Táctico:** Falta botón 'Limpiar/Nuevo' explícito para resetear el borrador sin recargar.
3.  **Plan de Acción:** Se generó el implementation_plan.md para abordar estos puntos en la próxima sesión.

### Nota Post-Cierre
Se intentó correr una 'Simulación de Integridad' (Frontend Build + Backend Tests), pero se abortó por falta de tiempo. Queda pendiente verificar el estado del servidor y tests de integración en la próxima sesión.
"""

print(f"Appending to BITACORA_DEV.md...")
try:
    with open("BITACORA_DEV.md", "a", encoding="utf-8") as f:
        f.write(append_text)
    print("Append successful.")
except Exception as e:
    print(f"Error appending: {e}")
    exit(1)

files_to_delete = ["BITACORA_OF_PENDIENTE.md", "BITACORA_DEV_20251215.md"]
for f in files_to_delete:
    print(f"Deleting {f}...")
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted {f}.")
        else:
            print(f"{f} not found.")
    except Exception as e:
        print(f"Error deleting {f}: {e}")
