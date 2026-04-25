# 🎊 Wedding AI Planner - Complete Documentation

A full-stack AI-powered wedding planning assistant that helps users find wedding ideas, plan budgets, manage checklists, and chat with an intelligent bot.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack & Libraries](#tech-stack--libraries)
4. [System Workflow](#system-workflow)
5. [API Endpoints](#api-endpoints)
6. [Features](#features)
7. [Installation & Setup](#installation--setup)
8. [Project Structure](#project-structure)
9. [Trained Model vs Gemini API](#trained-model-vs-gemini-api)
10. [Database Schema](#database-schema)

---

## 🎯 Project Overview

**Wedding AI Planner** is an intelligent web application that assists users in planning their weddings. It combines:
- **AI-Powered Responses** (Trained Model + Gemini API fallback)
- **Smart Search** with spell-checking
- **Image Suggestions** for wedding inspiration
- **Budget Calculator** with automatic breakdown
- **12-Month Checklist PDF** generator
- **Chatbot** with conversation history
- **Caching System** for fast response times

### Key Goals
✅ Provide instant wedding planning guidance  
✅ Personalize recommendations based on budget  
✅ Maintain conversation context for better responses  
✅ Generate downloadable planning documents  
✅ Cache responses for sub-second retrieval  

---

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (HTML/CSS/JS)                   │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐
│  │ Search Tab   │ Budget Tab   │ Checklist    │ Chat Tab     │
│  └──────────────┴──────────────┴──────────────┴──────────────┘
└──────────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌──────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Python)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ API Routes  │  │ AI Agent    │  │ Database Handler     │ │
│  │ /search     │  │ (smart_    │  │ (MongoDB)           │ │
│  │ /chat       │  │  agent)    │  │                      │ │
│  │ /budget     │  │            │  │  - Caching          │ │
│  │ /checklist  │  │  Uses:     │  │  - History          │ │
│  │             │  │  • Trained │  │  - Budgets          │ │
│  │             │  │    Model   │  │  - Conversations    │ │
│  │             │  │  • Gemini  │  │                      │ │
│  │             │  │    API     │  │                      │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘
│  ┌──────────────────────────────────────────────────────────┐
│  │  Support Modules                                          │
│  │  ├─ spell_checker.py (pyspellchecker/symspellpy)         │
│  │  ├─ image_handler.py (web image search)                  │
│  │  ├─ agent.py (model loading & inference)                 │
│  │  └─ video_handler.py (optional video support)            │
│  └──────────────────────────────────────────────────────────┘
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│              MONGODB (Cloud/Local Database)                  │
│  ├─ searches_col ────── Search history + AI responses        │
│  ├─ cache_responses ─── Cached AI responses for fast lookup  │
│  ├─ cached_images ───── Cached image sets by keywords        │
│  ├─ budgets_col ─────── User budgets & breakdowns            │
│  └─ conversations_col ─ Chat history per user                │
└──────────────────────────────────────────────────────────────┘
```

### Component Details

#### **Frontend Layer**
- **HTML/CSS/JavaScript** - Responsive web interface
- **Tabs** - Search, Budget, Checklist, Chat modes
- **Web Speech API** - Voice input support
- **Chart.js** - Budget visualization

#### **Backend Layer**
- **FastAPI** - Fast, async Python web framework
- **Agent Module** - AI response generation
- **Database Handler** - MongoDB CRUD operations
- **Support Modules** - Spell checking, image search, etc.

#### **Data Layer**
- **MongoDB** - Document storage for history, cache, budgets
- **In-Memory Cache** - Quick response retrieval

---

## 🛠️ Tech Stack & Libraries

### Backend Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | Latest | Web server & REST API routing |
| **Uvicorn** | Latest | ASGI server to run FastAPI |
| **Pydantic** | Latest | Data validation & request schemas |

### AI/ML Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **transformers** | Latest | Load pretrained LLMs (HuggingFace models) |
| **peft** | Latest | Parameter-Efficient Fine-Tuning (LoRA adapters) |
| **torch** | Latest | Deep learning framework for model inference |
| **sentence-transformers** | Latest | Semantic embeddings for similarity search |
| **datasets** | Latest | Dataset handling & preprocessing |
| **accelerate** | Latest | Model training optimization |

### NLP & Text Processing

| Library | Purpose |
|---------|---------|
| **pyspellchecker** | Basic spell correction |
| **symspellpy** | Fast fuzzy spell correction |
| **google-generativeai** | Gemini API for fallback responses |

### Data & Storage

| Library | Purpose |
|---------|---------|
| **pymongo** | MongoDB Python driver |
| **pymysql** | MySQL support (optional) |

### Document Generation

| Library | Purpose |
|---------|---------|
| **reportlab** | Generate styled PDF documents (checklist) |

### Utilities

| Library | Purpose |
|---------|---------|
| **Pillow** | Image processing |
| **python-dotenv** | Environment variable management |
| **httpx** | Async HTTP client |
| **python-multipart** | Multipart form data parsing |
| **requests** | HTTP requests library |
| **ollama** | Local LLM support (optional) |

### Frontend Libraries

| Library | Purpose |
|---------|---------|
| **Chart.js** | Budget pie chart visualization |
| **Web Speech API** | Browser voice input (native) |

---

## 🔄 System Workflow

### 1️⃣ **Search Flow** (Most Common)
```
User enters query
        ↓
[Spell Correction] → Corrected text
        ↓
[Cache Check] → If found, return cached response (0.02s)
        ↓
[If not cached] → Continue...
        ↓
[Smart Agent] → Try Trained Model First
        ├─ ✅ Success → Use trained model response
        └─ ❌ Fail → Fallback to Gemini API
        ↓
[Extract Keywords] → Get wedding-related search terms
        ↓
[Image Search] → Fetch images for those keywords
        ↓
[Cache Response] → Store for future use
        ↓
[Return Response] ← AI response + Images + Keywords
```

### 2️⃣ **Chat Flow** (Contextual)
```
User sends message
        ↓
[Spell Check] → Correct typos
        ↓
[Build Context] → Include last 5 messages from history
        ↓
[Smart Agent] → Process with conversation context
        ├─ Trained Model (with context)
        └─ Gemini API (fallback)
        ↓
[Save to History] → Store in MongoDB
        ↓
[Return Response] ← With model used indicator
```

### 3️⃣ **Budget Calculator Flow**
```
User enters total budget + User ID
        ↓
[Calculate Breakdown]
├─ Venue: 30% of total
├─ Catering: 35% of total
├─ Decor: 20% of total
├─ Photography: 10% of total
└─ Music/Entertainment: 5% of total
        ↓
[Save to MongoDB] → budgets_col
        ↓
[Display Pie Chart] → Frontend Chart.js
```

### 4️⃣ **PDF Checklist Flow**
```
User clicks "Download Checklist"
        ↓
[Generate PDF in Memory]
├─ Title: "12-Month Wedding Planning Checklist"
├─ 8 Timeline Sections (12 months → Wedding day)
├─ Tasks for each section
└─ Styled with wedding colors (Rose/Gold)
        ↓
[Encode to Base64] → Safe for transmission
        ↓
[Return to Frontend] → Browser downloads PDF
```

---

## 📡 API Endpoints

### Base URL
```
http://127.0.0.1:8000
```

### **1. SEARCH** - Get AI response with images
```
POST /search
Request:
{
  "query": "Tell me about mehndi ceremony"
}

Response:
{
  "original_query": "Tell me about mehndi ceremony",
  "spell_check": {
    "corrected": "Tell me about mehndi ceremony",
    "corrections_made": 0
  },
  "ai_response": "Mehndi is an ancient art form...",
  "model_used": "your_trained_model",  // or "gemini_api"
  "search_keywords": ["mehendi ceremony", "haldi ceremony"],
  "images": ["url1", "url2", "url3"],
  "from_cache": false
}
```

### **2. SPELL-CHECK** - Check & correct spelling
```
POST /spell-check
Request:
{
  "text": "tell me abot weding"
}

Response:
{
  "original": "tell me abot weding",
  "corrected": "tell me about wedding",
  "corrections_made": 2,
  "corrections": {"abot": "about", "weding": "wedding"}
}
```

### **3. BUDGET** - Calculate & save budget
```
POST /budget
Request:
{
  "total_budget": 500000,
  "user_id": "user_123"
}

Response:
{
  "total_budget": 500000,
  "breakdown": {
    "venue": 150000,
    "catering": 175000,
    "decor": 100000,
    "photography": 50000,
    "music_entertainment": 25000
  }
}

GET /budget/{user_id}
Response: (Same as above)
```

### **4. CHECKLIST PDF** - Generate 12-month checklist
```
POST /checklist-pdf
Request: (No body needed)

Response:
{
  "pdf": "base64-encoded-pdf-string...",
  "filename": "wedding-checklist-12-months.pdf"
}
```

### **5. CHAT** - Conversational AI with history
```
POST /chat
Request:
{
  "user_id": "user_123",
  "query": "What should I wear to mehndi?",
  "history": [
    {
      "query": "What is mehndi?",
      "response": "Mehndi is an ancient art form..."
    }
  ]
}

Response:
{
  "query": "What should I wear to mehndi?",
  "response": "For mehndi, wear...",
  "model_used": "your_trained_model",
  "search_keywords": ["mehndi ceremony"]
}
```

### **6. HISTORY** - Get recent searches
```
GET /history
Response:
[
  {
    "query": "Tell me about sangeet",
    "response": "Sangeet is...",
    "timestamp": "2026-04-24T10:30:00"
  },
  ...
]
```

### **7. HEALTH** - System status
```
GET /health
Response:
{
  "status": "running",
  "model": "TinyLlama LoRA fine-tuned + Gemini fallback",
  "cache": "MongoDB",
  "optimizations": "Parallel image fetching, greedy decoding"
}
```

---

## ✨ Features

### 🔍 **Smart Search**
- Spell correction in real-time
- Wedding-specific keyword extraction
- Image suggestions based on query
- Response caching for instant retrieval
- Fallback to Gemini if trained model fails

### 🤖 **AI Models**
- **Primary**: TinyLlama-1.1B fine-tuned with LoRA
- **Fallback**: Google Gemini 1.5 Flash API
- Support for conversation history (last 5 messages)

### 💰 **Budget Calculator**
- Automatic category breakdown (5 categories)
- Percentage-based distribution
- MongoDB persistence per user
- Pie chart visualization
- Export-ready data

### 📋 **PDF Checklist**
- 12-month wedding planning timeline
- 8 distinct phases (from 12 months before → wedding day)
- Professional styling with wedding colors
- Downloadable directly from browser
- No server file storage needed

### 💬 **Chatbot**
- Multi-turn conversation support
- Context awareness (remembers last 5 messages)
- Conversation history storage
- Per-user sessions

### 🎤 **Voice Input**
- Web Speech API integration
- Real-time transcription
- Visual feedback (pulsing mic button)
- Automatic search trigger
- Cross-browser support

### ⚡ **Performance Optimizations**
- MongoDB caching for responses
- Parallel image fetching
- Thread pool executor (3 workers)
- Greedy decoding for faster inference
- Reduced token generation (80 tokens)
- Cached embeddings

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- MongoDB (local or cloud - Atlas)
- Google Generative AI API key (optional)
- Node.js (optional, only if modifying frontend build)

### Step 1: Clone Repository
```bash
cd wedding-ai-agent
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Environment Setup
Create `.env` file in `backend/` directory:
```bash
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/wedding_ai?retryWrites=true&w=majority

# Google Gemini API (optional fallback)
GEMINI_API_KEY=your-api-key-here

# Local model paths (already included)
# TRAINED_MODEL_PATH=../models/wedding_model
```

### Step 5: Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 6: Open Frontend
Open in browser:
```
http://127.0.0.1:8000/
```

Or navigate to `frontend/index.html` (served via FastAPI static files).

---

## 📁 Project Structure

```
wedding-ai-agent/
├── frontend/
│   ├── index.html           # Main web interface
│   ├── style.css            # Wedding-themed styling
│   └── app.js               # JavaScript logic (search, chat, budget)
│
├── backend/
│   ├── main.py              # FastAPI routes & endpoints
│   ├── agent.py             # AI model loading & inference
│   │   ├─ load_my_model()       → Load TinyLlama + LoRA
│   │   ├─ ask_my_model()        → Generate response (trained model)
│   │   ├─ ask_gemini()          → Fallback to Gemini API
│   │   └─ smart_agent()         → Decision logic
│   │
│   ├── spell_checker.py     # Spell correction
│   ├── image_handler.py     # Image search & fetch
│   ├── video_handler.py     # Video support (optional)
│   │
│   ├── db/
│   │   └── mongo_handler.py # MongoDB operations
│   │       ├─ save_search()
│   │       ├─ cache_response()
│   │       ├─ save_budget()
│   │       ├─ save_conversation()
│   │       └─ [7 more functions]
│   │
│   ├── training/
│   │   ├── train_wedding.py     # Model fine-tuning script
│   │   ├── test_model.py        # Model testing
│   │   └── train.py
│   │
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
│
├── models/
│   └── wedding_model/        # Fine-tuned TinyLlama LoRA adapter
│       ├── adapter_config.json
│       ├── adapter_model.bin
│       ├── tokenizer.model
│       └── special_tokens_map.json
│
├── README.md                 # This file
└── FEATURES.md              # New features documentation
```

---

## 🧠 Trained Model vs Gemini API

### **Trained Model** (Primary)
```
Model: TinyLlama-1.1B (1.1 Billion parameters)
Fine-tuned with: LoRA (Low-Rank Adaptation)
Dataset: Wedding-specific Q&A pairs
Location: models/wedding_model/
Runtime: Local (CPU/GPU)
```

**When Used:**
- Always tried first for every query
- Responses are cached for repeat queries
- Provides domain-specific answers

**When It Fails:**
```python
# agent.py - load_my_model()
try:
    # Load model
except Exception as e:
    print("❌ Could not load trained model")
    print("Will use Gemini API as fallback")
```

### **Gemini API** (Fallback)
```
Model: Google Gemini 1.5 Flash
API: google.generativeai
Max Tokens: 150
Temperature: 0.7
Timeout: 8 seconds
```

**When Used:**
- Trained model loading fails (protobuf/dependency issues)
- Trained model returns empty response
- As contextual fallback in chat

**Decision Flow in Code:**
```python
def smart_agent(user_input):
    # Try YOUR trained model first
    my_answer = ask_my_model(user_input)
    
    if my_answer:  # If trained model returned response
        return {"model_used": "your_trained_model", "response": my_answer}
    else:  # Fallback to Gemini
        response = ask_gemini(user_input)
        return {"model_used": "gemini_api", "response": response}
```

---

## 💾 Database Schema

### **MongoDB Collections**

#### 1. **searches_col** - Search History
```javascript
{
  "_id": ObjectId(),
  "original_query": "Tell me about mehndi",
  "corrected_query": "Tell me about mehndi",
  "response": "Mehndi is an ancient art...",
  "model_used": "your_trained_model",
  "search_keywords": ["mehendi ceremony", "haldi ceremony"],
  "images": ["url1", "url2"],
  "timestamp": ISODate("2026-04-24T10:30:00Z")
}
```

#### 2. **cache_responses** - Response Cache (Fast Lookup)
```javascript
{
  "_id": "Tell me about mehndi",  // Query is the key
  "ai_response": "Mehndi is...",
  "model_used": "your_trained_model",
  "search_keywords": ["mehendi", "haldi"],
  "images": ["url1", "url2"],
  "cached_at": ISODate("2026-04-24T10:30:00Z"),
  "access_count": 5
}
```

#### 3. **cached_images** - Image Cache
```javascript
{
  "_id": "mehendi ceremony,haldi ceremony",  // Keywords joined
  "images": ["url1", "url2", "url3"],
  "cached_at": ISODate(),
  "access_count": 12
}
```

#### 4. **budgets_col** - User Budgets
```javascript
{
  "_id": ObjectId(),
  "user_id": "user_123",
  "total_budget": 500000,
  "breakdown": {
    "venue": 150000,
    "catering": 175000,
    "decor": 100000,
    "photography": 50000,
    "music_entertainment": 25000
  },
  "created_at": ISODate(),
  "updated_at": ISODate()
}
```

#### 5. **conversations_col** - Chat History
```javascript
{
  "_id": ObjectId(),
  "user_id": "user_123",
  "query": "What is mehndi?",
  "response": "Mehndi is an ancient art...",
  "model_used": "your_trained_model",
  "timestamp": ISODate("2026-04-24T10:30:00Z")
}
```

#### 6. **searches_col** (Indexed)
```javascript
// Index on corrected_query for fast cache lookup
db.cache_responses.createIndex({ "_id": 1 })
db.cached_images.createIndex({ "_id": 1 })
```

---

## 🔧 Development Commands

### Start Development Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Run Tests
```bash
cd backend/training
python test_model.py
```

### Train/Fine-tune Model
```bash
cd backend/training
python train_wedding.py
```

### Check Health
```bash
curl http://127.0.0.1:8000/health
```

### View API Docs
```
http://127.0.0.1:8000/docs          # Swagger UI
http://127.0.0.1:8000/redoc         # ReDoc UI
```

---

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'reportlab'"
**Solution:**
```bash
pip install reportlab
```

### Issue: "Could not load trained model: Protobuf version error"
**Solution:**
```bash
pip install tensorflow==2.15.1
```
The app will automatically fallback to Gemini API.

### Issue: MongoDB Connection Error
**Solution:**
- Check `.env` has correct `MONGO_URI`
- Verify IP whitelist in MongoDB Atlas
- Ensure VPN is off if required

### Issue: Slow responses (>10 seconds)
**Solution:**
- Check cache hit rate: Look for "Cache hit" in logs
- Verify trained model loaded: Look for "✅ Your trained model is ready!"
- Use Gemini API mode if model issues persist

---

## 📊 Performance Metrics

| Operation | Target | Achieved |
|-----------|--------|----------|
| Cache Hit | <0.1s | ✅ 0.02s |
| New Search | <20s | ✅ 9-12s |
| PDF Generation | <2s | ✅ 0.5s |
| Spell Check | <0.1s | ✅ 0.05s |
| Budget Calc | <1s | ✅ 0.1s |

---

## 🤝 Contributing

To extend this project:

1. **Add New Endpoint**: Edit `backend/main.py`
2. **Update Database**: Modify `backend/db/mongo_handler.py`
3. **Improve UI**: Edit `frontend/index.html` and `frontend/style.css`
4. **Fine-tune Model**: Use `backend/training/train_wedding.py`

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Yatin Singh**  
Internship Task - Wedding AI Agent  
2026-04-24

---

## 🎯 Quick Reference

**Start Server:**
```bash
python -m uvicorn main:app --reload --port 8000
```

**Test Endpoints:**
```bash
# Search
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about mehndi"}'

# Budget
curl -X POST http://127.0.0.1:8000/budget \
  -H "Content-Type: application/json" \
  -d '{"total_budget": 500000, "user_id": "user1"}'

# PDF
curl -X POST http://127.0.0.1:8000/checklist-pdf
```

**Monitor Logs:**
```bash
# Watch for model usage
grep "model_used\|Using\|Fallback" backend.log
```

