from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_ROLES = {"system", "user", "assistant"}


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield line_number, json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: JSON non valido: {exc}") from exc


def validate_prompt_row(path: Path, line_number: int, row: dict) -> None:
    for key in ["id", "prompt"]:
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"{path}:{line_number}: campo {key!r} mancante o vuoto.")
    if "messages" in row:
        validate_chat_row(path, line_number, row)


def validate_chat_row(path: Path, line_number: int, row: dict) -> None:
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError(f"{path}:{line_number}: campo 'messages' assente o troppo corto.")

    for index, message in enumerate(messages):
        role = message.get("role")
        content = message.get("content")
        if role not in VALID_ROLES:
            raise ValueError(f"{path}:{line_number}: ruolo non valido in messages[{index}]: {role!r}.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"{path}:{line_number}: content vuoto in messages[{index}].")

    if messages[-1]["role"] != "assistant":
        raise ValueError(f"{path}:{line_number}: l'ultimo messaggio deve essere assistant.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--kind", choices=["prompt", "chat"], default="chat")
    args = parser.parse_args()

    total = 0
    for path in args.files:
        if not path.exists():
            raise FileNotFoundError(path)
        count = 0
        for line_number, row in iter_jsonl(path):
            if args.kind == "prompt":
                validate_prompt_row(path, line_number, row)
            else:
                validate_chat_row(path, line_number, row)
            count += 1
        print(f"OK {path}: {count} righe")
        total += count

    print(f"Validazione completata: {total} righe totali")


if __name__ == "__main__":
    main()
