@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONWARNINGS=ignore::FutureWarning"
set "HF_HUB_DISABLE_PROGRESS_BARS=1"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "TRANSFORMERS_NO_ADVISORY_WARNINGS=1"
set "GLOG_minloglevel=2"
set "FLAGS_minloglevel=2"
set "LOGDIR=%ROOT%logs"
set "TRAIN_LOG=%LOGDIR%\training_latest.log"
set "OUTPUT_DIR=%ROOT%outputs\adriano-qwen3-14b-curated-lora"
set "RUN_MARKER=%ROOT%outputs\.adriano_training_active"
set "TRAINING_PROFILE_VERSION=curated-packing-2epochs-v3"
set "RESUME_MODE=auto"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo.
echo ============================================================
echo  ADRIANO IA - TRAINING TUTTO COMPRESO
echo ============================================================
echo  Log training: logs\training_latest.log
echo.

if not exist "%ROOT%outputs" mkdir "%ROOT%outputs"
set "NEEDS_CLEAN=1"
if exist "%RUN_MARKER%" (
    set "ACTIVE_PROFILE="
    set /p ACTIVE_PROFILE=<"%RUN_MARKER%"
    if "!ACTIVE_PROFILE!"=="%TRAINING_PROFILE_VERSION%" (
        echo [0/8] Run precedente interrotta: resume automatico dai checkpoint
        set "RESUME_MODE=auto"
        set "NEEDS_CLEAN=0"
    ) else (
        echo [0/8] Profilo training cambiato: ripartenza pulita
    )
)

if "!NEEDS_CLEAN!"=="1" (
    echo [0/8] Ripartenza da zero: pulizia output e dataset generati
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$root=(Resolve-Path '%ROOT%').Path; $targets=@('%OUTPUT_DIR%','%TRAIN_LOG%','%ROOT%data\distilled\teacher_adriano.jsonl','%ROOT%data\curated\adriano_sft.jsonl','%ROOT%data\curated\adriano_sft_report.json'); foreach($target in $targets){ if(Test-Path -LiteralPath $target){ $resolved=(Resolve-Path -LiteralPath $target).Path; if($resolved.StartsWith($root,[System.StringComparison]::OrdinalIgnoreCase)){ Remove-Item -LiteralPath $resolved -Recurse -Force } else { throw \"Target fuori progetto: $resolved\" } } }"
    if errorlevel 1 goto :fail
    echo %TRAINING_PROFILE_VERSION%>"%RUN_MARKER%"
    set "RESUME_MODE=never"
)

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
echo [6/8] Creazione DISTILLER locale e dataset distillato
python "%ROOT%scripts\create_local_distilled_dataset.py" --input "%ROOT%data\curated\external_sft.jsonl" --output "%ROOT%data\distilled\teacher_adriano.jsonl"
if errorlevel 1 goto :fail

echo.
echo [7/8] Preparazione dataset finale
python "%ROOT%scripts\prepare_sft_dataset.py" --include-short-seed --inputs "%ROOT%data\seed\adriano_seed.jsonl" "%ROOT%data\distilled\teacher_adriano.jsonl" --output "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 goto :fail

echo.
echo [8/8] Training Adriano con resume automatico
python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_curated.yaml" --resume "%RESUME_MODE%" --log-file "%TRAIN_LOG%"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo  TRAINING COMPLETATO
echo  Adapter: outputs\adriano-qwen3-14b-curated-lora
echo  Log: logs\training_latest.log
echo ============================================================
if exist "%RUN_MARKER%" del "%RUN_MARKER%" >nul 2>nul
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: training tutto compreso fermato.
echo  Log salvato in: logs\training_latest.log
echo  Mandami quel file o le ultime righe della finestra.
echo ============================================================
pause
exit /b 1
