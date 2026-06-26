# Worklog

This worklog records the technical, cultural, and operational decisions behind Adriano IA. It is not decorative documentation: it exists to make the project traceable, explain tradeoffs, and keep quality visible.

## 2026-06-26 - Project Foundation

### Context

The project starts with a clear goal: build an Italian/English bilingual model, with priority on Italian quality, starting from a Qwen 14B base and working locally on Windows 11 with an RTX 4060 Ti 16 GB GPU.

The cultural reference is Adriano Olivetti: industry as a civic project, technology as responsibility, product as a meeting point between engineering and humanism.

### Main Technical Decision

The project adopts a 4-bit QLoRA strategy on Qwen3-14B.

Rationale:

- full fine-tuning a 14B model is not realistic on 16 GB VRAM;
- QLoRA allows local, controlled, relatively affordable iteration;
- Unsloth reduces operational cost and simplifies training;
- LoRA adapters make versioning fast without duplicating the whole model.

Operational base:

- `Qwen/Qwen3-14B` as the official reference;
- `unsloth/Qwen3-14B-unsloth-bnb-4bit` as the practical training base.

### Clarification On Qwen3.6-14B

The initial request mentioned Qwen 3.6 14B. Verification showed no official `Qwen3.6-14B` release. The correct path is therefore:

- use Qwen3-14B as the local student;
- evaluate larger Qwen3.6 releases as teacher models, when available.

### Created Material

The foundation includes:

- QLoRA configuration;
- environment setup script;
- GPU verification script;
- training script;
- teacher distillation script;
- local chat script;
- merge/export script;
- minimal seed dataset;
- technical strategy document.

### Adriano Profile

The first model identity has been defined as:

- natural, precise, non-bureaucratic Italian;
- solid English;
- operational, non-promotional tone;
- ability to state when data is missing;
- attention to the quality of human work;
- rejection of generic answers.

### Next Step

Build a manual dataset of 300-800 excellent examples. Distillation should begin only after the model voice has been clearly established.

## 2026-06-26 - Bilingual Repository Pass

### Context

The project should not only produce a model that speaks Italian and English. The repository itself should communicate in both languages, so it can be read by Italian contributors and by international technical reviewers.

### Decision

Italian documentation remains the primary source, and dedicated English documents were added:

- worklog;
- manifesto;
- roadmap;
- bilingual README.

### Rationale

Italian remains central because it is the core quality target of the project. English is necessary for technical interoperability, collaboration, public review, and future model publication.

### Remaining Risk

Bilingual documentation must stay aligned. Important decisions should be recorded at least in the Italian diary and in the English worklog.

## 2026-06-26 - One-Click Windows Launcher

### Context

Manual Windows setup exposed a concrete issue: the virtual environment could be created without `pip`, causing later installation commands to fail without a clear stop.

### Decision

The project now includes a Windows double-click launcher that can run:

- full setup;
- GPU and package verification;
- training smoke test;
- local chat.

The `scripts/setup_env.ps1` checks were also hardened so native command failures stop the script properly.

### Rationale

The first-run experience should be direct. The user should be able to start Adriano without memorizing a PowerShell command sequence. When something fails, the failure point should be visible.

## 2026-06-26 - Data And Distillation Pipeline

### Context

The training smoke test is not enough to build Adriano. A model with a clear linguistic identity and strong Italian quality needs specific data: designed prompts, teacher-generated answers, quality filtering, an SFT dataset, and separate evaluation.

### Decision

The project now includes:

- a distillation prompt bank;
- a separate evaluation set;
- JSONL validation script;
- SFT dataset preparation script;
- training configuration for curated data;
- data preparation and training through the root launcher.

### Rationale

The model must not be Qwen with a different name. Adriano should be shaped through data that teaches Italian, method, tone, limits, and operational reasoning.

### Remaining Risk

The automatic filter only removes obvious failures. Real quality still requires human review and progressive dataset expansion.

## 2026-06-26 - 512k Context Plan

### Context

Adriano was requested to support a 512k-token context. This is a valid product ambition, but it is not realistic as a simple `max_seq_length` change in local training.

### Decision

The project now includes:

- long-context profiles for 32k, 128k, and the 512k target;
- a dedicated technical document;
- a KV cache estimation script;
- long-context memory estimation script.

### Rationale

Qwen3-14B must be handled carefully: 32k is the stable target, 128k is experimental with YaRN, and 512k requires different hardware/backend or external memory. The project should state this distinction clearly.

### Remaining Risk

The 512k target must be implemented through retrieval/memory architecture or a model with stronger native long-context support. It should not be promised as a local RTX 4060 Ti capability.

## 2026-06-26 - Italian Dataset Source Research

### Context

Adriano's quality depends on data. A search was started across Italian, university-linked, and free sources to understand what can support training, distillation, and evaluation.

### Decision

A dedicated Italian dataset source note was added, separating corpora, benchmarks, and instruction datasets.

### Rationale

Downloading large datasets is not enough. Sources must be classified by use, license, risk, and fit with the Adriano profile.

### Remaining Risk

Many Italian datasets are `NC`, translated, or designed for evaluation rather than training. Each source must be checked before use in the final model.

## 2026-06-26 - Clean Restart And Resumable Training

### Context

The first full execution exposed operational confusion: the distilled dataset was not materialized under `data/distilled`, the command window could close with little trace, and a new execution could mix old outputs with updated data.

### Decision

`TRAINA_TUTTO_ADRIANO.bat` now performs a clean restart when no active run marker exists: it removes only generated artifacts, recreates the local distilled dataset, prepares the final dataset, and starts training. If a run is interrupted, the local marker lets the next batch execution resume from checkpoints instead of starting over.

### Rationale

The project must be runnable by double click without manual command-line recovery. Critical steps must be explicit, repeatable, and traceable through a local log.

### Remaining Risk

The local distilled dataset still derives from available instruction datasets; external-teacher distillation requires credentials and an explicit teacher model choice.

## Decision Log

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-06-26 | 4-bit QLoRA instead of full fine-tuning | Realistic VRAM constraints |
| 2026-06-26 | Qwen3-14B as the 14B base | No official Qwen3.6-14B release found |
| 2026-06-26 | Distillation separated from training | Separate data generation, quality filtering, and SFT |
| 2026-06-26 | LoRA adapters as the initial format | Fast iteration and lower storage cost |
| 2026-06-26 | Bilingual Italian/English repository | Consistency with the model's bilingual identity |
| 2026-06-26 | Windows launcher | Reduce operational friction and make setup repeatable |
| 2026-06-26 | Distilled data pipeline | Make Adriano trainable on curated data, not only on seed examples |
| 2026-06-26 | 512k context as an architecture target | Avoid unrealistic local settings and plan long-context robustly |
| 2026-06-26 | Italian dataset source catalog | Separate corpora, benchmarks, and instruction data with license awareness |
| 2026-06-26 | Root launchers `TRAINA_TUTTO_ADRIANO.bat` and `CREA_MODELLO_USABILE_ADRIANO.bat` | Keep only two operational batch files: full training and model creation |
| 2026-06-26 | Clean training with automatic resume | Avoid mixed outputs and recover from command-window interruption |
| 2026-06-26 | Curated training set to 3 real epochs | Remove the 200-step smoke-test cap and actually train on the full dataset |
| 2026-06-26 | Packing enabled for curated training | Reduce waste on short examples and sharply lower epoch time |

## Worklog Standard

Each future entry should state:

- what was done;
- why it was done;
- which alternatives were rejected;
- which risks remain;
- how the result will be measured.
