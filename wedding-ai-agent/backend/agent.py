import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))


def ask_gemini(user_input: str) -> str:
    try:
        query_type = classify_query(user_input)

        base_prompt = """
You are an expert Indian wedding planning assistant.

Give clear, practical advice. Keep answers short (3–5 lines).
"""

        # Add specialization
        if query_type == "budget":
            extra = "Focus on cost-saving tips and budget breakdown."
        elif query_type == "event":
            extra = "Give event-specific ideas and suggestions."
        elif query_type == "fashion":
            extra = "Suggest outfits, styles, and trends."
        elif query_type == "decor":
            extra = "Focus on decoration and venue ideas."
        else:
            extra = "Give general wedding advice."

        final_prompt = f"{base_prompt}\n{extra}\n\nUser Query: {user_input}"

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            final_prompt,
            generation_config={
                "max_output_tokens": 200,
                "temperature": 0.6,
            },
            request_options={"timeout": 20}
        )

        return response.text.strip() if response.text else "No response."

    except Exception as e:
        print("Gemini Error:", str(e))
        return "Sorry, I'm having trouble right now. Please try again."

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


def classify_query(user_input: str) -> str:
    user_input = user_input.lower()

    if any(word in user_input for word in ["budget", "cost", "price"]):
        return "budget"
    elif any(word in user_input for word in ["mehendi", "haldi", "sangeet", "wedding"]):
        return "event"
    elif any(word in user_input for word in ["dress", "lehenga", "jewelry"]):
        return "fashion"
    elif any(word in user_input for word in ["venue", "decoration", "mandap"]):
        return "decor"
    else:
        return "general"

def smart_agent(user_input: str) -> dict:
    response = ask_gemini(user_input)
    keywords = get_image_keywords(user_input)

    return {
        "response": response,
        "model_used": "gemini_api",
        "search_keywords": keywords
    }