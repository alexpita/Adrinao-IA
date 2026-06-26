# Dati Adriano

Formato preferito: JSONL chat, una conversazione per riga.

```json
{"messages":[{"role":"system","content":"Sei Adriano..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}],"source":"manual","lang":"it"}
```

Linee guida:

- Italiano eccellente, naturale, non tradotto letteralmente.
- Inglese solido, sobrio, tecnico quando serve.
- Niente risposte servili o slogan: Adriano deve essere concreto, civile, rigoroso.
- Tenere separati dati seed manuali, dati distillati e dati di valutazione.
- Preferire esempi lunghi e densi rispetto a grandi quantita' di esempi mediocri.

Pipeline:

- `data/prompts/adriano_distill_prompts.jsonl`: prompt da inviare al teacher.
- `data/distilled/teacher_adriano.jsonl`: risposte generate dal teacher, ignorate da git.
- `data/curated/adriano_sft.jsonl`: dataset SFT filtrato, ignorato da git.
- `data/eval/adriano_eval_prompts.jsonl`: prompt di valutazione, mai da usare nel training.
- `data/external/`: dataset esterni scaricati con `download_datasets.bat`, ignorati da git.

Comandi:

```powershell
.\adriano.bat validate-data
.\adriano.bat distill
.\adriano.bat curate
.\adriano.bat train-curated
```

Download fonti esterne:

```powershell
.\download_datasets.bat --list
.\download_datasets.bat
.\download_datasets.bat paisa_raw
```

I dataset esterni non entrano automaticamente nel training: vanno filtrati, ripuliti e convertiti.
