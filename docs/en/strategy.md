# Adriano IA Strategy

## Base Decision

The project should not chase an unofficial model name. For a 14B student model, the concrete base is:

- `Qwen/Qwen3-14B` as the official model;
- `unsloth/Qwen3-14B-unsloth-bnb-4bit` as the operational QLoRA base.

Reason: full fine-tuning a 14B model is not realistic on 16 GB VRAM. 4-bit QLoRA is the correct path for local iteration.

## Adriano Profile

Adriano should be:

- excellent in Italian, natural rather than translated;
- clear and technically solid in English;
- concrete: no slogans, no generic motivational tone;
- capable of reasoning about work, enterprise, technology, writing, product, and society;
- rigorous about uncertainty: when it does not know, it says so and explains how to verify.

## Roadmap

### Phase 0 - Smoke Test

Goal: verify that Windows, GPU, PyTorch, bitsandbytes, Unsloth, and training all run correctly.

- Dataset: `data/seed/adriano_seed.jsonl`.
- Training: 30 steps.
- Sequence length: 2048 tokens.
- Output: LoRA adapter in `outputs/adriano-qwen3-14b-lora`.

### Phase 1 - Small, Excellent Manual Dataset

Target: 300-800 examples, written or reviewed by hand.

Categories:

- Adriano identity and tone;
- technical IT/AI/software answers in Italian;
- professional rewriting in Italian and English;
- critical analysis of texts;
- long, structured explanations without excess formality;
- refusals and limits: firm but useful answers.

This phase defines the model's voice. It is not meant to teach everything.

### Phase 2 - Teacher Distillation

Initial target: 5k-20k filtered conversations.

Recommended teacher:

- a larger Qwen3.6 model, if available locally or through an endpoint;
- otherwise, a strong OpenAI-compatible model reachable through an API.

Rule: generate more data than you keep. Discard answers that are too short, generic, poorly translated, hallucinated, or off-tone.

### Phase 3 - Adriano SFT

Recommended training setup for RTX 4060 Ti 16 GB:

- 4-bit QLoRA;
- LoRA rank 16, alpha 16;
- batch 1, gradient accumulation 8;
- max sequence length 2048;
- learning rate 2e-4;
- 1-2 epochs on curated data.

Try 4096 tokens only after a stable 2048-token run.

### Phase 4 - Evaluation

Create a fixed evaluation set that is never used for training:

- 50 difficult Italian prompts;
- 30 English prompts;
- 20 bilingual, translation, or adaptation prompts;
- 20 trap prompts with missing data, vague requests, or false premises.

Evaluate:

- Italian quality;
- faithfulness to the request;
- concreteness;
- ability to say "I do not know";
- stability of the Adriano tone.

### Phase 5 - Export

Do not merge too early. Keep LoRA adapters while experimenting.

Only after a version passes evaluation:

- merge to 16-bit;
- optionally export GGUF `q4_k_m`;
- test with Ollama or llama.cpp.

## Operational Sources

- Official Qwen3-14B: https://huggingface.co/Qwen/Qwen3-14B
- Qwen3.6 release: https://github.com/QwenLM/Qwen3.6
- Qwen3 fine-tuning with Unsloth: https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune
- Unsloth Windows installation: https://docs.unsloth.ai/get-started/installing-+-updating/windows-installation
- PyTorch CUDA install: https://pytorch.org/get-started/locally/

