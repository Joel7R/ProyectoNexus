@echo off
SETLOCAL EnableDelayedExpansion

:: --- Estética de la consola ---
color 0B
echo ====================================================
echo    🚀 GAMING NEXUS: INSTALADOR AUTOMATICO (WINDOWS)
echo ====================================================

:: 1. Verificación de versiones base
echo.
echo [1/4] Verificando requisitos del sistema...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.12 y añadelo al PATH.
    pause
    exit /b
)

node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no encontrado. Instala Node v22.
    pause
    exit /b
)
echo [OK] Versiones base detectadas correctamente.

:: 2. Configuración del Backend (FastAPI)
echo.
echo [2/4] Configurando Backend (FastAPI + LangGraph)...
if not exist "server" mkdir server
cd server

echo Creando entorno virtual en Python 3.12...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el venv. Verifica tu instalacion de Python.
    pause
    exit /b
)

echo Instalando dependencias del Backend...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install "fastapi>=0.109.0" "uvicorn[standard]" langchain langgraph ollama google-generativeai ddgs beautifulsoup4 langdetect pydantic-settings sse-starlette python-dotenv
cd ..

:: 3. Configuración del Frontend (Angular 19)
echo.
echo [3/4] Configurando Frontend (Angular 19)...
if not exist "client" mkdir client
cd client

echo Instalando Angular CLI v19 globalmente...
call npm install -g @angular/cli@19.1.0

echo Instalando dependencias del Frontend...
call npm install
cd ..

:: 4. Resumen Final
echo.
echo ====================================================
echo    ✅ ¡INSTALACION COMPLETADA CON EXITO!
echo ====================================================
echo.
echo Para lanzar el proyecto, usa los siguientes comandos:
echo.
echo BACKEND:
echo    cd server ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo.
echo FRONTEND:
echo    cd client ^&^& ng serve
echo.
echo ====================================================
pause