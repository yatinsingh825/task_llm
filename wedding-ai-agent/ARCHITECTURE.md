# 🎊 Wedding AI Planner - Architecture & Flow Diagrams

## System Architecture Flowchart

### Complete Data Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Browser)                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     User Interface Tabs                              │   │
│  │  ┌────────────┬────────────┬──────────────┬────────────────────────┐ │   │
│  │  │   SEARCH   │   BUDGET   │  CHECKLIST   │         CHAT           │ │   │
│  │  │            │            │              │                        │ │   │
│  │  │ - Input    │ - Form     │ - Button     │ - Message input        │ │   │
│  │  │ - Mic btn  │ - Number   │ - Download   │ - Message history      │ │   │
│  │  │ - Results  │ - Calc btn │   link       │ - Context display      │ │   │
│  │  │ - Images   │ - Pie      │              │                        │ │   │
│  │  │            │   chart    │              │                        │ │   │
│  │  └────────────┴────────────┴──────────────┴────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                            JavaScript (app.js)                               │
│                   - Form handling, API calls, DOM updates                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑ ↓
                              HTTP REST API
                                    ↑ ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI Server)                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         API Routes (main.py)                         │   │
│  │  ┌──────────────┬──────────────┬──────────┬────────────────────────┐ │   │
│  │  │   /search    │   /budget    │   /chat  │  /checklist-pdf        │ │   │
│  │  │              │              │          │                        │ │   │
│  │  │ 1. Spell-    │ 1. Validate  │ 1. Spell │ 1. Create PDF object   │ │   │
│  │  │    check     │    budget    │    check │ 2. Add content         │ │   │
│  │  │ 2. Cache     │ 2. Calculate │ 2. Get   │ 3. Style with colors   │ │   │
│  │  │    lookup    │    breakdown │    model │ 4. Encode base64       │ │   │
│  │  │ 3. Call      │ 3. Save to   │    response                       │ │   │
│  │  │    smart_    │    DB        │ 3. Add   │ → Return PDF           │ │   │
│  │  │    agent()   │ 4. Return    │    to    │                        │ │   │
│  │  │ 4. Get       │    result    │    history                        │ │   │
│  │  │    images    │              │ 4. Return                         │ │   │
│  │  │ 5. Cache     │              │    response                       │ │   │
│  │  │    response  │              │                                   │ │   │
│  │  │ 6. Return    │              │                                   │ │   │
│  │  │    result    │              │                                   │ │   │
│  │  └──────────────┴──────────────┴──────────┴────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Support Modules (agent.py)                        │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  smart_agent(user_input) ← Called by /search & /chat         │ │   │
│  │  │                                                                │ │   │
│  │  │  ┌────────────────────────────────────────────────────────┐  │ │   │
│  │  │  │ TRY: ask_my_model(input)                              │  │ │   │
│  │  │  │ ├─ Load model from: models/wedding_model/            │  │ │   │
│  │  │  │ ├─ Base Model: TinyLlama-1.1B                         │  │ │   │
│  │  │  │ ├─ LoRA Adapter: Fine-tuned on wedding Q&A           │  │ │   │
│  │  │  │ ├─ Device: GPU if available, else CPU                │  │ │   │
│  │  │  │ └─ Return: Generated response (max 80 tokens)        │  │ │   │
│  │  │  │                                                        │  │ │   │
│  │  │  │ CATCH: If model fails or empty response              │  │ │   │
│  │  │  │ ├─ Log: "⚠️ Trained model failed"                    │  │ │   │
│  │  │  │ └─ FALLBACK: ask_gemini(input)                       │  │ │   │
│  │  │  │    ├─ API: google-generativeai                       │  │ │   │
│  │  │  │    ├─ Model: Gemini 1.5 Flash                        │  │ │   │
│  │  │  │    └─ Return: Generated response                     │  │ │   │
│  │  │  │                                                        │  │ │   │
│  │  │  │ EXTRACT: Keywords from input for image search        │  │ │   │
│  │  │  │ └─ get_image_keywords(input)                         │  │ │   │
│  │  │  │    → Return wedding-related search terms             │  │ │   │
│  │  │  └────────────────────────────────────────────────────────┘  │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │  Other Support Functions:                                 │ │   │
│  │  │  ├─ spell_checker.py → get_suggestions(text)              │ │   │
│  │  │  │  └─ Returns: corrected text + corrections made         │ │   │
│  │  │  ├─ image_handler.py → get_images(keywords)               │ │   │
│  │  │  │  └─ Returns: list of image URLs                        │ │   │
│  │  │  └─ video_handler.py → (optional video support)           │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │               Database Operations (mongo_handler.py)             │   │
│  │  ├─ get_cached_response(query) ─→ Fast lookup                   │   │
│  │  ├─ cache_response(query, response) ─→ Store for reuse          │   │
│  │  ├─ get_cached_images(keywords) ─→ Image cache lookup           │   │
│  │  ├─ cache_images(keywords, images) ─→ Store images              │   │
│  │  ├─ save_search(query, response, ...) ─→ Search history         │   │
│  │  ├─ save_budget(user_id, budget, breakdown) ─→ Store budget     │   │
│  │  ├─ get_budget(user_id) ─→ Retrieve user budget                 │   │
│  │  ├─ save_conversation(user_id, query, response) ─→ Chat history │   │
│  │  └─ get_conversation(user_id) ─→ Retrieve chat history          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        MongoDB (Data Storage)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Collections:                                                     │   │
│  │  ┌──────────────────┐   ┌──────────────────┐                   │   │
│  │  │ cache_responses  │   │ cached_images    │                   │   │
│  │  │ (Query → Result) │   │ (Keywords→URLs)  │                   │   │
│  │  └──────────────────┘   └──────────────────┘                   │   │
│  │           ↑ Fast lookup (0.02s for hits)                        │   │
│  │  ┌──────────────────┐   ┌──────────────────┐                   │   │
│  │  │ searches_col     │   │ budgets_col      │                   │   │
│  │  │ (History)        │   │ (User budgets)   │                   │   │
│  │  └──────────────────┘   └──────────────────┘                   │   │
│  │  ┌──────────────────────────────────────┐                      │   │
│  │  │ conversations_col (Chat history)     │                      │   │
│  │  └──────────────────────────────────────┘                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ SEARCH Endpoint Flow

