param(
    [string]$PythonVersion = "3.12",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

Write-Host "== Adriano environment setup =="

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv non e' installato. Installa uv da https://docs.astral.sh/uv/ e rilancia questo script."
}

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    throw "nvidia-smi non trovato. Installa o aggiorna i driver NVIDIA."
}

Write-Host "GPU rilevata:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

if (-not (Get-Command nvcc -ErrorAction SilentlyContinue)) {
    Write-Warning "CUDA Toolkit/nvcc non trovato. PyTorch puo' funzionare con wheel CUDA, ma alcuni tool potrebbero richiederlo."
}

$VenvPath = Join-Path (Get-Location) ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

Invoke-Native uv python install $PythonVersion

if (Test-Path $VenvPath) {
    $HasPip = $false
    if (Test-Path $PythonExe) {
        $PreviousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $PythonExe -m pip --version 1>$null 2>$null
        $PipExitCode = $LASTEXITCODE
        $ErrorActionPreference = $PreviousErrorActionPreference
        $HasPip = ($PipExitCode -eq 0)
    }

    if (-not $HasPip) {
        Write-Warning ".venv esistente senza pip rilevata. La ricreo con uv --seed."
        Remove-Item -Recurse -Force -LiteralPath $VenvPath
    }
}

if (-not (Test-Path $VenvPath)) {
    Invoke-Native uv venv --seed --python $PythonVersion .venv
}

if ($SkipInstall) {
    Write-Host "Virtualenv creata. Installazione pacchetti saltata."
    exit 0
}

Invoke-Native $PythonExe -m pip install --upgrade pip
Invoke-Native $PythonExe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
Invoke-Native $PythonExe -m pip install --editable .
Invoke-Native $PythonExe -m pip install "unsloth[windows] @ git+https://github.com/unslothai/unsloth.git"

Write-Host "Setup completato. Esegui: .\.venv\Scripts\Activate.ps1 ; python .\scripts\verify_gpu.py"
