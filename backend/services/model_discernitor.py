import datetime
import logging
import json
import os
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

class ModelDiscernitor:
    """
    Ordenador de Tráfico para la API de Gemini.
    Gestiona dinámicamente el ruteo entre modelos Pro y Flash según la complejidad del texto
    y los estados de penalización (Error 429 - Quota Exceeded).
    """
    
    _cooldown_until: Optional[datetime.datetime] = None
    flash_count = 0
    pro_count = 0
    total_flash_count = 0
    total_pro_count = 0
    _telemetry_loaded = False
    
    @classmethod
    def _ensure_telemetry_loaded(cls):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = "atenea_telemetry.json"
        
        # Siempre intentamos cargar del disco para sincronizar procesos
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                if data.get("date") == today_str:
                    cls.total_flash_count = data.get("total_flash_count", 0)
                    cls.total_pro_count = data.get("total_pro_count", 0)
                else:
                    cls._save_telemetry(reset=True)
            except:
                cls._save_telemetry(reset=True)
        else:
            cls._save_telemetry(reset=True)
            
        cls._telemetry_loaded = True

    @classmethod
    def _log_debug(cls, msg):
        with open("discernitor_debug.log", "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

    @classmethod
    def _save_telemetry(cls, reset=False):
        if reset:
            cls.total_flash_count = 0
            cls.total_pro_count = 0
            
        data = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "total_flash_count": cls.total_flash_count,
            "total_pro_count": cls.total_pro_count
        }
        try:
            with open("atenea_telemetry.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error guardando telemetria: {e}")

    @classmethod
    def get_telemetry(cls) -> Dict[str, Any]:
        """Devuelve el estado de telemetría actual del Discernidor."""
        cls._ensure_telemetry_loaded()
        
        cooldown = cls._is_in_cooldown()
        segundos = 0
        if cooldown and cls._cooldown_until:
            delta = cls._cooldown_until - datetime.datetime.now()
            segundos = int(max(0, delta.total_seconds()))
            
        return {
            "flash_count": cls.flash_count,
            "pro_count": cls.pro_count,
            "total_flash_count": cls.total_flash_count,
            "total_pro_count": cls.total_pro_count,
            "is_cooldown": cooldown,
            "segundos_restantes": segundos
        }

    @classmethod
    def _is_in_cooldown(cls) -> bool:
        """Verifica si el sistema está bajo penalización por cuota excedida."""
        if cls._cooldown_until and datetime.datetime.now() < cls._cooldown_until:
            return True
        return False

    @staticmethod
    def analyze_prompt(prompt: str) -> str:
        """
        Decide el motor óptimo basado en reglas heurísticas (Embudo V2).
        Si hay cooldown activo o se detectan logs, retorna Flash.
        Si hay palabras de arquitectura/lógica, retorna Pro.
        Por defecto, retorna Flash.
        """
        model_flash = 'gemini-3.0-flash'
        model_pro = 'gemini-3.1-pro'

        if ModelDiscernitor._is_in_cooldown():
            # Bypass en estado de contingencia
            return model_flash

        prompt_lower = prompt.lower()
        
        # Filtro 1: Basura/Logs (Van crudos a Flash)
        log_keywords = [
            "uncaught", "typeerror", "[vue warn]", "webpack-internal", "node_modules",
            "traceback", "most recent call last", 'file "', "line ", 
            "internal server error", "fastapi", "uvicorn", "sqlalchemy"
        ]
        
        if any(keyword in prompt_lower for keyword in log_keywords):
            return model_flash
        
        # Filtro 2: Arquitectura y Lógica Pesada (Requieren Pro)
        heavy_keywords = [
            "código", "codigo", 
            "refactorizar", "refactor",
            "arquitectura", "architecture",
            "diseño", "diseno",
            "regex", "regular expression",
            "lógica", "logica", "logic"
        ]
        
        if any(keyword in prompt_lower for keyword in heavy_keywords):
            return model_pro
            
        # Default: Fallback eficiente
        return model_flash

    @classmethod
    async def execute_with_fallback(
        cls, 
        prompt: str, 
        execution_callback: Callable[[str, str], Any],  # Espera funcion async (prompt, model_name)
        *args, 
        **kwargs
    ) -> Any:
        """
        Ejecutor encapsulado.
        Intenta llamar al callback de ejecución con el modelo decidido.
        Si falla con 429 y estaba usando Pro, activa cooldown, degrada a Flash y reintenta.
        
        :param prompt: El texto base a analizar para deducir el motor y también enviarlo.
        :param execution_callback: La función (o wrapper) encargada de realizar el llamado real a la API.
        """
        
        cls._ensure_telemetry_loaded()
        model_name = cls.analyze_prompt(prompt)
        cls._log_debug(f"Prompt Analizado. Decisión: {model_name}. Prompt length: {len(prompt)}")
        
        # Incrementar contadores estáticamente
        if model_name == 'gemini-3.0-flash':
            cls.flash_count += 1
            cls.total_flash_count += 1
        elif model_name == 'gemini-3.1-pro':
            cls.pro_count += 1
            cls.total_pro_count += 1
        
        cls._save_telemetry()
        cls._log_debug(f"Contadores incrementados: S_F={cls.flash_count}, S_P={cls.pro_count}, T_F={cls.total_flash_count}, T_P={cls.total_pro_count}")
            
        try:
            # 1. Intento Misión Primaria
            return await execution_callback(prompt, model_name, *args, **kwargs)
            
        except Exception as e:
            error_str = str(e).lower()
            
            # 2. Atrape Misión Secundaria (Error 429 Quota Exceeded)
            # Detectamos "429" o "exceeded" 
            is_quota_error = "429" in error_str or "quota" in error_str or "exceeded" in error_str
            
            if is_quota_error and model_name == 'gemini-3.1-pro':
                logger.warning(
                    f"⚠️ [Discernitor] Error 429 detectado en modelo PRO. "
                    f"Activando Cooldown Táctico (1 hora) y degradando a FLASH."
                )
                
                # Penalización: Bloqueamos peticiones Pro por 1 hora
                # (Idealmente se lee Retry-After, aquí usamos default seguro)
                cls._cooldown_until = datetime.datetime.now() + datetime.timedelta(hours=1)
                
                # REINICIO ODOMETROS POR 429
                cls._save_telemetry(reset=True)
                
                # Fallback: Reintento transparente con Flash
                fallback_model = 'gemini-3.0-flash'
                logger.info(f"🔄 [Discernitor] Ejecutando Fallback Transparente con {fallback_model}...")
                cls.pro_count -= 1 # Revertir la cuenta fallida
                cls.flash_count += 1
                
                # Sumar a total ya que fue reseteado arriba y esto cuenta como uso flash
                cls.total_flash_count += 1
                cls._save_telemetry()
                
                return await execution_callback(prompt, fallback_model, *args, **kwargs)
                
            else:
                # Si el error es otro, o ya estábamos en Flash, elevamos la excepción.
                raise e
