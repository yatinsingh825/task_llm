import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

# ===== CONFIGURATION =====
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Small enough for laptop
DATA_FILE = "data/wedding_qa.jsonl"
OUTPUT_DIR = "../../models/wedding_model"
# =========================

print("Step 1: Loading your wedding data...")
data = []
with open(DATA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        # Format it as a conversation the model can learn from
        text = f"<human>: {item['prompt']}\n<assistant>: {item['completion']}"
        data.append({"text": text})

print(f"Loaded {len(data)} training examples")
dataset = Dataset.from_list(data)

print("Step 2: Loading base model (downloads first time, ~600MB)...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32,   # float32 for CPU, change to float16 if you have GPU
    device_map="auto"
)

print("Step 3: Applying LoRA (the magic that makes training efficient)...")
# LoRA only trains ~1% of the model's parameters
# This is WHY you can train on a laptop
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                    # Higher = more capacity, slower training
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output will say something like:
# trainable params: 2,097,152 || all params: 1,102,048,256 || trainable%: 0.19%
# This means you're only training 0.19% of the model — efficient!

print("Step 4: Tokenizing data...")
def tokenize_function(examples):
    tokens = tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length"
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

print("Step 5: Starting training...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=5,              # How many times to go through your data
    per_device_train_batch_size=1,   # Keep at 1 for laptop (low RAM)
    gradient_accumulation_steps=8,   # Simulates batch size of 8
    learning_rate=3e-4,
    warmup_steps=20,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    fp16=False,                      # Set True ONLY if you have NVIDIA GPU
    report_to="none",                # No wandb/tensorboard needed
    dataloader_num_workers=0         # Windows fix
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

print("Step 6: Saving YOUR trained model...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")
print("Training complete! Your model now knows about weddings.")