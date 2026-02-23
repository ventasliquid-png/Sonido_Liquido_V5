import asyncio
import os
import sys

# Add root to path
sys.path.insert(0, os.getcwd())

from backend.services.model_discernitor import ModelDiscernitor

async def test_discernitor():
    print("--- Test Discernitor ---")
    
    async def mid_callback(prompt, model):
        print(f"Callback ejecutado con: {model}")
        return "Respuesta OK"

    print("Iniciando ejecución...")
    await ModelDiscernitor.execute_with_fallback("hola", mid_callback)
    
    telemetry = ModelDiscernitor.get_telemetry()
    print(f"Telemetría: {telemetry}")
    
    if telemetry['flash_count'] > 0:
        print("SUCCESS: El contador Flash se incrementó.")
    else:
        print("FAIL: El contador Flash sigue en 0.")

if __name__ == "__main__":
    asyncio.run(test_discernitor())
