# Adriano IA

**Adriano IA** Ã¨ un progetto per costruire un assistente bilingue italiano/inglese, con prioritÃ  alla qualitÃ  dell'italiano e a un tono concreto, sobrio, tecnico e civile.

Il nome rende omaggio ad **Adriano Olivetti**.

## Uso

Nella root ci sono solo due launcher principali:

```text
TRAINA_TUTTO_ADRIANO.bat
CREA_MODELLO_USABILE_ADRIANO.bat
```

## Training

Doppio click su:

```text
TRAINA_TUTTO_ADRIANO.bat
```

Fa tutto:

- setup ambiente Python se serve;
- verifica GPU;
- scarica dataset esterni in `data/external/`;
- converte i dataset esterni in SFT;
- prepara `data/curated/adriano_sft.jsonl`;
- avvia training QLoRA;
- salva l'adapter in `outputs/adriano-qwen3-14b-curated-lora`.

## Modello Usabile

Doppio click su:

```text
CREA_MODELLO_USABILE_ADRIANO.bat
```

Crea:

- modello merged in `outputs/adriano-merged`;
- GGUF in `outputs/adriano-gguf`;
- Modelfile Ollama in `outputs/ollama/Modelfile`.

## Struttura

```text
configs/                         Config training
data/seed/                       Seed dataset
data/prompts/                    Prompt per distillazione
data/eval/                       Prompt di valutazione
data/external/                   Dataset esterni scaricati, ignorati da git
data/curated/                    Dataset SFT generati, ignorati da git
scripts/                         Script usati dai due batch
outputs/                         Modelli e adapter generati, ignorati da git
docs/                            Documentazione tecnica
```

## Dataset

File versionati:

```text
data/seed/adriano_seed.jsonl
data/prompts/adriano_distill_prompts.jsonl
data/eval/adriano_eval_prompts.jsonl
```

File generati localmente:

```text
data/external/
data/curated/external_sft.jsonl
data/curated/adriano_sft.jsonl
data/distilled/teacher_adriano.jsonl
```

## Base Tecnica

- Base model: `unsloth/Qwen3-14B-unsloth-bnb-4bit`
- Metodo: QLoRA 4-bit
- GPU target: RTX 4060 Ti 16 GB
- Training config: `configs/adriano_qwen3_14b_curated.yaml`

## Documentazione

- [Strategia](STRATEGIA.md)
- [Pipeline dati](docs/dataset-pipeline.md)
- [Fonti dataset italiane](docs/dataset-sources-italia.md)
- [Piano contesto 512k](docs/long-context.md)
- [Diario lavori](docs/diario-lavori.md)

## Disclaimer

Questo progetto Ã¨ un omaggio culturale e tecnico ad Adriano Olivetti. Non Ã¨ affiliato alla famiglia Olivetti, ad aziende collegate o a soggetti titolari di marchi.
