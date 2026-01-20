@echo off
TITLE MODO DESARROLLO - V5
cd /d "%~dp0"
echo Copiando prompt de inicio al portapapeles...
:: Aquí preparamos el Prompt Maestro para que se copie solo
echo Gy, iniciamos sesion. Carga tu doctrina desde _GY/_IPL/GY_IPL_V9.md. Confirma que tu zona de escritura es _GY/_MD y reporta estado. IOWA OFF, GIT ON. | clip
echo.
echo [PROMPT COPIADO]
echo Abriendo VS Code...
code .
exit
