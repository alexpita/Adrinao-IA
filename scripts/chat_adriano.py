from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


SYSTEM = (
    "Sei Adriano, un assistente bilingue italiano e inglese. "
    "Rispondi nella lingua dell'utente con precisione, concretezza e cura linguistica."
)


def load_model(base_model: str, adapter: Path | None):
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(adapter or base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=quantization,
        device_map="auto",
        trust_remote_code=True,
    )
    if adapter:
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model, tokenizer


def apply_qwen_chat_template(tokenizer, messages: list[dict]) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="unsloth/Qwen3-14B-unsloth-bnb-4bit")
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=700)
    args = parser.parse_args()

    model, tokenizer = load_model(args.base_model, args.adapter)
    messages = [{"role": "system", "content": SYSTEM}]
    print("Adriano pronto. Scrivi 'exit' per uscire.")

    while True:
        user_text = input("\nTu> ").strip()
        if user_text.lower() in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user_text})
        prompt = apply_qwen_chat_template(tokenizer, messages)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=0.6,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_tokens = output[0][inputs["input_ids"].shape[-1] :]
        answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        messages.append({"role": "assistant", "content": answer})
        print(f"\nAdriano> {answer}")


if __name__ == "__main__":
    main()
