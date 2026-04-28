import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))


def ask_gemini(user_input: str) -> str:
    try:
        query_type = classify_query(user_input)

        prompt = f"""
You are a professional Indian wedding planner.

User Query: {user_input}

Give:
- Clear, practical suggestions
- 3-5 bullet points
- No generic AI phrases
"""

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 200,
                "temperature": 0.5,
            }
        )

        if not response.text:
            return "Here are some wedding ideas based on your query."

        return response.text.strip()

    except Exception as e:
        print("Gemini Error:", str(e))

        # ✅ SMART FALLBACK (IMPORTANT)
        return fallback_response(user_input)
    

def fallback_response(user_input: str) -> str:
    user = user_input.lower()

    if "sherwani" in user:
        return "Choose a sherwani in silk or velvet with embroidery. Pair it with a contrasting stole and mojris for a royal look."

    elif "haldi" in user:
        return "For a haldi ceremony, use yellow decor, marigold flowers, and simple seating. Keep it fun with music and playful rituals."

    elif "mehendi" in user:
        return "For mehendi, go for colorful decor, floral seating, and add music or dance for a lively vibe."

    elif "budget" in user:
        return "Plan your wedding budget by prioritizing venue, catering, and outfits. Keep 10–15% buffer for unexpected costs."

    else:
        return "Consider themes, budget planning, and guest comfort while organizing your wedding."


def get_image_keywords(user_input: str) -> list:
    user = user_input.lower()

    if "sherwani" in user:
        return ["groom sherwani", "indian groom outfit"]

    elif "lehenga" in user:
        return ["bridal lehenga", "indian bridal outfit"]

    elif "haldi" in user:
        return ["haldi ceremony decoration", "haldi event"]

    elif "mehendi" in user:
        return ["mehendi ceremony decor", "mehendi function"]

    elif "sangeet" in user:
        return ["sangeet dance stage", "wedding dance event"]

    elif "decoration" in user or "mandap" in user:
        return ["wedding mandap decor", "wedding stage decoration"]

    elif "venue" in user:
        return ["wedding venue india", "wedding banquet hall"]

    else:
        return ["indian wedding", "wedding ceremony"]
    
    
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