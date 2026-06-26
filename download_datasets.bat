@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo  Adriano IA - download dataset esterni
echo ============================================================
echo  Destinazione: data\external
echo.

if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo [SETUP] Virtualenv non trovata. Avvio setup.
    call "%ROOT%adriano.bat" setup
    if errorlevel 1 goto :fail
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

python "%ROOT%scripts\download_italian_datasets.py" %*
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  Download completato.
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: download dataset fermato.
echo  Copia le ultime righe di questa finestra e mandamele.
echo ============================================================
pause
exit /b 1