```
START: User enters "Tell me about mehndi"
    │
    ├──→ [1] SPELL CHECK
    │    ├─ Input: "Tell me about mehndi"
    │    ├─ Library: pyspellchecker + symspellpy
    │    └─ Output: "Tell me about mehndi" (no changes)
    │
    ├──→ [2] CACHE LOOKUP (FASTEST PATH!)
    │    ├─ Search: cache_responses["Tell me about mehndi"]
    │    │
    │    ├─ HIT: Found cached response
    │    │   ├─ Return immediately (0.02s)
    │    │   ├─ Include: ai_response, model_used, images
    │    │   └─ Set from_cache = True
    │    │
    │    └─ MISS: Not in cache, continue...
    │
    ├──→ [3] CALL SMART AGENT
    │    │
    │    ├─ TRY: ask_my_model("Tell me about mehndi")
    │    │   ├─ Load: TinyLlama-1.1B + LoRA adapter
    │    │   ├─ Process: Tokenize → Model inference
    │    │   ├─ Generate: max_new_tokens=80
    │    │   ├─ Decode: Convert tokens back to text
    │    │   └─ Output: "Mehndi is a traditional art form..." (351 chars)
    │    │             ✅ Success → Use trained model
    │    │
    │    └─ EXCEPT: ask_my_model() fails
    │        ├─ Fallback: ask_gemini("Tell me about mehndi")
    │        ├─ API call: google-generativeai
    │        ├─ Max tokens: 150
    │        └─ Output: Response from Gemini
    │             ⚠️ Using Gemini (trained model error)
    │
    ├──→ [4] EXTRACT KEYWORDS
    │    ├─ Input: "Tell me about mehndi"
    │    ├─ Check: Is it wedding-related?
    │    ├─ Match: "mehendi" found in keywords_map
    │    └─ Output: ["mehendi ceremony", "haldi ceremony"]
    │
    ├──→ [5] FETCH IMAGES (Parallel)
    │    ├─ Keywords: ["mehendi ceremony", "haldi ceremony"]
    │    ├─ Check: cached_images["mehendi ceremony,haldi ceremony"]
    │    │
    │    ├─ HIT: Found in image cache
    │    │   └─ Return cached images (instant)
    │    │
    │    └─ MISS: Fetch fresh images
    │        ├─ Web search: "mehendi ceremony" images
    │        ├─ Collect: 6 image URLs
    │        ├─ Cache: store in cached_images
    │        └─ Return: URLs list
    │
    ├──→ [6] BUILD RESPONSE OBJECT
    │    ├─ ai_response: "Mehndi is..."
    │    ├─ model_used: "your_trained_model" or "gemini_api"
    │    ├─ search_keywords: ["mehendi ceremony", "haldi ceremony"]
    │    ├─ images: [url1, url2, url3, url4, url5, url6]
    │    └─ from_cache: False
    │
    ├──→ [7] SAVE TO CACHE
    │    ├─ Key: "Tell me about mehndi"
    │    ├─ Value: { ai_response, model_used, search_keywords, images }
    │    └─ MongoDB: cache_responses collection
    │
    ├──→ [8] SAVE TO HISTORY (Background)
    │    ├─ Collection: searches_col
    │    ├─ Store: query, corrected_query, response, keywords, images, timestamp
    │    └─ Non-blocking: Runs in thread pool
    │
    └──→ RETURN: Complete response to frontend
        │
        └─ Frontend renders:
           ├─ AI response text
           ├─ "Used: Your Trained Model" indicator
           ├─ Keywords display
           └─ Image gallery

TOTAL TIME: 
├─ Cache hit: ~0.02s
├─ Fresh search: 9-12s
│  ├─ Spell check: 0.05s
│  ├─ Smart agent: 8-10s (model inference)
│  ├─ Image fetch: 1-2s
│  └─ Cache + return: 0.1s
└─ Max timeout: 20s per request
```

