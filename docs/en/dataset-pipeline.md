# Adriano Data Pipeline

Adriano does not come from training on the seed dataset. The seed dataset only validates the pipeline. The real model requires curated data.

## Flow

```text
prompt bank -> teacher -> distillation -> quality filtering -> SFT dataset -> training -> evaluation
```

## 1. Prompt Bank

Initial prompts live in:

```text
data/prompts/adriano_distill_prompts.jsonl
```

Each line contains:

- `id`;
- `lang`;
- `topic`;
- `prompt`.

These prompts are not the final dataset. They are questions sent to a stronger teacher to generate candidate answers.

## 2. Distillation

Distillation requires an OpenAI-compatible endpoint:

Distillation uses `scripts/distill_from_teacher.py` when an OpenAI-compatible teacher is configured.

Output:

```text
data/distilled/teacher_adriano.jsonl
```

## 3. Filtering And Curation

Distilled answers must be filtered. The automatic filter removes only obvious failures: answers that are too short, malformed roles, duplicates, or empty content. It does not replace human review.

Dataset preparation is included in `TRAINA_TUTTO_ADRIANO.bat`.

Output:

```text
data/curated/adriano_sft.jsonl
```

## 4. Training

To train on the curated dataset:

```powershell
python .\scripts\train_qlora.py --config .\configs\adriano_qwen3_14b_curated.yaml
```

## 5. Evaluation

Evaluation prompts live in:

```text
data/eval/adriano_eval_prompts.jsonl
```

They must not be used for training.

## Quality Rule

Five hundred excellent examples are better than twenty thousand mediocre ones. Adriano must learn Italian, method, and tone; it must not accumulate noise.
