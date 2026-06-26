from __future__ import annotations

import argparse
import json
from pathlib import Path


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield line_number, json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: JSON non valido: {exc}") from exc


def is_chat_row(row: dict) -> bool:
    messages = row.get("messages")
    if not isinstance(messages, list) or not messages:
        return False
    return all(
        isinstance(message, dict)
        and message.get("role") in {"system", "user", "assistant"}
        and isinstance(message.get("content"), str)
        and message["content"].strip()
        for message in messages
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Crea un dataset distillato locale partendo dal dataset SFT esterno gia "
            "convertito. Serve quando non e' configurato un teacher remoto."
        )
    )
    parser.add_argument("--input", type=Path, default=Path("data/curated/external_sft.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/distilled/teacher_adriano.jsonl"))
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input mancante: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    rejected = 0
    seen = set()
    with args.output.open("w", encoding="utf-8") as handle:
        for line_number, row in iter_jsonl(args.input):
            if not isinstance(row, dict) or not is_chat_row(row):
                rejected += 1
                print(f"REJECT {args.input}:{line_number}: riga chat non valida")
                continue

            key = json.dumps(row.get("messages"), ensure_ascii=False, sort_keys=True)
            if key in seen:
                rejected += 1
                continue
            seen.add(key)

            source = row.get("source", f"external:{args.input.as_posix()}")
            distilled_row = {
                "messages": row["messages"],
                "source": f"local-distilled:{source}",
                "lang": row.get("lang", "mixed"),
                "id": row.get("id"),
            }
            handle.write(json.dumps(distilled_row, ensure_ascii=False) + "\n")
            written += 1

    if written == 0:
        raise RuntimeError(
            f"Nessun esempio scritto in {args.output}. Controllare il dataset sorgente: {args.input}"
        )

    print(f"Dataset distillato locale scritto: {args.output} ({written} esempi)")
    if rejected:
        print(f"Righe scartate: {rejected}")


if __name__ == "__main__":
    main()