---

## 2️⃣ CHAT Endpoint Flow (With Context)

```
START: User sends message (with history)
    │
    ├──→ [1] SPELL CHECK
    │    └─ Correct user's input
    │
    ├──→ [2] BUILD CONTEXT
    │    ├─ Retrieve: Last 5 messages from history
    │    ├─ Format: 
    │    │   User: "What is mehndi?"
    │    │   Assistant: "Mehndi is an ancient art form..."
    │    │   
    │    │   User: "How long does it take?"
    │    │   Assistant: "Typically 2-4 hours..."
    │    │
    │    └─ Context prepared with chat history
    │
    ├──→ [3] CALL SMART AGENT (With Context)
    │    ├─ Input: Corrected message + context
    │    ├─ smart_agent() processes with history
    │    │
    │    ├─ TRY: ask_my_model(input)
    │    │   ├─ Model is context-aware (due to prompt engineering)
    │    │   └─ Response considers previous messages
    │    │
    │    └─ FALLBACK: ask_gemini(input)
    │        └─ Gemini receives context in system prompt
    │
    ├──→ [4] SAVE TO CONVERSATION HISTORY
    │    ├─ Collection: conversations_col
    │    ├─ Document:
    │    │   {
    │    │     user_id: "user_123",
    │    │     query: "How long does mehndi take?",
    │    │     response: "Typically 2-4 hours...",
    │    │     model_used: "your_trained_model",
    │    │     timestamp: "2026-04-24T10:30:00Z"
    │    │   }
    │    └─ Stored for future context retrieval
    │
    └──→ RETURN: Response to frontend
        │
        └─ Frontend:
           ├─ Display new message
           ├─ Show model indicator
           ├─ Auto-scroll to latest
           └─ Keep history visible
```

