import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
TRAINED_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "wedding_model")

_tokenizer = None
_model = None


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
    response = ask_gemini(user_input)
    keywords = get_image_keywords(user_input)

    return {
        "response": response,
        "model_used": "gemini_api",
        "search_keywords": keywords
    }

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
