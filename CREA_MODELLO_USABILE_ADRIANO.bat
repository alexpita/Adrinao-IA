@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo  ADRIANO IA - CREA MODELLO USABILE
echo ============================================================
echo.

if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo [SETUP] Ambiente non trovato.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\setup_env.ps1"
    if errorlevel 1 goto :fail
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

set "ADAPTER=%ROOT%outputs\adriano-qwen3-14b-curated-lora"
if not exist "%ADAPTER%" (
    set "ADAPTER=%ROOT%outputs\adriano-qwen3-14b-lora"
)
if not exist "%ADAPTER%" (
    echo ERRORE: nessun adapter trovato.
    echo Prima fai doppio click su TRAINA_TUTTO_ADRIANO.bat
    goto :fail
)

echo Adapter usato:
echo %ADAPTER%
echo.

echo [1/2] Merge + export GGUF
python "%ROOT%scripts\merge_or_export.py" --adapter "%ADAPTER%" --merged-output "%ROOT%outputs\adriano-merged" --gguf-output "%ROOT%outputs\adriano-gguf" --gguf-quant q4_k_m
if errorlevel 1 goto :fail

echo.
echo [2/2] Creazione Modelfile Ollama
python "%ROOT%scripts\create_ollama_modelfile.py" --gguf-dir "%ROOT%outputs\adriano-gguf" --output "%ROOT%outputs\ollama\Modelfile"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  MODELLO CREATO
echo  Merged: outputs\adriano-merged
echo  GGUF:   outputs\adriano-gguf
echo  Ollama: outputs\ollama\Modelfile
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: creazione modello fermata.
echo  Mandami le ultime righe di questa finestra.
echo ============================================================
pause
exit /b 1

