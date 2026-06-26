# Adriano 512k Context Plan

## Decision

512k tokens is a product target, not the next parameter to put into local training.

On an RTX 4060 Ti 16 GB:

- realistic QLoRA training: 2048-4096 tokens;
- reasonable local inference: 32k as the stable target;
- 128k: experimental with YaRN and the right backend;
- 512k: requires a different architecture, larger backend, or external memory/RAG.

## Qwen3-14B Status

Official Qwen sources indicate:

- native Qwen3 context: 32,768 tokens;
- YaRN long-context validation up to 131,072 tokens for Qwen3;
- Qwen3-Coder reports stronger long-context capabilities, up to 1M with YaRN, but it is a different model family.

This means forcing 512k on `Qwen3-14B` is not a robust Adriano capability. It can be experimented with, but it should not be presented as reliable.

## Why 512k Does Not Fit A 4060 Ti

The main issue is KV cache: each additional token consumes memory during inference. At 512k tokens, a 14B model can require tens or hundreds of GB just to maintain attention, depending on architecture, KV quantization, and backend.

Training is even more expensive: memory and time grow rapidly with sequence length.

## Correct Strategy For Adriano

### Phase 1 - Local Stability

Goal:

- QLoRA at 2048 tokens;
- optionally 4096 tokens;
- curated Italian/English dataset;
- qualitative evaluation.

Reason: first build Adriano's linguistic identity. Long context does not fix a model without a voice.

### Phase 2 - 32k Inference

Goal:

- test chat and long documents up to 32k;
- build a long-context evaluation set;
- measure whether Adriano remains coherent in Italian.

### Phase 3 - 128k YaRN

Goal:

- experimental YaRN profile;
- backend such as llama.cpp/vLLM/SGLang, if supported;
- controlled tests on long documents.

### Phase 4 - Real 512k

Three possible paths:

1. Use a model with stronger native long-context support.
2. Use a remote backend with adequate hardware.
3. Build external memory: RAG, chunking, ranking, compression summaries, document maps.

For Adriano, the third path is likely the most useful one: useful 512k context means retrieving the right context, not dumping half a million tokens into the prompt.

## Operational Rule

Do not set:

```yaml
max_seq_length: 524288
```

in local training configs.

Use instead:

```powershell
.\adriano.bat context-plan
```

to estimate memory and choose a profile.

## Profiles

See:

```text
configs/long_context_profiles.yaml
```

## Sources

- Qwen3-14B model card: https://huggingface.co/Qwen/Qwen3-14B
- Qwen3 GitHub: https://github.com/QwenLM/Qwen3
- Qwen3-Coder-30B-A3B-Instruct model card: https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
