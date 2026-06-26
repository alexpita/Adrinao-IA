from __future__ import annotations

import argparse
from pathlib import Path


SYSTEM = (
    "Sei Adriano, un assistente bilingue italiano e inglese. "
    "Rispondi con precisione, sobrietà, concretezza e ottima qualità linguistica."
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gguf-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ggufs = sorted(args.gguf_dir.rglob("*.gguf"))
    if not ggufs:
        raise SystemExit(f"Nessun file .gguf trovato in {args.gguf_dir}")

    gguf_path = ggufs[0].resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(
            [
                f'FROM "{gguf_path}"',
                "",
                'PARAMETER temperature 0.6',
                'PARAMETER top_p 0.9',
                'PARAMETER num_ctx 32768',
                "",
                f'SYSTEM """{SYSTEM}"""',
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Modelfile Ollama scritto in {args.output}")
    print(f"GGUF: {gguf_path}")


if __name__ == "__main__":
    main()

