from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from openai import OpenAI
from rich.progress import track


DEFAULT_SYSTEM = (
    "Sei Adriano, un assistente bilingue italiano e inglese ispirato al rigore civile di Adriano Olivetti. "
    "Rispondi con chiarezza, concretezza e cura linguistica. Evita slogan, enfasi inutile e traduzioni letterali."
)


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"JSON non valido in {path}:{line_number}") from exc


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    for row in iter_jsonl(path):
        row_id = row.get("id")
        if isinstance(row_id, str) and row_id:
            ids.add(row_id)
    return ids


def normalized_messages(row: dict) -> list[dict]:
    messages = row.get("messages")
    if not messages:
        prompt = row.get("prompt") or row.get("question")
        if not prompt:
            raise ValueError("Ogni riga deve avere messages oppure prompt/question.")
        messages = [{"role": "system", "content": DEFAULT_SYSTEM}, {"role": "user", "content": prompt}]
    if messages[0]["role"] != "system":
        messages = [{"role": "system", "content": DEFAULT_SYSTEM}, *messages]
    return messages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temperature", type=float, default=0.45)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    base_url = os.environ.get("TEACHER_BASE_URL")
    api_key = os.environ.get("TEACHER_API_KEY")
    model = os.environ.get("TEACHER_MODEL")
    if not base_url or not api_key or not model:
        raise SystemExit("Imposta TEACHER_BASE_URL, TEACHER_API_KEY e TEACHER_MODEL.")

    client = OpenAI(base_url=base_url, api_key=api_key)
    rows = list(iter_jsonl(args.input))
    if args.limit:
        rows = rows[: args.limit]
    seen_ids = set() if args.overwrite else existing_ids(args.output)
    if args.overwrite and args.output.exists():
        args.output.unlink()
    written = 0
    skipped = 0

    for row in track(rows, description="Distilling"):
        row_id = row.get("id")
        if isinstance(row_id, str) and row_id in seen_ids:
            skipped += 1
            continue
        messages = normalized_messages(row)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        answer = completion.choices[0].message.content or ""
        if len(answer.strip()) < 80:
            continue

        distilled = {
            "messages": [*messages, {"role": "assistant", "content": answer.strip()}],
            "source": f"distilled:{model}",
            "lang": row.get("lang", "mixed"),
            "id": row.get("id"),
        }
        write_jsonl(args.output, [distilled])
        written += 1
        if isinstance(row_id, str):
            seen_ids.add(row_id)
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Scritte {written} conversazioni in {args.output}")
    if skipped:
        print(f"Saltate {skipped} conversazioni gia' presenti")


if __name__ == "__main__":
    main()
