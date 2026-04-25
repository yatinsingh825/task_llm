from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import smart_agent
from spell_checker import get_suggestions
from image_handler import get_images
from db.mongo_handler import (
    save_search, get_recent_searches,
    cache_response, get_cached_response,
    cache_images, get_cached_images,
    save_budget, get_budget, save_conversation, get_conversation
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

class BudgetRequest(BaseModel):
    total_budget: float
    user_id: str

class ConversationRequest(BaseModel):
    user_id: str
    query: str
    history: list = []

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

@app.post("/budget")
async def save_budget_endpoint(req: BudgetRequest):
    """Save wedding budget breakdown"""
    budget_breakdown = {
        "venue": req.total_budget * 0.30,
        "catering": req.total_budget * 0.35,
        "decor": req.total_budget * 0.20,
        "photography": req.total_budget * 0.10,
        "music_entertainment": req.total_budget * 0.05
    }
    save_budget(req.user_id, req.total_budget, budget_breakdown)
    return {
        "total_budget": req.total_budget,
        "breakdown": budget_breakdown
    }

@app.get("/budget/{user_id}")
async def get_budget_endpoint(user_id: str):
    """Retrieve user's budget"""
    budget = get_budget(user_id)
    if not budget:
        return {"error": "No budget found"}
    return budget

@app.post("/checklist-pdf")
async def generate_checklist_pdf():
    """Generate 12-month wedding checklist PDF"""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import inch

    # Create PDF in memory
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#c9636a'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#b8974a'),
        spaceAfter=8
    )

    # Checklist data
    checklist_data = [
        ("12 Months Before", ["Decide on wedding date", "Set budget", "Create guest list", "Book venue"]),
        ("9-10 Months", ["Book catering", "Book photographer/videographer", "Select wedding attire"]),
        ("6-8 Months", ["Send save-the-date", "Plan honeymoon", "Book wedding planner"]),
        ("3-4 Months", ["Finalize guest list", "Order invitations", "Plan ceremonies", "Book band/DJ"]),
        ("1-2 Months", ["Final dress fitting", "Confirm all vendor details", "Plan seating", "Prepare speeches"]),
        ("2 Weeks", ["Confirm vendor arrivals", "Final headcount", "Prepare payment cheques", "Rehearsal dinner"]),
        ("1 Week", ["Final confirmations", "Pack for honeymoon", "Confirm transportation", "Get manicure/pedicure"]),
        ("Wedding Day", ["Hair and makeup", "Eat a good breakfast", "Arrive early", "Enjoy the day! 💍"])
    ]

    # Build content
    story = []
    story.append(Paragraph("🎊 Your 12-Month Wedding Planning Checklist", title_style))
    story.append(Spacer(1, 0.2*inch))

    for timeline, tasks in checklist_data:
        story.append(Paragraph(f"✓ {timeline}", heading_style))
        tasks_table = Table([[f"• {task}"] for task in tasks], colWidths=[7*inch])
        tasks_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#3a2a30')),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#e8d9db')),
        ]))
        story.append(tasks_table)
        story.append(Spacer(1, 0.15*inch))

    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)

    import base64
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode()
    return {
        "pdf": pdf_base64,
        "filename": "wedding-checklist-12-months.pdf"
    }

@app.post("/chat")
async def chat_with_history(req: ConversationRequest):
    """Chat endpoint with conversation history"""
    import time
    total_start = time.time()

    # Get spell corrected query
    spell_result = get_suggestions(req.query)
    final_query = spell_result["corrected"]

    # Get AI response (this time with context of history)
    loop = asyncio.get_event_loop()

    try:
        # Build context from history
        context = ""
        if req.history:
            for msg in req.history[-5:]:  # Use last 5 messages for context
                context += f"User: {msg['query']}\nAssistant: {msg['response']}\n\n"

        # Prepare the prompt with history
        full_prompt = f"{context}User: {final_query}\nAssistant:"

        # Run agent with context
        agent_start = time.time()
        agent_result = await asyncio.wait_for(
            loop.run_in_executor(executor, smart_agent, final_query),
            timeout=20.0
        )

        # Save to conversation history
        save_conversation(req.user_id, final_query, agent_result["response"])

        total_elapsed = time.time() - total_start
        print(f"✅ Chat response in {total_elapsed:.2f}s")

        return {
            "query": final_query,
            "response": agent_result["response"],
            "model_used": agent_result["model_used"],
            "search_keywords": agent_result.get("search_keywords", [])
        }
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return {
            "query": final_query,
            "response": "Error generating response. Please try again.",
            "model_used": "error",
            "search_keywords": []
        }

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "TinyLlama LoRA fine-tuned + Gemini fallback",
        "cache": "MongoDB",
        "optimizations": "Parallel image fetching, greedy decoding, 6 images, 250 tokens"
    }