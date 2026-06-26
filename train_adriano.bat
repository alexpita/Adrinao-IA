@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo  Adriano IA - TRAINING
echo ============================================================
echo  Cartella: %CD%
echo.

if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo [SETUP] Virtualenv non trovata. Avvio setup.
    call "%ROOT%adriano.bat" setup
    if errorlevel 1 goto :fail
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

echo.
echo [1/4] Verifica GPU e pacchetti
python "%ROOT%scripts\verify_gpu.py"
if errorlevel 1 goto :fail

echo.
echo [2/4] Validazione dataset base
python "%ROOT%scripts\validate_jsonl.py" --kind prompt "%ROOT%data\prompts\adriano_distill_prompts.jsonl" "%ROOT%data\eval\adriano_eval_prompts.jsonl"
if errorlevel 1 goto :fail
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\seed\adriano_seed.jsonl"
if errorlevel 1 goto :fail

echo.
echo [3/4] Preparazione dataset SFT curato
if not exist "%ROOT%data\distilled\teacher_adriano.jsonl" (
    echo ATTENZIONE: data\distilled\teacher_adriano.jsonl non esiste.
    echo Sto preparando il dataset solo con il seed minimo.
    echo Per Adriano serio devi prima fare distillazione: adriano.bat distill
    echo.
)
python "%ROOT%scripts\prepare_sft_dataset.py" --include-short-seed --inputs "%ROOT%data\seed\adriano_seed.jsonl" "%ROOT%data\distilled\teacher_adriano.jsonl" --output "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail

echo.
echo [4/4] Training Adriano QLoRA su dataset curato
python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_curated.yaml"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  Training completato.
echo  Output: outputs\adriano-qwen3-14b-curated-lora
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: training fermato.
echo  Copia le ultime righe di questa finestra e mandamele.
echo ============================================================
pause
exit /b 1

