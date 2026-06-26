from __future__ import annotations

import argparse
import inspect
from pathlib import Path

import torch
import yaml
from datasets import concatenate_datasets, load_dataset
from rich.console import Console
from trl import SFTConfig, SFTTrainer
from unsloth import FastModel


console = Console()


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
    args = parser.parse_args()

    cfg = read_config(args.config)
    max_seq_length = int(cfg["max_seq_length"])

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

    training_args = SFTConfig(
        output_dir=cfg["output_dir"],
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        packing=bool(cfg.get("packing", False)),
        num_train_epochs=float(train_cfg["num_train_epochs"]),
        max_steps=int(train_cfg["max_steps"]),
        per_device_train_batch_size=int(train_cfg["per_device_train_batch_size"]),
        gradient_accumulation_steps=int(train_cfg["gradient_accumulation_steps"]),
        learning_rate=float(train_cfg["learning_rate"]),
        warmup_steps=int(train_cfg["warmup_steps"]),
        weight_decay=float(train_cfg["weight_decay"]),
        lr_scheduler_type=train_cfg["lr_scheduler_type"],
        logging_steps=int(train_cfg["logging_steps"]),
        save_steps=int(train_cfg["save_steps"]),
        optim="adamw_8bit",
        fp16=not bf16,
        bf16=bf16,
        seed=int(train_cfg["seed"]),
        report_to="none",
    )

    trainer_kwargs = {
        "model": model,
        "train_dataset": dataset,
        "args": training_args,
    }
    processing_arg = "processing_class" if "processing_class" in inspect.signature(SFTTrainer.__init__).parameters else "tokenizer"
    trainer_kwargs[processing_arg] = tokenizer
    trainer = SFTTrainer(**trainer_kwargs)
    trainer.train()

    output_dir = Path(cfg["output_dir"])
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    console.print(f"[bold green]Adapter salvato in[/bold green] {output_dir}")


if __name__ == "__main__":
    main()
