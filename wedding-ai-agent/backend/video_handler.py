import requests
import os

PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

def search_pixabay_videos(keyword: str, count: int = 4) -> list:
    """Fetch videos from Pixabay (free video API)"""
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={keyword}&per_page={count}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        videos = []
        for hit in data.get("hits", []):
            videos.append({
                "url": hit["videos"]["medium"]["url"],
                "thumbnail": hit.get("picture_id", ""),
                "duration": hit["duration"],
                "user": hit["user"],
                "source": "pixabay"
            })
        return videos
    except Exception as e:
        print(f"Video search error: {e}")
        return []

def get_videos_for_keywords(keywords: list) -> list:
    """Get videos for keywords"""
    all_videos = []
    for keyword in keywords:
        vids = search_pixabay_videos(keyword, count=2)
        all_videos.extend(vids)
    return all_videos[:6]