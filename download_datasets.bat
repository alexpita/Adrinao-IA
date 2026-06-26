@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"
set "NO_PAUSE=0"
set "ARGS=%*"
if /I "%~1"=="--no-pause" (
    set "NO_PAUSE=1"
    set "ARGS=%ARGS:--no-pause=%"
)

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

python "%ROOT%scripts\download_italian_datasets.py" %ARGS%
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  Download completato.
echo ============================================================
if "%NO_PAUSE%"=="1" exit /b 0
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: download dataset fermato.
echo  Copia le ultime righe di questa finestra e mandamele.
echo ============================================================
if "%NO_PAUSE%"=="1" exit /b 1
pause
exit /b 1
