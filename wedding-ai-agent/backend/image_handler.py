import requests
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

def search_pexels(keyword: str, count: int = 3) -> list:
    if not PEXELS_KEY:
        return []
    try:
        headers = {"Authorization": PEXELS_KEY}
        url = f"https://api.pexels.com/v1/search?query={keyword}&per_page={count}&orientation=landscape"
        r = requests.get(url, headers=headers, timeout=5, verify=False)  # Disable SSL verification for Windows compatibility
        data = r.json()
        return [
            {
                "url": p["src"]["large"],
                "thumbnail": p["src"]["medium"],
                "credit": p["photographer"],
                "source": "pexels"
            }
            for p in data.get("photos", [])
        ]
    except Exception as e:
        print(f"Pexels error: {e}")
        return []

def search_pixabay(keyword: str, count: int = 3) -> list:
    if not PIXABAY_KEY or PIXABAY_KEY == "your_pixabay_key_here":
        return []
    try:
        url = (
            f"https://pixabay.com/api/?key={PIXABAY_KEY}"
            f"&q={requests.utils.quote(keyword)}"
            f"&image_type=photo&per_page={count}&safesearch=true"
        )
        r = requests.get(url, timeout=5, verify=False)  # Disable SSL verification for Windows compatibility
        data = r.json()
        return [
            {
                "url": h["largeImageURL"],
                "thumbnail": h["webformatURL"],
                "credit": h["user"],
                "source": "pixabay"
            }
            for h in data.get("hits", [])
        ]
    except Exception as e:
        print(f"Pixabay error: {e}")
        return []

def get_images_for_keyword(keyword: str, target_count: int = 3) -> list:
    """Fetch images from both sources in parallel for a single keyword"""
    images = []

    # Try Pexels first (often faster)
    pexels_imgs = search_pexels(keyword, count=target_count)
    if pexels_imgs:
        return pexels_imgs[:target_count]

    # If Pexels fails or returns few, try Pixabay
    pixabay_imgs = search_pixabay(keyword, count=target_count)
    return pixabay_imgs[:target_count] if pixabay_imgs else []

def get_images(keywords: list) -> list:
    """
    Ultra-fast image fetching - only 3 images for instant rendering.
    Uses parallel fetching with aggressive timeout.
    """
    all_images = []

    # Parallel image fetching for each keyword
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Only fetch 1-2 images per keyword for speed (3 images total)
        futures = {executor.submit(get_images_for_keyword, kw, 2): kw for kw in keywords}

        for future in as_completed(futures, timeout=6):  # 6 second max timeout total
            try:
                images = future.result(timeout=5)  # 5 second per image fetch
                all_images.extend(images)
                # Early exit if we have enough
                if len(all_images) >= 3:
                    break
            except Exception as e:
                print(f"Error fetching images: {e}")

    # Return exactly 3 images for fast rendering
    return all_images[:3]