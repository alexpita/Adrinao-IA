# Adriano IA

**Italiano** | [English](#english)

## Italiano

**Adriano IA** è un progetto di ricerca e costruzione applicata per creare un assistente bilingue italiano/inglese, ottimizzato per la qualità della lingua italiana e per un modo di ragionare concreto, civile, industriale.

Il nome rende omaggio ad **Adriano Olivetti**: non come citazione estetica, ma come direzione progettuale. Tecnologia utile, cultura tecnica, responsabilità sociale, attenzione al lavoro umano.

> Obiettivo: costruire un modello locale, raffinato e distillato, capace di parlare italiano con naturalezza e rigore, senza perdere solidità tecnica in inglese.

### Stato Del Progetto

Repository inizializzato con:

- pipeline QLoRA per Qwen 14B;
- configurazione Windows 11 + RTX 4060 Ti 16 GB;
- seed dataset bilingue;
- script di distillazione da teacher OpenAI-compatible;
- chat locale per testare l'adapter;
- strategia tecnica, diario lavori, manifesto e roadmap.

Base operativa consigliata:

- modello ufficiale: `Qwen/Qwen3-14B`;
- base training 4-bit: `unsloth/Qwen3-14B-unsloth-bnb-4bit`;
- tecnica: QLoRA 4-bit, adapter LoRA, distillazione progressiva.

Nota importante: non risulta disponibile un `Qwen3.6-14B` ufficiale. Per restare sulla taglia 14B la scelta solida è Qwen3-14B; Qwen3.6 va valutato su taglie diverse o come teacher.

### Identità Del Modello

Adriano deve essere:

- eccellente in italiano, non semplicemente tradotto dall'inglese;
- competente in inglese tecnico e operativo;
- sobrio, preciso, utile;
- capace di spiegare, scrivere, progettare e criticare;
- trasparente quando mancano dati o certezze;
- orientato alla dignità del lavoro e alla qualità del prodotto.

Adriano non deve diventare un personaggio teatrale. Deve avere una voce riconoscibile perché ragiona bene, non perché recita uno stile.

### Documentazione

- [Strategia tecnica](STRATEGIA.md)
- [Technical strategy EN](docs/en/strategy.md)
- [Pipeline dati](docs/dataset-pipeline.md)
- [Data pipeline EN](docs/en/dataset-pipeline.md)
- [Fonti dataset italiane](docs/dataset-sources-italia.md)
- [Piano contesto 512k](docs/long-context.md)
- [512k context plan EN](docs/en/long-context.md)
- [Diario dei lavori](docs/diario-lavori.md)
- [Manifesto](docs/manifesto.md)
- [Roadmap](docs/roadmap.md)
- [Worklog](docs/en/worklog.md)
- [Manifesto EN](docs/en/manifesto.md)
- [Roadmap EN](docs/en/roadmap.md)

### Struttura

```text
adriano.bat                       Launcher Windows one-click
configs/
  adriano_qwen3_14b_qlora.yaml   Configurazione training QLoRA
data/
  seed/                          Dataset manuale iniziale
  distilled/                     Output della distillazione
  eval/                          Set di valutazione da costruire
docs/
  diario-lavori.md               Diario professionale in italiano
  manifesto.md                   Principi in italiano
  roadmap.md                     Roadmap in italiano
  en/                            Documentazione inglese
scripts/
  setup_env.ps1                  Setup ambiente Windows
  verify_gpu.py                  Verifica GPU e librerie
  train_qlora.py                 Training LoRA
  distill_from_teacher.py        Distillazione da teacher
  chat_adriano.py                 Chat locale
  merge_or_export.py             Merge/export modello
STRATEGIA.md                     Piano tecnico completo
```

### Setup Windows

Requisiti:

- Windows 11;
- GPU NVIDIA con almeno 16 GB VRAM;
- driver NVIDIA aggiornati;
- `git`;
- `uv`.

Avvio rapido:

```bat
adriano.bat
```

Training diretto dalla root:

```bat
train_adriano.bat
```

Smoke test veloce:

```bat
train_smoke.bat
```

Comandi disponibili:

```bat
adriano.bat setup
adriano.bat verify
adriano.bat validate-data
adriano.bat context-plan
adriano.bat distill
adriano.bat curate
adriano.bat train
adriano.bat train-curated
adriano.bat chat
```

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_env.ps1
```

Verifica:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\verify_gpu.py
```

### Primo Training

Il primo run è uno smoke test: serve a verificare pipeline e memoria, non a produrre il modello finale.

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\train_qlora.py --config .\configs\adriano_qwen3_14b_qlora.yaml
```

Output previsto:

```text
outputs/adriano-qwen3-14b-lora
```

### Dataset E Distillazione

Il seed dataset non basta per creare Adriano. Serve una pipeline dati:

```text
prompt bank -> teacher -> distillazione -> filtro qualità -> dataset SFT -> training -> valutazione
```

Comandi:

```bat
adriano.bat validate-data
adriano.bat distill
adriano.bat curate
adriano.bat train-curated
```

Documentazione:

- [Pipeline dati](docs/dataset-pipeline.md)
- prompt bank: `data/prompts/adriano_distill_prompts.jsonl`
- eval set: `data/eval/adriano_eval_prompts.jsonl`
- dataset curato generato: `data/curated/adriano_sft.jsonl`

### Distillazione

Adriano va costruito con dati curati. Il seed manuale definisce il tono; la distillazione produce volume; il filtro umano preserva qualità.

```powershell
$env:TEACHER_BASE_URL="http://localhost:8000/v1"
$env:TEACHER_API_KEY="local"
$env:TEACHER_MODEL="qwen3.6-27b-instruct"
python .\scripts\distill_from_teacher.py --input .\data\distill_prompts.jsonl --output .\data\distilled\teacher_adriano.jsonl
```

### Chat Locale

```powershell
python .\scripts\chat_adriano.py --adapter .\outputs\adriano-qwen3-14b-lora
```

### Principio Guida

Adriano IA non nasce per imitare una persona. Nasce per portare in un modello linguistico una certa idea di tecnologia: elegante perché utile, potente perché comprensibile, moderna perché umana.

### Disclaimer

Questo progetto è un omaggio culturale e tecnico ad Adriano Olivetti. Non è affiliato alla famiglia Olivetti, ad aziende collegate o a soggetti titolari di marchi.

---

## English

**Adriano IA** is a research and applied engineering project for building an Italian/English bilingual assistant, optimized for high-quality Italian and for a concrete, civic, industrial way of reasoning.

The name pays tribute to **Adriano Olivetti**: not as decoration, but as a design direction. Useful technology, technical culture, social responsibility, and respect for human work.

> Goal: build a local, refined, distilled model that speaks Italian naturally and rigorously while preserving strong technical English.

### Project Status

The repository currently includes:

- a QLoRA pipeline for a Qwen 14B base model;
- Windows 11 + RTX 4060 Ti 16 GB configuration;
- a bilingual seed dataset;
- teacher distillation scripts through an OpenAI-compatible endpoint;
- local chat testing for LoRA adapters;
- technical strategy, worklog, manifesto, and roadmap.

Recommended operational base:

- official model: `Qwen/Qwen3-14B`;
- 4-bit training base: `unsloth/Qwen3-14B-unsloth-bnb-4bit`;
- method: 4-bit QLoRA, LoRA adapters, progressive distillation.

Important note: an official `Qwen3.6-14B` release does not appear to be available. For a 14B student, Qwen3-14B is the solid choice; Qwen3.6 should be evaluated in other sizes or as a teacher.

### Model Identity

Adriano should be:

- excellent in Italian, not merely translated from English;
- competent in technical and operational English;
- sober, precise, useful;
- able to explain, write, design, and critique;
- transparent when data or certainty is missing;
- oriented toward the dignity of work and product quality.

Adriano should not become a theatrical character. Its voice should be recognizable because it reasons well, not because it performs a style.

### Documentation

- [Technical strategy IT](STRATEGIA.md)
- [Technical strategy EN](docs/en/strategy.md)
- [Data pipeline IT](docs/dataset-pipeline.md)
- [Data pipeline EN](docs/en/dataset-pipeline.md)
- [Italian dataset sources](docs/dataset-sources-italia.md)
- [512k context plan IT](docs/long-context.md)
- [512k context plan EN](docs/en/long-context.md)
- [Italian worklog](docs/diario-lavori.md)
- [Italian manifesto](docs/manifesto.md)
- [Italian roadmap](docs/roadmap.md)
- [English worklog](docs/en/worklog.md)
- [English manifesto](docs/en/manifesto.md)
- [English roadmap](docs/en/roadmap.md)

### Windows Setup

Requirements:

- Windows 11;
- NVIDIA GPU with at least 16 GB VRAM;
- updated NVIDIA drivers;
- `git`;
- `uv`.

Quick start:

```bat
adriano.bat
```

Root-level training:

```bat
train_adriano.bat
```

Quick smoke test:

```bat
train_smoke.bat
```

Available commands:

```bat
adriano.bat setup
adriano.bat verify
adriano.bat validate-data
adriano.bat context-plan
adriano.bat distill
adriano.bat curate
adriano.bat train
adriano.bat train-curated
adriano.bat chat
```

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_env.ps1
```

Verification:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\verify_gpu.py
```

### First Training Run

The first run is a smoke test: it validates the pipeline and memory behavior, not the final model quality.

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\train_qlora.py --config .\configs\adriano_qwen3_14b_qlora.yaml
```

Expected output:

```text
outputs/adriano-qwen3-14b-lora
```

### Dataset And Distillation

The seed dataset is not enough to create Adriano. The real pipeline is:

```text
prompt bank -> teacher -> distillation -> quality filtering -> SFT dataset -> training -> evaluation
```

Commands:

```bat
adriano.bat validate-data
adriano.bat distill
adriano.bat curate
adriano.bat train-curated
```

Documentation:

- [Data pipeline](docs/dataset-pipeline.md)
- prompt bank: `data/prompts/adriano_distill_prompts.jsonl`
- eval set: `data/eval/adriano_eval_prompts.jsonl`
- generated curated dataset: `data/curated/adriano_sft.jsonl`

### Distillation

Adriano should be built from curated data. Manual seed examples define the voice; distillation adds scale; human filtering preserves quality.

```powershell
$env:TEACHER_BASE_URL="http://localhost:8000/v1"
$env:TEACHER_API_KEY="local"
$env:TEACHER_MODEL="qwen3.6-27b-instruct"
python .\scripts\distill_from_teacher.py --input .\data\distill_prompts.jsonl --output .\data\distilled\teacher_adriano.jsonl
```

### Local Chat

```powershell
python .\scripts\chat_adriano.py --adapter .\outputs\adriano-qwen3-14b-lora
```

### Guiding Principle

Adriano IA is not meant to imitate a person. It is meant to bring a specific idea of technology into a language model: elegant because useful, powerful because understandable, modern because human.

### Disclaimer

This project is a cultural and technical tribute to Adriano Olivetti. It is not affiliated with the Olivetti family, related companies, or trademark holders.