---

## 3️⃣ BUDGET Endpoint Flow

```
START: User enters budget data
    │
    ├─→ POST /budget
    │   ├─ Request body:
    │   │   {
    │   │     "total_budget": 500000,
    │   │     "user_id": "user_123"
    │   │   }
    │   │
    │   ├─→ [1] CALCULATE BREAKDOWN
    │   │   ├─ Venue: 500000 × 0.30 = 150,000
    │   │   ├─ Catering: 500000 × 0.35 = 175,000
    │   │   ├─ Decor: 500000 × 0.20 = 100,000
    │   │   ├─ Photography: 500000 × 0.10 = 50,000
    │   │   └─ Music/Entertainment: 500000 × 0.05 = 25,000
    │   │
    │   ├─→ [2] SAVE TO DATABASE
    │   │   ├─ Collection: budgets_col
    │   │   ├─ Document:
    │   │   │   {
    │   │   │     user_id: "user_123",
    │   │   │     total_budget: 500000,
    │   │   │     breakdown: {
    │   │   │       venue: 150000,
    │   │   │       catering: 175000,
    │   │   │       decor: 100000,
    │   │   │       photography: 50000,
    │   │   │       music_entertainment: 25000
    │   │   │     },
    │   │   │     created_at: ISODate(),
    │   │   │     updated_at: ISODate()
    │   │   │   }
    │   │   └─ Persistent storage
    │   │
    │   └─→ [3] RETURN RESPONSE
    │       └─ Return breakdown for display
    │
    ├─→ GET /budget/{user_id}
    │   ├─ Query: budgets_col.find_one({ user_id })
    │   └─ Return: Budget data if exists
    │
    └──→ FRONTEND: Render pie chart + breakdown table
        ├─ Chart.js visualization (30%, 35%, 20%, 10%, 5%)
        ├─ Table with amounts in currency format
        └─ Interactive hover tooltips
```

---

## 4️⃣ CHECKLIST-PDF Endpoint Flow

