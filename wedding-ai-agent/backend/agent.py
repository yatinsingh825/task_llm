import os
import torch
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
TRAINED_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "wedding_model")

_tokenizer = None
_model = None

def load_my_model():
    global _tokenizer, _model
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel
        print(f"Loading YOUR trained wedding model from: {TRAINED_MODEL_PATH}")
        if not os.path.exists(TRAINED_MODEL_PATH):
            print(f"ERROR: Model path does not exist: {TRAINED_MODEL_PATH}")
            return

        # Use lower precision for faster CPU inference
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        _tokenizer = AutoTokenizer.from_pretrained(TRAINED_MODEL_PATH)
        # Load in float16 for CPU efficiency
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            dtype=torch.float16 if device == "cpu" else torch.float32,
            device_map="auto"  # Auto-detect best placement
        )
        _model = PeftModel.from_pretrained(base, TRAINED_MODEL_PATH)
        _model.eval()
        print("✅ Your trained model is ready!")
    except Exception as e:
        print(f"❌ Could not load trained model: {e}")
        import traceback
        traceback.print_exc()
        print("Will use Gemini API as fallback.")

def ask_my_model(user_input: str) -> str:
    if _model is None or _tokenizer is None:
        return ""
    try:
        import time
        start = time.time()
        prompt = f"<human>: {user_input}\n<assistant>:"

        inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            outputs = _model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=80,  # REDUCED: from 150 for faster generation
                min_length=10,
                do_sample=False,  # Greedy decoding
                pad_token_id=_tokenizer.eos_token_id,
                eos_token_id=_tokenizer.eos_token_id,
                use_cache=True,  # Enable caching for faster generation
                num_beams=1,  # Greedy search (fastest)
            )

        response = _tokenizer.decode(outputs[0], skip_special_tokens=True)
        text = response.split("<assistant>:")[-1].strip()

        # Ensure response ends with proper punctuation
        if text and text[-1] not in '.!?\n':
            text = text + '.'

        elapsed = time.time() - start
        print(f"⏱️ Model inference took {elapsed:.2f}s ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"Trained model error: {e}")
        import traceback
        traceback.print_exc()
        return ""

def ask_gemini(user_input: str) -> str:
    try:
        system = """You are a wedding planning assistant. Give SHORT, direct answers (2-3 sentences max)."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"{system}\n\nQuestion: {user_input}",
            generation_config={
                "max_output_tokens": 150,  # Short answers only
                "temperature": 0.7,
            },
            request_options={"timeout": 8}  # Timeout after 8 seconds
        )
        return response.text[:300]  # Cap at 300 chars
    except Exception as e:
        return "Unable to generate response."

def get_image_keywords(user_input: str) -> list:
    """Smart keyword extraction for wedding-related queries"""
    keywords_map = {
        "honeymoon": ["honeymoon destination", "honeymoon resort"],
        "beach": ["beach wedding", "tropical honeymoon"],
        "flower": ["wedding flowers", "floral decoration"],
        "dress": ["wedding dress", "bridal gown"],
        "cake": ["wedding cake", "dessert"],
        "decoration": ["wedding decoration", "venue"],
        "mehendi": ["mehendi ceremony", "haldi ceremony"],
        "haldi": ["haldi ceremony", "mehendi"],
        "sangeet": ["sangeet ceremony", "wedding dance"],
        "reception": ["wedding reception", "reception decor"],
        "photoshoot": ["wedding photoshoot", "pre-wedding shoot"],
        "bride": ["bridal jewelry", "bridal makeup"],
        "groom": ["groom outfit", "sherwani"],
        "venue": ["wedding venue", "banquet hall"],
        "invitation": ["wedding card", "invitation design"],
        "jewelry": ["bridal jewelry", "wedding jewelry"],
        "makeup": ["bridal makeup", "wedding makeup"],
        "lehenga": ["wedding lehenga", "bridal lehenga"],
        "sherwani": ["sherwani", "groom outfit"],
        "budget": ["wedding budget", "cost saving tips"],
        "planner": ["wedding planner", "event planning"],
    }

    user_lower = user_input.lower()

    # Check for wedding-related keywords
    for key, keywords in keywords_map.items():
        if key in user_lower:
            return keywords[:2]

    # Check if query is wedding-related at all
    wedding_terms = ["wedding", "marriage", "bride", "groom", "ceremony", "mandap", "baraat"]
    is_wedding_query = any(term in user_lower for term in wedding_terms)

    if not is_wedding_query:
        # Non-wedding query - return generic images or empty
        # This prevents unrelated content
        return []

    # Default fallback for other wedding queries
    return ["wedding decoration", "wedding ceremony"]

def smart_agent(user_input: str) -> dict:
    # Try YOUR trained model first
    my_answer = ask_my_model(user_input)

    if my_answer:  # If we got any response from trained model
        source = "your_trained_model"
        response = my_answer
        print(f"✅ Using trained model response ({len(my_answer)} chars)")
    else:
        # Fallback to Gemini only if trained model failed
        source = "gemini_api"
        response = ask_gemini(user_input)
        print(f"⚠️ Trained model failed, using Gemini API")

    keywords = get_image_keywords(user_input)

    return {
        "response": response,
        "model_used": source,
        "search_keywords": keywords
    }

# Load your trained model when this module is imported
load_my_model()