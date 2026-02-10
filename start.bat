@echo off
TITLE Proyecto Nexus - Launcher
echo ==========================================
echo    Iniciando Proyecto Nexus...
echo ==========================================

:: Iniciar el Servidor (Backend)
echo [+] Iniciando Servidor (FastAPI)...
start cmd /k "cd /d %~dp0server && python main.py"

:: Iniciar el Cliente (Frontend)
echo [+] Iniciando Cliente (Angular)...
start cmd /k "cd /d %~dp0client && npm start"

echo ==========================================
echo    Servidores lanzados en ventanas nuevas.
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:4200
echo ==========================================
pause
