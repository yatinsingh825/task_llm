from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
TRAINED_MODEL_PATH = "../../models/wedding_model"

print("Loading your trained model...")
tokenizer = AutoTokenizer.from_pretrained(TRAINED_MODEL_PATH)
base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32)
model = PeftModel.from_pretrained(base, TRAINED_MODEL_PATH)
model.eval()
print("Model loaded! Ask it wedding questions.\n")

def ask(question):
    prompt = f"<human>: {question}\n<assistant>:"
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("<assistant>:")[-1].strip()

# Test questions
questions = [
    "What flowers are best for a wedding mandap?",
    "How do I plan a mehndi ceremony?",
    "What is the saptapadi ritual?",
    "What is a good wedding budget for 200 guests?"
]

for q in questions:
    print(f"Q: {q}")
    print(f"A: {ask(q)}")
    print("-" * 60)