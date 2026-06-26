# Adriano 512k Context Plan

## Decisione

512k token è un obiettivo di prodotto, non il prossimo parametro da mettere nel training locale.

Su RTX 4060 Ti 16 GB:

- training QLoRA realistico: 2048-4096 token;
- inference locale sensata: 32k come target stabile;
- 128k: sperimentale con YaRN e backend adatto;
- 512k: richiede architettura diversa, backend più grande o memoria/RAG.

## Stato Di Qwen3-14B

Le fonti ufficiali Qwen indicano:

- contesto nativo Qwen3: 32,768 token;
- long context con YaRN validato fino a 131,072 token per Qwen3;
- Qwen3-Coder dichiara capacità long-context superiori, fino a 1M con YaRN, ma è un modello/famiglia diversa.

Questo significa che forzare 512k su `Qwen3-14B` non è una scelta robusta per Adriano. Si può sperimentare, ma non va presentata come capacità affidabile.

## Perché 512k Non Sta Nella 4060 Ti

Il problema principale è il KV cache: ogni token in più occupa memoria durante l'inferenza. A 512k token, un 14B può richiedere decine o centinaia di GB solo per mantenere l'attenzione, a seconda di architettura, quantizzazione KV e backend.

Il training è ancora più costoso: memoria e tempo crescono rapidamente con la lunghezza di sequenza.

## Strategia Corretta Per Adriano

### Fase 1 - Stabilità Locale

Obiettivo:

- QLoRA a 2048 token;
- eventualmente 4096 token;
- dataset italiano/inglese curato;
- valutazione qualitativa.

Motivo: prima si costruisce Adriano come identità linguistica. Il contesto lungo non corregge un modello senza voce.

### Fase 2 - 32k Inference

Obiettivo:

- testare chat e documenti lunghi fino a 32k;
- costruire eval set long-context;
- misurare se Adriano resta coerente in italiano.

### Fase 3 - 128k YaRN

Obiettivo:

- profilo sperimentale con YaRN;
- backend come llama.cpp/vLLM/SGLang, se supportato;
- test controllati su documenti lunghi.

### Fase 4 - 512k Reale

Tre strade possibili:

1. Usare un modello con long-context nativo più adatto.
2. Usare backend remoto con hardware adeguato.
3. Costruire una memoria esterna: RAG, chunking, ranking, compression summaries, document map.

Per Adriano, la terza strada è probabilmente la più utile: 512k "utili" significa recuperare il contesto giusto, non buttare mezzo milione di token nel prompt.

## Regola Operativa

Non cambiare:

```yaml
max_seq_length: 524288
```

nei config di training locale.

Usare `scripts/estimate_context_memory.py` per stimare memoria e scegliere un profilo.

## Profili

Vedi:

```text
configs/long_context_profiles.yaml
```

## Fonti

- Qwen3-14B model card: https://huggingface.co/Qwen/Qwen3-14B
- Qwen3 GitHub: https://github.com/QwenLM/Qwen3
- Qwen3-Coder-30B-A3B-Instruct model card: https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
