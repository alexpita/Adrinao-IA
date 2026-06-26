from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
OUTPUT = ROOT / "data" / "curated" / "external_sft.jsonl"

SYSTEM_IT = (
    "Sei Adriano, un assistente bilingue italiano e inglese. "
    "Rispondi con precisione, concretezza, sobrietà e ottima qualità linguistica."
)


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def first_text(row: dict, keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def convert_camoscio() -> list[dict]:
    rows = []
    camoscio_dir = EXTERNAL / "camoscio"
    if not camoscio_dir.exists():
        print("SKIP camoscio: non trovato in data/external/camoscio")
        return rows

    for file_path in sorted(camoscio_dir.glob("*.jsonl")):
        for index, row in enumerate(iter_jsonl(file_path), start=1):
            instruction = first_text(row, ["instruction", "prompt", "question", "input"])
            extra_input = first_text(row, ["input", "context"])
            output = first_text(row, ["output", "response", "answer", "completion"])
            if not instruction or not output:
                continue
            if extra_input and extra_input != instruction:
                user = f"{instruction}\n\nContesto:\n{extra_input}"
            else:
                user = instruction
            rows.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_IT},
                        {"role": "user", "content": user},
                        {"role": "assistant", "content": output},
                    ],
                    "source": "external:camoscio",
                    "lang": "it",
                    "id": f"camoscio_{file_path.stem}_{index}",
                }
            )
    return rows


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    rows.extend(convert_camoscio())

    seen = set()
    deduped = []
    for row in rows:
        key = "\n".join(message["content"] for message in row["messages"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    with OUTPUT.open("w", encoding="utf-8") as handle:
        for row in deduped:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Scritto {OUTPUT} con {len(deduped)} esempi.")
    if not deduped:
        print("Nessun dataset esterno convertito. Il training userà seed/distillati se presenti.")


if __name__ == "__main__":
    main()