```
START: User clicks "Download Checklist"
    │
    ├─→ POST /checklist-pdf
    │   │
    │   ├─→ [1] CREATE PDF DOCUMENT (In Memory)
    │   │   ├─ Library: reportlab
    │   │   ├─ Size: Letter (8.5" × 11")
    │   │   ├─ Margins: 0.5 inch all sides
    │   │   └─ Buffer: BytesIO (not saved to disk)
    │   │
    │   ├─→ [2] DEFINE STYLES
    │   │   ├─ Title Style:
    │   │   │   ├─ Font: Cormorant Garamond
    │   │   │   ├─ Size: 24pt
    │   │   │   ├─ Color: Rose (#c9636a)
    │   │   │   └─ Alignment: Center
    │   │   │
    │   │   └─ Heading Style:
    │   │       ├─ Font: DM Sans
    │   │       ├─ Size: 14pt
    │   │       ├─ Color: Gold (#b8974a)
    │   │       └─ Alignment: Left
    │   │
    │   ├─→ [3] PREPARE CONTENT
    │   │   ├─ Title: "🎊 Your 12-Month Wedding Planning Checklist"
    │   │   │
    │   │   ├─ Timeline 1: "12 Months Before"
    │   │   │   ├─ Decide on wedding date
    │   │   │   ├─ Set budget
    │   │   │   ├─ Create guest list
    │   │   │   └─ Book venue
    │   │   │
    │   │   ├─ Timeline 2: "9-10 Months"
    │   │   │   ├─ Book catering
    │   │   │   ├─ Book photographer/videographer
    │   │   │   └─ Select wedding attire
    │   │   │
    │   │   ├─ Timeline 3: "6-8 Months"
    │   │   │   ├─ Send save-the-date
    │   │   │   ├─ Plan honeymoon
    │   │   │   └─ Book wedding planner
    │   │   │
    │   │   ├─ Timeline 4: "3-4 Months"
    │   │   │   ├─ Finalize guest list
    │   │   │   ├─ Order invitations
    │   │   │   ├─ Plan ceremonies
    │   │   │   └─ Book band/DJ
    │   │   │
    │   │   ├─ Timeline 5: "1-2 Months"
    │   │   │   ├─ Final dress fitting
    │   │   │   ├─ Confirm vendor details
    │   │   │   ├─ Plan seating
    │   │   │   └─ Prepare speeches
    │   │   │
    │   │   ├─ Timeline 6: "2 Weeks"
    │   │   │   ├─ Confirm vendor arrivals
    │   │   │   ├─ Final headcount
    │   │   │   ├─ Prepare payment cheques
    │   │   │   └─ Rehearsal dinner
    │   │   │
    │   │   ├─ Timeline 7: "1 Week"
    │   │   │   ├─ Final confirmations
    │   │   │   ├─ Pack for honeymoon
    │   │   │   ├─ Confirm transportation
    │   │   │   └─ Get manicure/pedicure
    │   │   │
    │   │   └─ Timeline 8: "Wedding Day"
    │   │       ├─ Hair and makeup
    │   │       ├─ Eat a good breakfast
    │   │       ├─ Arrive early
    │   │       └─ Enjoy the day! 💍
    │   │
    │   ├─→ [4] BUILD TABLE FOR EACH TIMELINE
    │   │   ├─ Format: Bullet point list
    │   │   ├─ Width: Full page (7 inches)
    │   │   ├─ Font: Helvetica 11pt
    │   │   ├─ Text Color: Dark brown (#3a2a30)
    │   │   ├─ Line spacing: 0.5pt light line between items
    │   │   └─ Color: Rose tint (#e8d9db)
    │   │
    │   ├─→ [5] BUILD PDF DOCUMENT
    │   │   ├─ Combine: Title + Spacer + All timelines
    │   │   ├─ Add spacing: 0.15 inch between sections
    │   │   └─ Compile into PDF
    │   │
    │   ├─→ [6] ENCODE TO BASE64
    │   │   ├─ Read: PDF bytes from buffer
    │   │   ├─ Encode: base64.b64encode()
    │   │   └─ Result: String safe for JSON transmission
    │   │
    │   └─→ [7] RETURN RESPONSE
    │       └─ {
    │           "pdf": "base64-encoded-pdf-string...",
    │           "filename": "wedding-checklist-12-months.pdf"
    │         }
    │
    └──→ FRONTEND: Download PDF
        ├─ Decode base64
        ├─ Create blob
        ├─ Trigger browser download
        └─ File saved to Downloads folder
```

---

## 5️⃣ AI Model Selection Logic

