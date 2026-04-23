from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import smart_agent
from spell_checker import get_suggestions
from image_handler import get_images
from db.mongo_handler import (
    save_search, get_recent_searches,
    cache_response, get_cached_response,
    cache_images, get_cached_images
)
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="Wedding AI Planner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=3)

class SearchRequest(BaseModel):
    query: str

class SpellRequest(BaseModel):
    text: str

@app.post("/search")
async def search(req: SearchRequest):
    import time
    total_start = time.time()
    spell_result = get_suggestions(req.query)
    final_query = spell_result["corrected"]

    # Check if response is cached - FASTEST PATH
    cached_response = get_cached_response(final_query)
    if cached_response:
        elapsed = time.time() - total_start
        print(f"✅ Cache hit in {elapsed:.2f}s")
        return {
            "original_query": req.query,
            "spell_check": spell_result,
            "ai_response": cached_response["ai_response"],
            "model_used": cached_response["model_used"],
            "search_keywords": cached_response["search_keywords"],
            "images": cached_response["images"],
            "from_cache": True
        }

    # Get loop and timeout after 10 seconds total
    loop = asyncio.get_event_loop()

    try:
        # Run agent and image fetching in parallel with timeout
        agent_start = time.time()
        agent_result = await asyncio.wait_for(
            loop.run_in_executor(executor, smart_agent, final_query),
            timeout=20.0  # Increased to 20 seconds for CPU inference
        )
        agent_elapsed = time.time() - agent_start
        print(f"Agent response in {agent_elapsed:.2f}s")

        keywords = agent_result["search_keywords"]
        keywords_key = ",".join(keywords)

        # Check if images are cached
        cached_images = get_cached_images(keywords_key)
        if cached_images:
            images = cached_images
        else:
            # Fetch images with timeout
            try:
                images = await asyncio.wait_for(
                    loop.run_in_executor(executor, get_images, keywords),
                    timeout=10.0  # Increased to 10 seconds for image fetching
                )
            except asyncio.TimeoutError:
                print("Image fetch timeout - using empty list")
                images = []

            if images:
                cache_images(keywords_key, images)

        # Prepare response
        response_data = {
            "ai_response": agent_result["response"],
            "model_used": agent_result["model_used"],
            "search_keywords": keywords,
            "images": images
        }

        # Cache the complete response
        cache_response(final_query, response_data)

        # Save to search history (non-blocking)
        loop.run_in_executor(executor, save_search, req.query, final_query,
                            agent_result["response"], keywords, images)

        total_elapsed = time.time() - total_start
        print(f"✅ Total search completed in {total_elapsed:.2f}s")

        return {
            "original_query": req.query,
            "spell_check": spell_result,
            "ai_response": agent_result["response"],
            "model_used": agent_result["model_used"],
            "search_keywords": keywords,
            "images": images,
            "from_cache": False
        }

    except asyncio.TimeoutError:
        total_elapsed = time.time() - total_start
        print(f"❌ Search timeout after {total_elapsed:.2f}s - returning cached or default")
        return {
            "original_query": req.query,
            "spell_check": spell_result,
            "ai_response": "Request took too long. Please try again.",
            "model_used": "timeout",
            "search_keywords": [],
            "images": [],
            "from_cache": False
        }
    except Exception as e:
        total_elapsed = time.time() - total_start
        print(f"❌ Search error after {total_elapsed:.2f}s: {e}")
        return {
            "original_query": req.query,
            "spell_check": spell_result,
            "ai_response": "Error generating response.",
            "model_used": "error",
            "search_keywords": [],
            "images": [],
            "from_cache": False
        }

@app.post("/spell-check")
async def spell_check(req: SpellRequest):
    return get_suggestions(req.text)

@app.get("/history")
async def history():
    return get_recent_searches(10)

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "TinyLlama LoRA fine-tuned + Gemini fallback",
        "cache": "MongoDB",
        "optimizations": "Parallel image fetching, greedy decoding, 6 images, 250 tokens"
    }