@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo  Adriano IA - SMOKE TRAINING
echo ============================================================
echo  Questo test verifica solo che la pipeline parta.
echo.

if not exist "%ROOT%.venv\Scripts\activate.bat" (
    call "%ROOT%adriano.bat" setup
    if errorlevel 1 goto :fail
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_qlora.yaml"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  Smoke training completato.
echo  Output: outputs\adriano-qwen3-14b-lora
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: smoke training fermato.
echo  Copia le ultime righe di questa finestra e mandamele.
echo ============================================================
pause
exit /b 1

