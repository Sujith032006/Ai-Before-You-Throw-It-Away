# ♻️ Before You Throw It Away — AI Reuse Assistant

An AI-powered web application that helps users discover creative ways to upcycle and reuse household items before throwing them away.

## 🚀 Project Status: COMPLETE ANALYZER MIGRATION & FULL HYBRID SYSTEM

### Feature Architecture:
- **FRONTEND & INTERACTION:** React 19 + TypeScript + Vite + Tailwind CSS with camera & image upload scanner.
- **RF-DETR & HYBRID VISION AI ANALYZER:** Real-time object detection endpoint (`POST /api/analyze` & `POST /api/scan`) using RF-DETR Transformer (`rtdetr-l.pt`) as the primary detector, with Multimodal Vision AI fallback (Gemini 1.5 Flash / OpenAI Vision) for low confidence or obscure objects.
- **IMAGE QUALITY PRE-CHECKER:** Evaluates file size, minimum resolution, extreme dark/glare lighting, and blurriness with actionable recommendations.
- **REUSE KNOWLEDGE BASE & RECOMMENDATION ENGINE:** Scoring algorithm (`POST /api/recommendations`) matching goal, tools, materials, budget, time, and difficulty.
- **GENERATIVE AI & PERSONALIZED GUIDE & AI ASSISTANT:** Structured guide generation (`POST /api/projects/personalized-guide`) and context-aware chat assistant (`POST /api/chat`).
- **PERSISTENCE, DASHBOARD & HISTORY:** SQLAlchemy ORM models tracking scans, project completion, history logs, and environmental impact meters.

---

## 🔒 Security & Data Flow Strategy
- **API Key Security**: `LLM_API_KEY` is loaded strictly on the backend (`backend/.env`). It is never sent to the browser or committed to Git.
- **Database Non-Blocking Persistence**: All database operations are wrapped in try/except blocks. If the database is offline or uninitialized, core scanning and AI operations continue without crashing.
- **CORS Configuration**: Controlled origins via `FRONTEND_URL` environment variable.

---

## 🛠️ Technology Stack
- **Frontend:** React 19 + TypeScript, Vite, Tailwind CSS v4, Lucide React, React Router v7
- **Backend:** FastAPI (Python 3.11), SQLAlchemy v2, Pydantic v2, Pillow, Ultralytics RF-DETR (`rtdetr-l.pt`), HTTPX Async Client, Pytest

---

## 🏃 How to Run the Application

### 1. Run Backend Server:
```bash
cd backend
# Activate virtual environment
.\.venv\Scripts\activate
# Start FastAPI server (Initializes DB automatically)
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Run Frontend Application:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173/`** in your browser.

---

## 🧪 Running Automated Tests
```bash
cd backend
.\.venv\Scripts\python -m pytest
```
All 25 backend unit tests run cleanly.

---

## 🎬 End-to-End Demo Flow

1. Open **`http://localhost:5173/`**.
2. Click **"Scan an Item"**.
3. Upload or capture a bottle photo.
4. RF-DETR Transformer detects **Plastic Bottle (94%)**.
5. Click **"✓ Yes, that's correct"**.
6. Select preferences: Goal: *Gardening*, Tools: *Scissors*, Materials: *Soil*, Budget: *₹50*, Difficulty: *Easy*, Time: *30 minutes*.
7. Click **"Find Reuse Ideas"**.
8. View ranked match: **Self-Watering Planter (95% Match)**.
9. Click **"✨ Create Personalized Guide"**.
10. AI generates step-by-step instructions.
11. Click **"Ask AI Assistant"**.
12. Ask: *"I don't have cotton."* -> AI responds with cotton T-shirt wick substitution.
13. Click **"Mark Project Complete 🎉"**.
14. View updated impact stats on **Dashboard** and **History**.
