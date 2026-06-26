from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import urllib.request
import warnings
from pathlib import Path


os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("datasets").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"


SOURCES = {
    "camoscio": {
        "kind": "huggingface_dataset",
        "dataset": "teelinsan/camoscio",
        "target": EXTERNAL / "camoscio",
        "note": "Instruction dataset italiano tradotto da Stanford Alpaca con ChatGPT. Usare con cautela.",
        "source_url": "https://huggingface.co/datasets/teelinsan/camoscio",
    },
    "ud_isdt": {
        "kind": "git",
        "repo": "https://github.com/UniversalDependencies/UD_Italian-ISDT.git",
        "target": EXTERNAL / "ud_italian_isdt",
        "note": "Treebank UD Italian ISDT. Licenza indicata dalla fonte: CC BY-NC-SA 3.0.",
        "source_url": "https://github.com/UniversalDependencies/UD_Italian-ISDT",
    },
    "ita_bench": {
        "kind": "git",
        "repo": "https://github.com/SapienzaNLP/ita-bench.git",
        "target": EXTERNAL / "ita_bench",
        "note": "Benchmark LLM italiani. Usare per valutazione, non training.",
        "source_url": "https://github.com/SapienzaNLP/ita-bench",
    },
    "paisa_lemmas": {
        "kind": "url",
        "url": "https://clarin.eurac.edu/repository/xmlui/bitstream/handle/20.500.12124/3/lemma-frequencies-paisa.txt.gz",
        "target": EXTERNAL / "paisa" / "lemma-frequencies-paisa.txt.gz",
        "note": "Frequenze lemma PAISÀ, piccolo file utile per analisi lessicale.",
        "source_url": "https://clarin.eurac.edu/repository/xmlui/handle/20.500.12124/3",
    },
    "paisa_raw": {
        "kind": "url",
        "url": "https://clarin.eurac.edu/repository/xmlui/bitstream/handle/20.500.12124/3/paisa.raw.utf8.gz",
        "target": EXTERNAL / "paisa" / "paisa.raw.utf8.gz",
        "note": "PAISÀ raw cleaned web texts, circa 522 MB compressi. Non scaricarlo se vuoi solo testare.",
        "source_url": "https://clarin.eurac.edu/repository/xmlui/handle/20.500.12124/3",
    },
}


def write_manifest(source_key: str, metadata: dict, target: Path) -> None:
    manifest_path = EXTERNAL / "manifest.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "id": source_key,
        "target": str(target.relative_to(ROOT)),
        "kind": metadata["kind"],
        "source_url": metadata.get("source_url"),
        "note": metadata.get("note"),
    }
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def download_url(url: str, target: Path, force: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        print(f"SKIP esiste già: {target}")
        return
    print(f"Download {url}")
    print(f"-> {target}")
    urllib.request.urlretrieve(url, target)


def download_git(repo: str, target: Path, force: bool) -> None:
    if target.exists() and force:
        shutil.rmtree(target)
    if target.exists():
        print(f"UPDATE {target}")
        run(["git", "-C", str(target), "pull", "--ff-only"])
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", repo, str(target)])


def download_hf_dataset(dataset_name: str, target: Path, force: bool) -> None:
    from datasets import load_dataset
    from datasets.utils.logging import disable_progress_bar

    disable_progress_bar()

    if target.exists() and force:
        shutil.rmtree(target)
    if target.exists():
        print(f"SKIP esiste già: {target}")
        return
    target.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(dataset_name)
    for split_name, split in dataset.items():
        split.to_json(target / f"{split_name}.jsonl", force_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "sources",
        nargs="*",
        default=["camoscio", "ud_isdt", "ita_bench", "paisa_lemmas"],
        help=f"Sorgenti: {', '.join(SOURCES)}. Default: camoscio ud_isdt ita_bench paisa_lemmas",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for key, metadata in SOURCES.items():
            print(f"{key}: {metadata['note']}")
        return

    EXTERNAL.mkdir(parents=True, exist_ok=True)
    for source_key in args.sources:
        if source_key not in SOURCES:
            raise SystemExit(f"Sorgente sconosciuta: {source_key}. Usa --list.")
        metadata = SOURCES[source_key]
        target = metadata["target"]
        print(f"\n== {source_key} ==")
        if metadata["kind"] == "url":
            download_url(metadata["url"], target, args.force)
        elif metadata["kind"] == "git":
            download_git(metadata["repo"], target, args.force)
        elif metadata["kind"] == "huggingface_dataset":
            download_hf_dataset(metadata["dataset"], target, args.force)
        else:
            raise SystemExit(f"Tipo sorgente non gestito: {metadata['kind']}")
        write_manifest(source_key, metadata, target)

    print(f"\nDataset esterni in: {EXTERNAL}")
    print("Nota: questi dati NON sono automaticamente usati per training. Vanno filtrati/convertiti.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
    except KeyboardInterrupt:
        sys.exit(130)
