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

# ✅ SAFE index creation (prevents crash)
try:
    cache_col.create_index("timestamp", expireAfterSeconds=86400)
except Exception as e:
    print("Mongo index error:", e)


def save_search(query: str, corrected: str, ai_response: str, keywords: list, images: list):
    search_data = {
        "original_query": query,
        "corrected_query": corrected,
        "ai_response": ai_response,
        "keywords": keywords,
        "images": images,
        "timestamp": datetime.utcnow()
    }
    result = searches_col.insert_one(search_data)
    return str(result.inserted_id)


def get_recent_searches(limit: int = 10):
    results = searches_col.find({}, {
        "_id": 0,
        "original_query": 1,
        "corrected_query": 1,
        "timestamp": 1
    }).sort("timestamp", -1).limit(limit)
    return list(results)


def cache_response(query: str, response_data: dict):
    cache_data = {
        "query": query,
        "response": response_data,
        "timestamp": datetime.utcnow()
    }
    cache_col.update_one({"query": query}, {"$set": cache_data}, upsert=True)


def get_cached_response(query: str):
    result = cache_col.find_one({"query": query})
    return result.get("response") if result else None


def cache_images(keywords: str, images: list):
    images_col.update_one(
        {"keywords": keywords},
        {"$set": {"images": images, "updated": datetime.utcnow()}},
        upsert=True
    )


def get_cached_images(keywords: str):
    result = images_col.find_one({"keywords": keywords})
    return result.get("images") if result else None


def clear_old_cache(days: int = 7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    cache_col.delete_many({"timestamp": {"$lt": cutoff}})
    images_col.delete_many({"updated": {"$lt": cutoff}})


def save_budget(user_id: str, total_budget: float, breakdown: dict):
    data = {
        "user_id": user_id,
        "total_budget": total_budget,
        "breakdown": breakdown,
        "timestamp": datetime.utcnow()
    }
    budgets_col.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


def get_budget(user_id: str):
    result = budgets_col.find_one({"user_id": user_id})
    if result:
        result.pop("_id", None)
        return result
    return None


def save_conversation(user_id: str, query: str, response: str):
    conversations_col.insert_one({
        "user_id": user_id,
        "query": query,
        "response": response,
        "timestamp": datetime.utcnow()
    })


def get_conversation(user_id: str, limit: int = 10):
    results = conversations_col.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    return list(results)[::-1]