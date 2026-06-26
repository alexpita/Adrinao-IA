@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "MODE=%~1"
if "%MODE%"=="" set "MODE=all"

echo.
echo ============================================================
echo  Adriano IA - Windows launcher
echo ============================================================
echo  Cartella: %CD%
echo  Modalita: %MODE%
echo.

if /I "%MODE%"=="help" goto :help
if /I "%MODE%"=="setup" goto :setup_only
if /I "%MODE%"=="verify" goto :verify_only
if /I "%MODE%"=="validate-data" goto :validate_data_only
if /I "%MODE%"=="context-plan" goto :context_plan_only
if /I "%MODE%"=="distill" goto :distill_only
if /I "%MODE%"=="curate" goto :curate_only
if /I "%MODE%"=="train" goto :train_only
if /I "%MODE%"=="train-curated" goto :train_curated_only
if /I "%MODE%"=="chat" goto :chat_only
if /I "%MODE%"=="all" goto :all

echo Modalita non riconosciuta: %MODE%
goto :help

:all
call :setup
if errorlevel 1 goto :fail
call :verify
if errorlevel 1 goto :fail
call :train
if errorlevel 1 goto :fail
call :chat
if errorlevel 1 goto :fail
goto :done

:setup_only
call :setup
if errorlevel 1 goto :fail
goto :done

:verify_only
call :activate
if errorlevel 1 goto :fail
call :verify
if errorlevel 1 goto :fail
goto :done

:train_only
call :activate
if errorlevel 1 goto :fail
call :train
if errorlevel 1 goto :fail
goto :done

:train_curated_only
call :activate
if errorlevel 1 goto :fail
call :train_curated
if errorlevel 1 goto :fail
goto :done

:validate_data_only
call :activate
if errorlevel 1 goto :fail
call :validate_data
if errorlevel 1 goto :fail
goto :done

:context_plan_only
call :activate
if errorlevel 1 goto :fail
call :context_plan
if errorlevel 1 goto :fail
goto :done

:distill_only
call :activate
if errorlevel 1 goto :fail
call :distill
if errorlevel 1 goto :fail
goto :done

:curate_only
call :activate
if errorlevel 1 goto :fail
call :curate
if errorlevel 1 goto :fail
goto :done

:chat_only
call :activate
if errorlevel 1 goto :fail
call :chat
if errorlevel 1 goto :fail
goto :done

:setup
echo.
echo [1/4] Setup ambiente Python, Torch, Unsloth
echo Questo passaggio puo scaricare diversi GB.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\setup_env.ps1"
if errorlevel 1 exit /b 1
call :activate
if errorlevel 1 exit /b 1
exit /b 0

:activate
if not exist "%ROOT%.venv\Scripts\activate.bat" (
    echo ERRORE: virtualenv non trovata. Esegui prima: adriano.bat setup
    exit /b 1
)
call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1
exit /b 0

:verify
echo.
echo [2/4] Verifica GPU e pacchetti
python "%ROOT%scripts\verify_gpu.py"
if errorlevel 1 exit /b 1
exit /b 0

:validate_data
echo.
echo [DATA] Validazione prompt, seed ed eval set
python "%ROOT%scripts\validate_jsonl.py" --kind prompt "%ROOT%data\prompts\adriano_distill_prompts.jsonl" "%ROOT%data\eval\adriano_eval_prompts.jsonl"
if errorlevel 1 exit /b 1
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\seed\adriano_seed.jsonl"
if errorlevel 1 exit /b 1
exit /b 0

:context_plan
echo.
echo [CTX] Stima memoria contesto lungo
python "%ROOT%scripts\estimate_context_memory.py" --tokens 32768
if errorlevel 1 exit /b 1
echo.
python "%ROOT%scripts\estimate_context_memory.py" --tokens 131072
if errorlevel 1 exit /b 1
echo.
python "%ROOT%scripts\estimate_context_memory.py" --tokens 524288
if errorlevel 1 exit /b 1
exit /b 0

:distill
echo.
echo [DATA] Distillazione dal teacher
if "%TEACHER_BASE_URL%"=="" (
    echo ERRORE: imposta TEACHER_BASE_URL.
    echo Esempio: set TEACHER_BASE_URL=http://localhost:8000/v1
    exit /b 1
)
if "%TEACHER_API_KEY%"=="" (
    echo ERRORE: imposta TEACHER_API_KEY.
    echo Esempio: set TEACHER_API_KEY=local
    exit /b 1
)
if "%TEACHER_MODEL%"=="" (
    echo ERRORE: imposta TEACHER_MODEL.
    echo Esempio: set TEACHER_MODEL=qwen3.6-27b-instruct
    exit /b 1
)
python "%ROOT%scripts\distill_from_teacher.py" --input "%ROOT%data\prompts\adriano_distill_prompts.jsonl" --output "%ROOT%data\distilled\teacher_adriano.jsonl"
if errorlevel 1 exit /b 1
exit /b 0

:curate
echo.
echo [DATA] Preparazione dataset SFT curato
python "%ROOT%scripts\prepare_sft_dataset.py" --include-short-seed --inputs "%ROOT%data\seed\adriano_seed.jsonl" "%ROOT%data\distilled\teacher_adriano.jsonl" --output "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 exit /b 1
python "%ROOT%scripts\validate_jsonl.py" --kind chat "%ROOT%data\curated\adriano_sft.jsonl"
if errorlevel 1 exit /b 1
exit /b 0

:train
echo.
echo [3/4] Training smoke test Adriano
echo Output: outputs\adriano-qwen3-14b-lora
python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_qlora.yaml"
if errorlevel 1 exit /b 1
exit /b 0

:train_curated
echo.
echo [TRAIN] Training Adriano su dataset curato
if not exist "%ROOT%data\curated\adriano_sft.jsonl" (
    echo ERRORE: dataset curato non trovato. Esegui prima: adriano.bat curate
    exit /b 1
)
python "%ROOT%scripts\train_qlora.py" --config "%ROOT%configs\adriano_qwen3_14b_curated.yaml"
if errorlevel 1 exit /b 1
exit /b 0

:chat
echo.
echo [4/4] Chat locale Adriano
python "%ROOT%scripts\chat_adriano.py" --adapter "%ROOT%outputs\adriano-qwen3-14b-lora"
if errorlevel 1 exit /b 1
exit /b 0

:help
echo.
echo Uso:
echo   adriano.bat          setup + verify + train + chat
echo   adriano.bat setup    installa ambiente e dipendenze
echo   adriano.bat verify   verifica GPU e pacchetti
echo   adriano.bat validate-data  valida prompt, seed ed eval
echo   adriano.bat context-plan  stima memoria per 32k/128k/512k
echo   adriano.bat distill  genera dati dal teacher
echo   adriano.bat curate   prepara data\curated\adriano_sft.jsonl
echo   adriano.bat train    avvia solo il training smoke test
echo   adriano.bat train-curated  training sul dataset curato
echo   adriano.bat chat     avvia solo la chat
echo.
pause
exit /b 0

:fail
echo.
echo ============================================================
echo  ERRORE: Adriano si e fermato.
echo  Copia le ultime righe di questa finestra e mandamele.
echo ============================================================
pause
exit /b 1

:done
echo.
echo ============================================================
echo  Adriano completato.
echo ============================================================
pause
exit /b 0
