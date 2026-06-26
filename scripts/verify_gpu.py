from __future__ import annotations

import importlib.util

import torch
from rich.console import Console


console = Console()


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> None:
    console.print("[bold]Adriano GPU check[/bold]")
    console.print(f"torch: {torch.__version__}")
    console.print(f"cuda available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        console.print(f"gpu: {props.name}")
        console.print(f"vram: {props.total_memory / 1024**3:.2f} GB")
        console.print(f"bf16 supported: {torch.cuda.is_bf16_supported()}")

    for package in ["unsloth", "transformers", "datasets", "trl", "peft", "bitsandbytes"]:
        console.print(f"{package}: {'ok' if package_available(package) else 'missing'}")


if __name__ == "__main__":
    main()

