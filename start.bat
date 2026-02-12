@echo off
setlocal EnableDelayedExpansion
TITLE Proyecto Nexus - Launcher
cd /d "%~dp0"

echo ==========================================
echo    Iniciando Proyecto Nexus...
echo ==========================================

:: 1. Verificacion de Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [!] Python no encontrado. Por favor, instale Python y asegurese de agregarlo al SC PATH.
    pause
    exit /b
)

echo [+] Verificando dependencias de Python...
python -m pip install -r server/requirements.txt
if !errorlevel! neq 0 (
    echo [!] Error al instalar dependencias de Python.
    pause
    exit /b
)

:: 2. Verificacion de Node.js / npm
call npm --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [!] Node.js/npm no encontrado en el PATH.
    echo.
    echo OPCIONES:
    echo   1. Si ya instalaste Node.js, cierra TODAS las ventanas de terminal
    echo      y vuelve a ejecutar este script.
    echo.
    echo   2. Si NO tienes Node.js instalado, descargalo desde:
    echo      https://nodejs.org/
    echo.
    echo   3. Puedes continuar SOLO con el servidor backend (sin frontend)
    echo      presionando 'S' o salir presionando cualquier otra tecla.
    echo.
    set /p "continue=Continuar solo con backend? (S/N): "
    if /i "!continue!"=="S" (
        echo [+] Continuando solo con el backend...
        goto START_BACKEND
    ) else (
        echo [!] Saliendo...
        pause
        exit /b
    )
)

:: 3. Verificacion de dependencias de Node.js (Cliente)
if not exist "client\node_modules" (
    echo [+] Instalando dependencias del cliente (Angular)...
    cd client
    call npm install
    cd ..
)

echo ==========================================
echo    Lanzando aplicaciones...
echo ==========================================

:START_BACKEND
:: Iniciar el Servidor (Backend)
echo [+] Iniciando Servidor (FastAPI)...
start "Nexus Server" cmd /k "cd /d %~dp0server && python main.py"

:: Verificar si npm esta disponible antes de iniciar el cliente
call npm --version >nul 2>&1
if !errorlevel! equ 0 (
    :: Iniciar el Cliente (Frontend)
    echo [+] Iniciando Cliente (Angular)...
    start "Nexus Client" cmd /k "cd /d %~dp0client && npm start"
    echo ==========================================
    echo    Servidores lanzados en ventanas nuevas.
    echo    Backend: http://localhost:8000
    echo    Frontend: http://localhost:4200
    echo ==========================================
) else (
    echo ==========================================
    echo    Servidor Backend lanzado.
    echo    Backend: http://localhost:8000
    echo    (Frontend no disponible - npm no encontrado)
    echo ==========================================
)
pause