```
DECISION TREE: Which AI Model to Use?
=====================================

START: smart_agent(user_input)
    │
    ├─→ TRY: Load & use Trained Model
    │   │
    │   ├─ Is model loaded?
    │   │  ├─ YES: Continue
    │   │  └─ NO: Skip to Fallback
    │   │
    │   ├─ Generate response with trained model
    │   │  ├─ Tokenize input
    │   │  ├─ Forward pass through model
    │   │  ├─ Generate tokens (max 80)
    │   │  └─ Decode to text
    │   │
    │   ├─ Check: Is response non-empty?
    │   │  ├─ YES: ✅ Return trained model response
    │   │  │        └─ model_used: "your_trained_model"
    │   │  │
    │   │  └─ NO: Continue to Fallback
    │   │
    │   └─ CATCH: Exception during inference?
    │       └─ YES: Continue to Fallback
    │
    ├─→ FALLBACK: Use Gemini API
    │   │
    │   ├─ Setup: Google Generative AI client
    │   ├─ Model: Gemini 1.5 Flash
    │   ├─ System prompt: "You are a wedding planning assistant..."
    │   ├─ Max tokens: 150
    │   ├─ Temperature: 0.7
    │   ├─ Timeout: 8 seconds
    │   │
    │   ├─ Generate response from Gemini
    │   │
    │   └─ ⚠️ Return Gemini response
    │       └─ model_used: "gemini_api"
    │
    └─→ EXTRACT KEYWORDS & RETURN
        ├─ Search keywords for image fetching
        └─ Complete response object
```

---

## 6️⃣ Caching Strategy (Performance Optimization)

```
CACHING LAYERS:
==============

Layer 1: RESPONSE CACHE (Fastest)
├─ Type: MongoDB collection (cache_responses)
├─ Key: Query text
├─ Value: { ai_response, model_used, search_keywords, images }
├─ Hit Rate: Depends on query repetition
├─ Speed: 0.02 seconds
├─ Use Case: Same query asked multiple times
│
└─ Example:
   Query: "Tell me about mehndi"
   ├─ First time: 9.12s (fresh search)
   └─ Second time: 0.02s (cache hit)

Layer 2: IMAGE CACHE
├─ Type: MongoDB collection (cached_images)
├─ Key: Keywords joined with comma
├─ Value: [url1, url2, url3, url4, url5, url6]
├─ Speed: Instant lookup
├─ Use Case: Avoid redundant image searches
│
└─ Example:
   Keywords: ["mehndi ceremony", "haldi ceremony"]
   ├─ First request: Fetch from web (1-2s)
   └─ Later requests: Use cached URLs (0s)

Layer 3: THREAD POOL EXECUTOR
├─ Type: In-memory worker pool
├─ Workers: 3 threads
├─ Tasks: CPU-bound operations
│  ├─ Model inference (trained model)
│  ├─ Spell checking
│  └─ Image fetching
├─ Benefit: Parallel processing
│
└─ Flow:
   ┌─────────────────────────────┐
   │ Main Event Loop (Async)     │
   ├─────────────────────────────┤
   │ Task 1: Spell check         │
   │ Task 2: Smart agent         │  ← Run in parallel
   │ Task 3: Image fetch         │
   └─────────────────────────────┘

CACHE INVALIDATION:
===================
├─ Responses: No auto-invalidation (permanent cache)
├─ Images: No auto-invalidation (permanent cache)
├─ When to clear:
│  ├─ Manual: Delete from MongoDB
│  ├─ Seasonal: Clear old entries quarterly
│  └─ On error: Automatically retry on cache miss

MEMORY OPTIMIZATION:
====================
├─ Model: Loaded once at startup
├─ Tokenizer: Cached after first use
├─ Embeddings: Reused across requests
└─ Result: Subsequent requests are 100x faster
```

---

## 7️⃣ Error Handling & Fallback Flow

