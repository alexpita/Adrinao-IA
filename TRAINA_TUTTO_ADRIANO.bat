@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo  ADRIANO IA - TRAINING TUTTO COMPRESO
echo ============================================================
echo.

if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo [1/8] Setup ambiente
    powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\setup_env.ps1"
    if errorlevel 1 goto :fail
) else (
    echo [1/8] Ambiente trovato
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

python -c "import rich, yaml, torch, unsloth, datasets" 1>nul 2>nul
if errorlevel 1 (
    echo [2/8] Dipendenze incomplete: completo setup
    powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\setup_env.ps1"
    if errorlevel 1 goto :fail
    call "%ROOT%.venv\Scripts\activate.bat"
    if errorlevel 1 goto :fail
) else (
    echo [2/8] Dipendenze ok
)

echo [3/8] Verifica GPU
python "%ROOT%scripts\verify_gpu.py"
if errorlevel 1 goto :fail

echo.
echo [4/8] Download dataset esterni
if not exist "%ROOT%data\external\camoscio" (
    python "%ROOT%scripts\download_italian_datasets.py"
    if errorlevel 1 goto :fail
) else (
    echo data\external\camoscio gia presente: salto download.
)

echo.
echo [5/8] Conversione dataset esterni in SFT
python "%ROOT%scripts\convert_external_to_sft.py"
if errorlevel 1 goto :fail

echo.
echo [6/8] Creazione dataset distillato locale
python "%ROOT%scripts\create_local_distilled_dataset.py" --input "%ROOT%data\curated\external_sft.jsonl" --output "%ROOT%data\distilled\teacher_adriano.jsonl"
if errorlevel 1 goto :fail

echo.
echo [7/8] Preparazione dataset finale
python "%ROOT%scripts\prepare_sft_dataset.py" --include-short-seed --inputs "%ROOT%data\seed\adriano_seed.jsonl" "%ROOT%data\distilled\teacher_adriano.jsonl" --output "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail

echo.
echo [8/8] Training Adriano
python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_curated.yaml"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  TRAINING COMPLETATO
echo  Adapter: outputs\adriano-qwen3-14b-curated-lora
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: training tutto compreso fermato.
echo  Mandami le ultime righe di questa finestra.
echo ============================================================
pause
exit /b 1
