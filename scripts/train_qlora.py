from __future__ import annotations

import argparse
import datetime as dt
import inspect
import logging
import os
import re
import sys
import warnings
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("FLAGS_minloglevel", "2")

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("datasets").setLevel(logging.ERROR)

# Unsloth must patch Torch/TRL before they are imported.
import unsloth  # noqa: F401
import torch
import yaml
from datasets import concatenate_datasets, load_dataset
from datasets.utils.logging import disable_progress_bar
from rich.console import Console
from trl import SFTConfig, SFTTrainer
from unsloth import FastModel


console = Console()
disable_progress_bar()


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def enable_file_log(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a", encoding="utf-8", buffering=1)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = Tee(original_stdout, handle)
    sys.stderr = Tee(original_stderr, handle)
    print()
    print("=" * 60)
    print(f"Adriano training log - {dt.datetime.now().isoformat(timespec='seconds')}")
    print("=" * 60)
    return handle, original_stdout, original_stderr


def latest_checkpoint(output_dir: Path) -> Path | None:
    if not output_dir.exists():
        return None
    checkpoints = []
    for path in output_dir.glob("checkpoint-*"):
        if not path.is_dir():
            continue
        match = re.fullmatch(r"checkpoint-(\d+)", path.name)
        if match:
            checkpoints.append((int(match.group(1)), path))
    if not checkpoints:
        return None
    return max(checkpoints, key=lambda item: item[0])[1]


def read_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_jsonl_dataset(files: list[str]):
    datasets = []
    for file_name in files:
        file_path = Path(file_name)
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        datasets.append(load_dataset("json", data_files=str(file_path), split="train"))
    return datasets[0] if len(datasets) == 1 else concatenate_datasets(datasets)


def ensure_messages(example: dict) -> None:
    messages = example.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError("Ogni riga deve contenere un campo messages con almeno system/user e assistant.")
    for message in messages:
        if message.get("role") not in {"system", "user", "assistant"}:
            raise ValueError(f"Ruolo non valido: {message.get('role')}")
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            raise ValueError("Ogni message deve avere content non vuoto.")


def apply_qwen_chat_template(tokenizer, messages: list[dict], enable_thinking: bool) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--resume", choices=["auto", "never"], default="auto")
    parser.add_argument("--log-file", type=Path)
    args = parser.parse_args()

    log_handle = None
    original_stdout = None
    original_stderr = None
    if args.log_file:
        log_handle, original_stdout, original_stderr = enable_file_log(args.log_file)
    cfg = read_config(args.config)
    max_seq_length = int(cfg["max_seq_length"])
    output_dir = Path(cfg["output_dir"])
    console.print(
        "[bold]Training profile:[/bold] "
        f"packing={bool(cfg.get('packing', False))}, "
        f"max_seq_length={max_seq_length}, "
        f"epochs={cfg['training']['num_train_epochs']}, "
        f"max_steps={cfg['training']['max_steps']}"
    )

    console.print(f"[bold]Loading base model:[/bold] {cfg['base_model']}")
    model, tokenizer = FastModel.from_pretrained(
        model_name=cfg["base_model"],
        max_seq_length=max_seq_length,
        load_in_4bit=True,
        full_finetuning=False,
    )

    lora_cfg = cfg["lora"]
    model = FastModel.get_peft_model(
        model,
        r=int(lora_cfg["r"]),
        target_modules=lora_cfg["target_modules"],
        lora_alpha=int(lora_cfg["alpha"]),
        lora_dropout=float(lora_cfg["dropout"]),
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=int(cfg["training"]["seed"]),
    )

    raw_dataset = load_jsonl_dataset(cfg["train_files"])
    for row in raw_dataset.select(range(min(5, len(raw_dataset)))):
        ensure_messages(row)

    enable_thinking = bool(cfg.get("enable_thinking_template", False))

    def format_batch(batch: dict) -> dict:
        texts = []
        for messages in batch["messages"]:
            texts.append(apply_qwen_chat_template(tokenizer, messages, enable_thinking))
        return {"text": texts}

    remove_columns = list(raw_dataset.column_names)
    dataset = raw_dataset.map(format_batch, batched=True, remove_columns=remove_columns, num_proc=1)

    train_cfg = cfg["training"]
    bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    sft_params = inspect.signature(SFTConfig.__init__).parameters
    sft_kwargs = {
        "output_dir": cfg["output_dir"],
        "dataset_text_field": "text",
        "packing": bool(cfg.get("packing", False)),
        "num_train_epochs": float(train_cfg["num_train_epochs"]),
        "max_steps": int(train_cfg["max_steps"]),
        "per_device_train_batch_size": int(train_cfg["per_device_train_batch_size"]),
        "gradient_accumulation_steps": int(train_cfg["gradient_accumulation_steps"]),
        "learning_rate": float(train_cfg["learning_rate"]),
        "warmup_steps": int(train_cfg["warmup_steps"]),
        "weight_decay": float(train_cfg["weight_decay"]),
        "lr_scheduler_type": train_cfg["lr_scheduler_type"],
        "logging_steps": int(train_cfg["logging_steps"]),
        "save_steps": int(train_cfg["save_steps"]),
        "optim": "adamw_8bit",
        "fp16": not bf16,
        "bf16": bf16,
        "seed": int(train_cfg["seed"]),
        "report_to": "none",
    }
    if "save_total_limit" in train_cfg:
        sft_kwargs["save_total_limit"] = int(train_cfg["save_total_limit"])
    if "max_seq_length" in sft_params:
        sft_kwargs["max_seq_length"] = max_seq_length
    elif "max_length" in sft_params:
        sft_kwargs["max_length"] = max_seq_length
    else:
        console.print("[yellow]SFTConfig has no max length argument; relying on dataset/model defaults.[/yellow]")

    training_args = SFTConfig(**{key: value for key, value in sft_kwargs.items() if key in sft_params})

    trainer_kwargs = {
        "model": model,
        "train_dataset": dataset,
        "args": training_args,
    }
    processing_arg = "processing_class" if "processing_class" in inspect.signature(SFTTrainer.__init__).parameters else "tokenizer"
    trainer_kwargs[processing_arg] = tokenizer
    trainer = SFTTrainer(**trainer_kwargs)

    resume_from_checkpoint = None
    if args.resume == "auto":
        checkpoint = latest_checkpoint(output_dir)
        if checkpoint is not None:
            resume_from_checkpoint = str(checkpoint)
            console.print(f"[bold yellow]Ripartenza automatica da checkpoint:[/bold yellow] {checkpoint}")
        else:
            console.print("[bold]Nessun checkpoint precedente: training da zero.[/bold]")

    trainer.train(resume_from_checkpoint=resume_from_checkpoint)

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    console.print(f"[bold green]Adapter salvato in[/bold green] {output_dir}")
    if log_handle is not None:
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_handle.close()


if __name__ == "__main__":
    main()
