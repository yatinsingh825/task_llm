from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
import torch

# Use a small base model (runs on laptop)
BASE_MODEL = "microsoft/phi-2"  # Only 2.7B params, runs on 8GB RAM
# Alternative: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def train_wedding_model():
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,  # Use float32 for CPU
        trust_remote_code=True
    )
    
    # LoRA config - trains only small adapters (efficient!)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,               # Rank
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]  # Attention layers
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    # This will show: ~1% of params trained (very efficient!)
    
    # Load your dataset
    dataset = load_dataset("json", data_files="data/wedding_qa.jsonl", split="train")
    
    def tokenize(examples):
        text = f"Question: {examples['prompt']}\nAnswer: {examples['completion']}"
        return tokenizer(text, truncation=True, max_length=512, padding="max_length")
    
    tokenized = dataset.map(tokenize, batched=False)
    
    # Training arguments (optimized for laptop)
    training_args = TrainingArguments(
        output_dir="../../models/fine_tuned",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        save_steps=50,
        logging_steps=10,
        fp16=False,        # Set True if you have NVIDIA GPU
        report_to="none"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
    )
    
    print("Starting training...")
    trainer.train()
    
    # Save the fine-tuned model
    model.save_pretrained("../../models/fine_tuned")
    tokenizer.save_pretrained("../../models/fine_tuned")
    print("✅ Model saved to models/fine_tuned/")

if __name__ == "__main__":
    train_wedding_model()