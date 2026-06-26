from __future__ import annotations

import argparse
from pathlib import Path

from unsloth import FastModel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--base-model", default="unsloth/Qwen3-14B-unsloth-bnb-4bit")
    parser.add_argument("--merged-output", type=Path, default=Path("outputs/adriano-merged"))
    parser.add_argument("--gguf-output", type=Path)
    parser.add_argument("--gguf-quant", default="q4_k_m")
    args = parser.parse_args()

    model, tokenizer = FastModel.from_pretrained(
        model_name=str(args.adapter),
        max_seq_length=4096,
        load_in_4bit=True,
        full_finetuning=False,
    )

    args.merged_output.parent.mkdir(parents=True, exist_ok=True)
    model.save_pretrained_merged(str(args.merged_output), tokenizer, save_method="merged_16bit")
    print(f"Merged model salvato in {args.merged_output}")

    if args.gguf_output:
        args.gguf_output.parent.mkdir(parents=True, exist_ok=True)
        model.save_pretrained_gguf(str(args.gguf_output), tokenizer, quantization_method=args.gguf_quant)
        print(f"GGUF salvato in {args.gguf_output}")


if __name__ == "__main__":
    main()

