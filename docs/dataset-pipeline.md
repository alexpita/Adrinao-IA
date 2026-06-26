# Pipeline Dati Adriano

Adriano non nasce dal training sul dataset seed. Il seed serve solo a verificare la pipeline. Il modello vero richiede dati curati.

## Flusso

```text
prompt bank -> teacher -> distillazione -> filtro qualità -> dataset SFT -> training -> valutazione
```

## 1. Prompt Bank

I prompt iniziali sono in:

```text
data/prompts/adriano_distill_prompts.jsonl
```

Ogni riga contiene:

- `id`;
- `lang`;
- `topic`;
- `prompt`.

Questi prompt non sono il dataset finale: sono domande inviate a un teacher più forte per generare risposte candidate.

## 2. Distillazione

La distillazione richiede un endpoint OpenAI-compatible:

La distillazione usa `scripts/distill_from_teacher.py` quando è configurato un teacher OpenAI-compatible.

Output:

```text
data/distilled/teacher_adriano.jsonl
```

## 3. Filtro E Curation

Le risposte distillate vanno filtrate. Il filtro automatico elimina solo errori evidenti: risposte troppo corte, ruoli sbagliati, duplicati, contenuto vuoto. Non sostituisce la revisione umana.

La preparazione del dataset è inclusa in `TRAINA_TUTTO_ADRIANO.bat`.

Output:

```text
data/curated/adriano_sft.jsonl
```

## 4. Training

Per usare il dataset curato:

```powershell
python .\scripts\train_qlora.py --config .\configs\adriano_qwen3_14b_curated.yaml
```

## 5. Valutazione

I prompt di valutazione sono in:

```text
data/eval/adriano_eval_prompts.jsonl
```

Non devono entrare nel training.

## Regola Di Qualità

Meglio 500 esempi eccellenti che 20.000 esempi mediocri. Adriano deve imparare italiano, metodo e tono; non accumulare rumore.
