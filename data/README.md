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
- `data/external/`: dataset esterni scaricati da `TRAINA_TUTTO_ADRIANO.bat`, ignorati da git.

Il training tutto compreso viene avviato dal batch root `TRAINA_TUTTO_ADRIANO.bat`.
