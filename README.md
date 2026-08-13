# ♻️ Before You Throw It Away — AI Reuse Assistant

An AI-powered web application that helps users discover creative ways to upcycle and reuse household items before throwing them away.

## 🚀 Project Status: STAGE 6 COMPLETED (FINAL INTEGRATION, DATABASE, DASHBOARD, TESTING & DEPLOYMENT)

### Completed Stages:
- **STAGE 1 — Frontend Foundation & Navigation Prototype:** React 19 + TypeScript + Vite + Tailwind CSS navigation prototype.
- **STAGE 2 — Image Upload + Camera Scanning:** Live webcam stream with `navigator.mediaDevices` API and fallback file upload.
- **STAGE 3 — FastAPI + YOLO Object Detection:** Real-time computer vision object detection endpoint (`POST /api/scan`) using Ultralytics YOLOv11 (`yolo11n.pt`).
- **STAGE 4 — Reuse Knowledge Base & Recommendation Engine:** Deterministic scoring algorithm (`POST /api/recommendations`) matching goal, tools, materials, budget, time, and difficulty.
- **STAGE 5 — Generative AI + Personalized Guide + AI Assistant:** LLM provider abstraction (OpenAI, Gemini, Mock mode), structured guide generation (`POST /api/projects/personalized-guide`), and context-aware chat assistant (`POST /api/chat`).
- **STAGE 6 — Database Persistence, User Dashboard, Project Completion & Deployment:**
  - SQLAlchemy ORM models: `User`, `Scan`, `Detection`, `Recommendation`, `SelectedProject`, `PersonalizedGuide`, `ProjectCompletion`, `ChatSession`, `ChatMessage`.
  - Flexible PostgreSQL database connection via `DATABASE_URL` with automatic SQLite (`sqlite:///./sql_app.db`) fallback.
  - User Dashboard (`/dashboard`) displaying total scans, projects created, completed projects, and recent activity timeline.
  - Scan History (`/history`) displaying past scans, status badges (`Completed`, `In Progress`), and match scores.
  - Project Completion (`POST /api/projects/{id}/complete`) tracking completed DIY upcycles.
  - 21 automated backend Pytest tests covering all API endpoints and end-to-end integration flow.

---

## 🔒 Security & Data Flow Strategy
- **API Key Security**: `LLM_API_KEY` is loaded strictly on the backend (`backend/.env`). It is never sent to the browser or committed to Git.
- **Database Non-Blocking Persistence**: All database operations are wrapped in try/except blocks. If the database is offline or uninitialized, core scanning and AI operations continue without crashing.
- **CORS Configuration**: Controlled origins via `FRONTEND_URL` environment variable.

---

## 🛠️ Technology Stack
- **Frontend:** React 19 + TypeScript, Vite, Tailwind CSS v4, Lucide React, React Router v7
- **Backend:** FastAPI (Python 3.11), SQLAlchemy v2, Alembic, Pydantic v2, Pillow, Ultralytics YOLOv11, HTTPX Async Client, Pytest

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
All 21 backend unit tests run using offline mock mode without requiring an active LLM API key.

---

## 🎬 19-Step End-to-End Demo Script

1. Open **`http://localhost:5173/`**.
2. Click **"Scan an Item"**.
3. Upload or capture a bottle image.
4. YOLO detects **Bottle (94%)**.
5. Click **"✓ Yes, that's correct"**.
6. Select preferences: Goal: *Gardening*, Tools: *Scissors*, Materials: *Soil*, Budget: *₹50*, Difficulty: *Easy*, Time: *30 minutes*.
7. Click **"Find Reuse Ideas"**.
8. View ranked match: **Self-Watering Planter (95% Match)**.
9. Click **"Show Me How"** or **"✨ Create Personalized Guide"**.
10. AI generates step-by-step instructions.
11. Click **"Ask AI Assistant"**.
12. Ask: *"I don't have cotton."* -> AI responds with cotton T-shirt wick substitution.
13. Navigate through project steps.
14. Click **"Mark Project Complete 🎉"**.
15. Click **"View Dashboard"**.
16. View updated impact stats: **Items Scanned: 1**, **Projects Created: 1**, **Completed: 1**.
17. Click **"View History"**.
18. View scan item with green **"Completed"** badge.
19. Click item to reopen project details.
