# 🤖 BLUEPRINT TÉCNICO: PROYECTO "OPEN GRAVITY"
**Versión:** 1.0 (Estrategia de Independencia)
**Fecha:** 09-Mar-2026
**Objetivo:** Guía de implementación rápida para agentes de IA autónomos con capacidades multimodales (Voz/Telegram/Automatización) sin rediseñar el núcleo V5.

---

## 🏗️ 1. ARQUITECTURA DEL SISTEMA (STACK RECOMENDADO)
Para que yo (u otro agente) pueda reconstruir este sistema rápidamente, necesitaremos:

1.  **Orquestador:** Google Antigravity (Modo Planning/Fast).
2.  **Lenguaje:** Node.js (Recomendado por el video para alta concurrencia) o Python (Si preferimos mantener la paridad con V5).
3.  **Cerebro (LLMs):** 
    - **Groq API:** Para velocidad extrema (Llama 3.3 / Mixtral). Gratis/Low Cost.
    - **OpenRouter API:** Como fallback para modelos premium (Claude/GPT-4).
4.  **Canales (Interface):**
    - **Telegram Bot API:** El portal de comunicación móvil.
5.  **Memoria y Persistencia:**
    - **Firebase (Firestore):** Almacenamiento NoSQL para historial de conversaciones e "identidad" del agente.
6.  **Voz y Multimodalidad:**
    - **Groq (Whisper):** Para transcripción de audios de usuario (Voz -> Texto).
    - **ElevenLabs API:** Para síntesis de voz del agente (Texto -> Voz).

---

## 🔑 2. INVENTARIO DE CREDENCIALES (REQUERIDO)
Para iniciar la ejecución, el usuario deberá proveer las siguientes llaves (keys) en un archivo `.env` independiente:

| Plataforma | Propósito | Dónde obtener |
| :--- | :--- | :--- |
| **Grok API** | Inferencia de IA (Cerebro) | [console.groq.com](https://console.groq.com) |
| **OpenRouter** | Fallback de modelos | [openrouter.ai](https://openrouter.ai) |
| **BotFather** | Telegram Token | App Telegram -> `@BotFather` |
| **ElevenLabs** | Generación de Voz | [elevenlabs.io](https://elevenlabs.io) |
| **Firebase** | Base de datos en la nube | [console.firebase.google.com](https://console.firebase.google.com) |
| **Google Cloud** | Acceso a Gmail/Calendar (MCP) | [console.cloud.google.com](https://console.cloud.google.com) |

---

## 🚀 3. ROADMAP DE IMPLEMENTACIÓN (MISIÓN SEPARADA)

### FASE 1: El "Cuerpo" Digital (Telegram + Brain)
1. Instanciar un servidor básico en Node.js/Python.
2. Conectar el Webhook de Telegram.
3. Integrar Groq para respuestas en tiempo real.
4. **Resultado:** Un chat de Telegram inteligente.

### FASE 2: La "Memoria" Inmortal (Firestore)
1. Vincular el proyecto con Firebase.
2. Crear un esquema de documentos `conversaciones/userID/mensajes`.
3. Implementar lógica de recuperación de contexto (RAG light).
4. **Resultado:** El agente te reconoce y recuerda qué charlaron ayer.

### FASE 3: Sentidos Expandidos (Oído y Habla)
1. Implementar manejador de archivos `.ogg` (Telegram Voice).
2. Enviar audio a Groq (Whisper) para transcripción.
3. Convertir la respuesta del LLM a audio con ElevenLabs.
4. **Resultado:** Operación manos libres total.

### FASE 4: El "Mayordomo" (Herramientas MCP)
1. Conectar servidor MCP para Google Workspace.
2. Dar permisos para leer Gmail y Calendar.
3. **Resultado:** El agente puede agendar entregas o avisarte si llegó un mail de un cliente.

---

## 📝 4. NOTA ESTRATÉGICA PARA EL AGENTE FUTURO
> *"Si recibís este documento, no intentes modificar el backend de Clientes de Sonido Líquido todavía. Primero creá una carpeta independiente llamada `/OpenGravity` y construí el bot de Telegram ahí. Una vez que el bot 'escuche' y 'hable', usaremos el `AfipBridgeService` de V5 como herramienta (tool) para que el bot pueda consultar datos de la base de datos de la empresa."*

---
**ESTADO DE MISIÓN:** BLUEPRINT SELLADO Y LISTO PARA DESPLIEGUE.
