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


def normalize_messages(row: dict) -> list[dict]:
    messages = row.get("messages")
    if not isinstance(messages, list):
        raise ValueError("Campo messages mancante.")
    cleaned = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role not in VALID_ROLES:
            raise ValueError(f"Ruolo non valido: {role!r}")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Content vuoto.")
        cleaned.append({"role": role, "content": content.strip()})
    if cleaned[-1]["role"] != "assistant":
        raise ValueError("L'ultimo messaggio deve essere assistant.")
    return cleaned


def quality_score(messages: list[dict]) -> tuple[bool, str]:
    assistant_text = messages[-1]["content"]
    lowered = assistant_text.lower()
    if len(assistant_text) < 160:
        return False, "assistant_too_short"
    if "as an ai language model" in lowered or "come modello linguistico" in lowered:
        return False, "generic_ai_disclaimer"
    if lowered.count("!") >= 4:
        return False, "too_promotional"
    if len(set(assistant_text.split())) < 35:
        return False, "low_lexical_variety"
    return True, "ok"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/curated/adriano_sft.jsonl"))
    parser.add_argument("--report", type=Path, default=Path("data/curated/adriano_sft_report.json"))
    parser.add_argument("--include-short-seed", action="store_true")
    args = parser.parse_args()

    rows = []
    seen = set()
    rejected: dict[str, int] = {}

    for path in args.inputs:
        if not path.exists():
            print(f"SKIP missing: {path}")
            continue
        for line_number, row in iter_jsonl(path):
            try:
                messages = normalize_messages(row)
                ok, reason = quality_score(messages)
                if not ok and not args.include_short_seed:
                    rejected[reason] = rejected.get(reason, 0) + 1
                    continue
                key = "\n".join(message["content"] for message in messages)
                if key in seen:
                    rejected["duplicate"] = rejected.get("duplicate", 0) + 1
                    continue
                seen.add(key)
                rows.append(
                    {
                        "messages": messages,
                        "source": row.get("source", f"prepared:{path.as_posix()}"),
                        "lang": row.get("lang", "mixed"),
                        "id": row.get("id"),
                    }
                )
            except ValueError as exc:
                rejected[f"invalid:{exc}"] = rejected.get(f"invalid:{exc}", 0) + 1
                print(f"REJECT {path}:{line_number}: {exc}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "output": str(args.output),
        "accepted": len(rows),
        "rejected": rejected,
        "inputs": [str(path) for path in args.inputs],
    }
    with args.report.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print(f"Dataset SFT scritto: {args.output} ({len(rows)} esempi)")
    print(f"Report scritto: {args.report}")


if __name__ == "__main__":
    main()
