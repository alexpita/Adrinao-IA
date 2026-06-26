# Roadmap

## Phase 0 - Foundation

Status: in progress.

- Create repository structure.
- Define the QLoRA strategy.
- Prepare the Windows environment.
- Verify GPU and dependencies.
- Run a training smoke test.

## Phase 1 - Adriano Voice

Goal: 300-800 high-quality manual examples.

Dataset areas:

- model identity;
- professional writing in Italian;
- technical explanations;
- text revision;
- critical reasoning;
- bilingual responses;
- uncertainty handling.

Success criteria:

- Adriano answers in Italian without sounding translated;
- the tone is recognizable but not theatrical;
- responses are useful on the first pass.

## Phase 2 - Distillation

Goal: 5k-20k filtered conversations.

Process:

- generate controlled prompts;
- use a larger teacher;
- filter weak outputs;
- balance Italian and English;
- keep the evaluation set separate.

## Phase 3 - Training

Goal: first consistent Adriano adapter.

Initial parameters:

- LoRA rank 16;
- LoRA alpha 16;
- sequence length 2048 tokens;
- batch size 1;
- gradient accumulation 8;
- learning rate 2e-4.

## Phase 4 - Evaluation

Goal: evaluate Adriano with fixed prompts.

Qualitative metrics:

- Italian quality;
- concreteness;
- faithfulness;
- reasoning;
- ability to correct false premises;
- bilingual behavior.

## Phase 5 - Local Release

Goal: usable local version.

Outputs:

- LoRA adapter;
- merged model;
- optional GGUF;
- model card;
- usage examples;
- changelog.

