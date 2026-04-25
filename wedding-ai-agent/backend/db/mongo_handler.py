from pymongo import MongoClient
from datetime import datetime, timedelta
import os

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["wedding_ai"]
searches_col = db["searches"]
images_col = db["image_cache"]
cache_col = db["response_cache"]
budgets_col = db["budgets"]
conversations_col = db["conversations"]

# Index for TTL-based cache expiration (24 hours)
cache_col.create_index("timestamp", expireAfterSeconds=86400)

def save_search(query: str, corrected: str, ai_response: str, keywords: list, images: list):
    """Save search with complete metadata to MongoDB"""
    search_data = {
        "original_query": query,
        "corrected_query": corrected,
        "ai_response": ai_response,
        "keywords": keywords,
        "images": images,
        "timestamp": datetime.now()
    }
    result = searches_col.insert_one(search_data)
    return str(result.inserted_id)

def get_recent_searches(limit: int = 10):
    """Get recent searches with all metadata"""
    results = searches_col.find({}, {
        "_id": 0,
        "original_query": 1,
        "corrected_query": 1,
        "timestamp": 1
    }).sort("timestamp", -1).limit(limit)
    return list(results)

def cache_response(query: str, response_data: dict, ttl_hours: int = 24):
    """Cache complete search response for faster retrieval"""
    cache_data = {
        "query": query,
        "response": response_data,
        "timestamp": datetime.now()
    }
    cache_col.update_one(
        {"query": query},
        {"$set": cache_data},
        upsert=True
    )

def get_cached_response(query: str):
    """Retrieve cached response if available and fresh"""
    result = cache_col.find_one({"query": query})
    if result:
        return result.get("response")
    return None

def cache_images(keywords: str, images: list):
    """Cache images for specific keywords"""
    images_col.update_one(
        {"keywords": keywords},
        {"$set": {
            "images": images,
            "updated": datetime.now()
        }},
        upsert=True
    )

def get_cached_images(keywords: str):
    """Get cached images for keywords"""
    result = images_col.find_one({"keywords": keywords})
    if result:
        return result.get("images")
    return None

def clear_old_cache(days: int = 7):
    """Clear cache older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    cache_col.delete_many({"timestamp": {"$lt": cutoff_date}})
    images_col.delete_many({"updated": {"$lt": cutoff_date}})

def save_budget(user_id: str, total_budget: float, breakdown: dict):
    """Save wedding budget breakdown per user"""
    budget_data = {
        "user_id": user_id,
        "total_budget": total_budget,
        "breakdown": breakdown,
        "timestamp": datetime.now()
    }
    budgets_col.update_one(
        {"user_id": user_id},
        {"$set": budget_data},
        upsert=True
    )

def get_budget(user_id: str):
    """Get user's budget"""
    result = budgets_col.find_one({"user_id": user_id})
    if result:
        result.pop("_id", None)
        return result
    return None

def save_conversation(user_id: str, query: str, response: str):
    """Save conversation message for history"""
    msg = {
        "user_id": user_id,
        "query": query,
        "response": response,
        "timestamp": datetime.now()
    }
    conversations_col.insert_one(msg)

def get_conversation(user_id: str, limit: int = 10):
    """Get conversation history for user"""
    results = conversations_col.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    return list(results)[::-1]  # Reverse to show oldest first