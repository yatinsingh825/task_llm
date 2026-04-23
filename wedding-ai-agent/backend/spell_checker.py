from spellchecker import SpellChecker

spell = SpellChecker()

# Inject wedding-specific and Indian words the spell checker won't know
wedding_words = [
    "mehndi", "sangeet", "baraat", "mandap", "lehenga", "sherwani",
    "trousseau", "nikah", "walima", "haldi", "sindoor", "mangalsutra",
    "kanyadaan", "saptapadi", "pheras", "vidaai", "anand", "karaj",
    "laavan", "gurdwara", "gurudwara", "palla", "jaimala", "varmala",
    "milni", "grahpravesh", "griha", "pravesh", "muhurat", "pandit",
    "rajasthani", "dupatta", "chunni", "anarkali", "chandbali",
    "jhumka", "tikka", "maang", "nath", "payal", "kamarband",
    "bandhgala", "churidar", "mojri", "dhol", "bhangra", "kalbeliya",
    "rajnigandha", "tuberose", "mogra", "jasmine", "marigold",
    "peonies", "hydrangeas", "corsage", "bouquet", "officiant",
    "decor", "florals", "centerpieces", "tablescape", "venue",
    "catering", "videography", "photoshoot", "pre-wedding"
]
spell.word_frequency.load_words(wedding_words)

def get_suggestions(text: str) -> dict:
    words = text.split()
    suggestions = {}
    corrected_words = []

    for word in words:
        clean = word.lower().strip(".,!?\"'")
        if len(clean) < 3:
            corrected_words.append(word)
            continue

        if spell.unknown([clean]):
            best = spell.correction(clean)
            candidates = spell.candidates(clean) or set()
            if best and best != clean:
                suggestions[word] = {
                    "best": best,
                    "options": list(candidates)[:4]
                }
                corrected_words.append(best)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)

    corrected_text = " ".join(corrected_words)
    return {
        "original": text,
        "corrected": corrected_text,
        "suggestions": suggestions,
        "has_errors": len(suggestions) > 0
    }