```
ERROR HANDLING STRATEGY:
======================

Level 1: Model Loading (Startup)
├─ TRY: Load TinyLlama + LoRA adapter
├─ EXCEPT: Protobuf version mismatch
│   ├─ Log: "❌ Could not load trained model"
│   ├─ Action: Set _model = None
│   └─ Fallback: Will use Gemini API for all requests
│
└─ EXCEPT: Model not found
    ├─ Log: "ERROR: Model path does not exist"
    └─ Action: Skip model loading

Level 2: Request Handling (Runtime)
├─ TRY: Process /search request
├─ TIMEOUT: If request takes > 20 seconds
│   ├─ Return: "Request took too long. Please try again."
│   ├─ model_used: "timeout"
│   └─ from_cache: false
│
├─ TIMEOUT: Image fetch takes > 10 seconds
│   ├─ Skip: Image fetching
│   ├─ Return: Empty images array []
│   └─ Continue: With AI response only
│
└─ EXCEPT: Spell check fails
    └─ Use: Original query (no correction)

Level 3: Database Operations
├─ Connection error:
│   ├─ Silently skip: Cache save (request still succeeds)
│   ├─ Return: Valid response without cache
│   └─ Log: Error for debugging
│
└─ Query error:
    ├─ Return: Default value (empty list/None)
    └─ Continue: With request processing

Level 4: AI Model Inference
├─ TRY: Trained model response
├─ FAIL: Empty response or error
│   ├─ Log: "⚠️ Trained model failed, using Gemini API"
│   ├─ TRY: Gemini API
│   └─ FAIL: Return generic message
│        └─ Response: "Unable to generate response."
│
└─ Timeout: 8 seconds per API call

GRACEFUL DEGRADATION:
====================
Cache hit → Trained model → Gemini API → Default response
  (0.02s)      (9-12s)         (1-2s)       (instant)

User always gets SOMETHING, never a blank error.
```

---

## 📊 Response Time Breakdown

```
TYPICAL REQUEST TIMELINE:
========================

Fresh Search Request (First Time):
  0ms    ├─ Receive request from frontend
  50ms   ├─ Spell check (pyspellchecker)
  60ms   ├─ Cache lookup → MISS
         │
  100ms  ├─ Smart agent starts
         │
  8500ms ├─ Trained model inference (TinyLlama)
         │  ├─ Tokenization: 50ms
         │  ├─ Model forward pass: 8000ms (CPU)
         │  ├─ Token generation: 400ms
         │  └─ Decoding: 50ms
         │
  8600ms ├─ Image keyword extraction (instant)
         │
  8700ms ├─ Image fetching starts (parallel)
  10200ms├─ Image fetch completes (~1500ms)
         │
  10300ms├─ Response caching (MongoDB) ~100ms
         │
  10400ms└─ Return to frontend
         
TOTAL: ~10.4 seconds for fresh search

Cached Search Request (Repeat Query):
  0ms    ├─ Receive request from frontend
  50ms   ├─ Spell check
  52ms   ├─ Cache lookup → HIT ✓
  100ms  └─ Return cached response
         
TOTAL: ~0.1 seconds (100x faster!)

Budget Request:
  0ms    ├─ Receive budget data
  50ms   ├─ Validate input
  100ms  ├─ Calculate breakdown (5 operations)
  200ms  ├─ Save to MongoDB
  250ms  └─ Return response
  
TOTAL: ~0.25 seconds

PDF Generation Request:
  0ms    ├─ Receive request
  200ms  ├─ Create PDF document
  300ms  ├─ Add all 8 timeline sections
  400ms  ├─ Style and format
  500ms  ├─ Encode to base64
  550ms  └─ Return response
  
TOTAL: ~0.55 seconds
```

---

## 🔐 Data Flow with Security

```
SECURITY CONSIDERATIONS:
=======================

Frontend → Backend:
├─ HTTPS: ✓ (in production)
├─ CORS: Allowed all origins (in development)
├─ Input: Validated by Pydantic models
└─ SQL Injection: Not applicable (MongoDB)

Backend → Database:
├─ Connection: Encrypted (MongoDB Atlas TLS)
├─ Authentication: Username + password
├─ Data: Stored as JSON documents
└─ Backup: MongoDB automatic daily backups

Backend → External APIs:
├─ Gemini API: Uses API key from .env
├─ Image Search: Public APIs (no authentication)
└─ All: Timeout protection (8-20 seconds)

User Data Privacy:
├─ Budget data: Stored per user_id
├─ Chat history: Stored per user_id
├─ Search history: Grouped by query (not user-specific yet)
└─ PII: No personal information stored
```

---

