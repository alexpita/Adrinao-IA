# Strategia Adriano

## Decisione di base

Non conviene inseguire un nome modello non ufficiale. Per una variante 14B oggi la base concreta e':

- `Qwen/Qwen3-14B` come modello ufficiale.
- `unsloth/Qwen3-14B-unsloth-bnb-4bit` come base operativa per QLoRA.

Motivo: su 16 GB VRAM un full fine-tune 14B non e' realistico. QLoRA 4-bit e' la strada corretta per iterare in locale.

## Profilo Adriano

Adriano deve essere:

- Italiano di livello alto, naturale, non burocratico.
- Inglese tecnico e chiaro.
- Concreto: niente slogan, niente tono motivazionale generico.
- Capace di ragionare su lavoro, impresa, tecnologia, scrittura, prodotto, societa'.
- Rigoroso sulle incertezze: se non sa, lo dice e propone come verificare.

## Roadmap

## Pipeline Dati

Il training sul solo seed dataset non produce Adriano. Serve una catena dati completa:

```text
prompt bank -> teacher -> distillazione -> filtro qualità -> dataset SFT -> training -> valutazione
```

File principali:

- `data/prompts/adriano_distill_prompts.jsonl`: prompt da inviare al teacher;
- `data/distilled/teacher_adriano.jsonl`: risposte generate dal teacher;
- `data/curated/adriano_sft.jsonl`: dataset SFT filtrato;
- `data/eval/adriano_eval_prompts.jsonl`: prompt di valutazione esclusi dal training.

Comandi:

```powershell
.\adriano.bat validate-data
.\adriano.bat distill
.\adriano.bat curate
.\adriano.bat train-curated
```

### Fase 0 - Smoke test

Obiettivo: verificare che Windows, GPU, PyTorch, bitsandbytes, Unsloth e training partano.

- Dataset: `data/seed/adriano_seed.jsonl`.
- Training: 30 step.
- Sequenza: 2048 token.
- Output: adapter LoRA in `outputs/adriano-qwen3-14b-lora`.

### Fase 1 - Dataset manuale piccolo ma eccellente

Target: 300-800 esempi, scritti o rivisti a mano.

Categorie:

- Identita' e tono Adriano.
- Risposte tecniche IT/AI/software in italiano.
- Riscrittura professionale italiano/inglese.
- Analisi critica di testi.
- Spiegazioni lunghe, strutturate, senza eccesso di formalismo.
- Rifiuti e limiti: risposte ferme ma utili.

Questa fase serve a definire lo stile, non a insegnare tutto.

### Fase 2 - Distillazione dal teacher

Target iniziale: 5k-20k conversazioni filtrate.

Teacher consigliato:

- Qwen3.6 piu' grande, se disponibile localmente o via endpoint.
- In alternativa un modello forte OpenAI-compatible raggiungibile da API.

Regola: generare piu' dati di quanti se ne tengono. Scartare risposte troppo corte, generiche, tradotte male, allucinate o fuori tono.

### Fase 3 - SFT Adriano

Training consigliato su 4060 Ti 16GB:

- 4-bit QLoRA.
- LoRA rank 16, alpha 16.
- Batch 1, gradient accumulation 8.
- Max sequence length 2048.
- Learning rate 2e-4.
- 1-2 epoche sui dati curati.

Se la VRAM lo permette, provare 4096 token solo dopo un run stabile a 2048.

### Fase 4 - Valutazione

Creare un set fisso non usato in training:

- 50 prompt italiani difficili.
- 30 prompt inglesi.
- 20 prompt bilingui/traduzione/adattamento.
- 20 prompt con trappole: dati mancanti, richieste vaghe, premesse false.

Valutare:

- Qualita' italiana.
- Fedelta' alla domanda.
- Concretezza.
- Capacita' di dire "non so".
- Stabilita' del tono Adriano.

### Fase 5 - Export

Non mergiare subito. Tenere gli adapter LoRA finche' si sperimenta.

Solo quando una versione supera la valutazione:

- merge 16-bit;
- eventuale GGUF `q4_k_m`;
- test con Ollama/llama.cpp.

## Fonti operative

- Qwen3-14B ufficiale: https://huggingface.co/Qwen/Qwen3-14B
- Release Qwen3.6: https://github.com/QwenLM/Qwen3.6
- Fine-tuning Qwen3 con Unsloth: https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune
- Installazione Unsloth Windows: https://docs.unsloth.ai/get-started/installing-+-updating/windows-installation
- PyTorch install CUDA: https://pytorch.org/get-started/locally/
