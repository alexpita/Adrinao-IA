from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelShape:
    layers: int = 40
    kv_heads: int = 8
    head_dim: int = 128


DTYPE_BYTES = {
    "fp16": 2.0,
    "bf16": 2.0,
    "fp8": 1.0,
    "q8": 1.0,
    "q4": 0.5,
}


def kv_cache_gb(tokens: int, shape: ModelShape, dtype: str) -> float:
    bytes_per_value = DTYPE_BYTES[dtype]
    # K and V cache per token across all layers.
    total_bytes = tokens * 2 * shape.layers * shape.kv_heads * shape.head_dim * bytes_per_value
    return total_bytes / 1024**3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", type=int, default=524288)
    parser.add_argument("--layers", type=int, default=40)
    parser.add_argument("--kv-heads", type=int, default=8)
    parser.add_argument("--head-dim", type=int, default=128)
    args = parser.parse_args()

    shape = ModelShape(layers=args.layers, kv_heads=args.kv_heads, head_dim=args.head_dim)
    print("Adriano long-context KV cache estimate")
    print(f"tokens: {args.tokens:,}")
    print(f"shape: layers={shape.layers}, kv_heads={shape.kv_heads}, head_dim={shape.head_dim}")
    print()

    for dtype in ["fp16", "fp8", "q8", "q4"]:
        print(f"{dtype:>4}: {kv_cache_gb(args.tokens, shape, dtype):8.2f} GB KV cache")

    print()
    print("Nota: questa stima riguarda solo il KV cache. Devi aggiungere pesi modello, runtime, attivazioni e overhead backend.")
    print("Su RTX 4060 Ti 16 GB, 512k token non e' un target locale realistico per Qwen3-14B.")


if __name__ == "__main__":
    main()

