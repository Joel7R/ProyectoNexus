@echo off
SETLOCAL EnableDelayedExpansion

:: --- Estética de la consola ---
color 0A
echo ====================================================
echo    🚀 GAMING NEXUS: LANZADOR (WINDOWS)
echo ====================================================

:: 1. Verificación de entorno
echo.
echo [1/3] Verificando entorno...

:: Verificar Backend
if not exist "server\venv\Scripts\activate.bat" (
    echo [ERROR] Entorno del Backend no encontrado en "server\venv".
    echo         Por favor ejecuta "setup_nexus.bat" primero para instalar las dependencias.
    pause
    exit /b
)

:: Verificar Frontend
if not exist "client\node_modules" (
    echo [ERROR] Dependencias del Frontend no encontradas en "client\node_modules".
    echo         Por favor ejecuta "setup_nexus.bat" primero para instalar las dependencias.
    pause
    exit /b
)

echo [OK] Entornos verificados correctamente.

:: 2. Lanzar Backend
echo.
echo [2/3] Iniciando Servidor Backend (Puerto 8000)...
start "Gaming Nexus Backend" cmd /k "cd server && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: 3. Lanzar Frontend
echo.
echo [3/3] Iniciando Cliente Frontend (Puerto 4200)...
:: El parametro -o abre el navegador automaticamente
start "Gaming Nexus Frontend" cmd /k "cd client && ng serve -o"

echo.
echo ====================================================
echo    ✅ SISTEMAS INICIADOS!
echo ====================================================
echo.
echo Backend disponible en: http://localhost:8000
echo Frontend disponible en: http://localhost:4200
echo.
echo Puedes cerrar esta ventana, los servidores seguiran corriendo
echo en sus propias ventanas.
pause
