import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))


def ask_gemini(user_input: str) -> str:
    try:
        system = "You are a wedding planning assistant. Give SHORT answers (2-3 sentences)."
        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(
            f"{system}\n\nQuestion: {user_input}",
            generation_config={
                "max_output_tokens": 150,
                "temperature": 0.7,
            }
        )

        return response.text[:300] if response.text else "No response."
    except Exception:
        return "Unable to generate response."


def get_image_keywords(user_input: str) -> list:
    keywords_map = {
        "mehendi": ["mehendi ceremony", "haldi ceremony"],
        "haldi": ["haldi ceremony", "mehendi"],
        "sangeet": ["sangeet ceremony", "wedding dance"],
        "venue": ["wedding venue", "banquet hall"],
        "dress": ["wedding dress", "bridal gown"],
    }

    user_lower = user_input.lower()

    for key, keywords in keywords_map.items():
        if key in user_lower:
            return keywords[:2]

    return ["wedding decoration", "wedding ceremony"]


def smart_agent(user_input: str) -> dict:
    response = ask_gemini(user_input)
    keywords = get_image_keywords(user_input)

    return {
        "response": response,
        "model_used": "gemini_api",
        "search_keywords": keywords
    }