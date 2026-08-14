# 🐍 Before You Throw It Away — FastAPI Backend

FastAPI application providing object detection and analysis endpoints powered by **RF-DETR (Real-Time Detection Transformer)** and **Multimodal Vision AI**.

---

## ⚙️ Requirements & Environment Setup

### 1. Create a Python Virtual Environment
Navigate to the `backend` folder and create a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Default Configuration:
```env
FRONTEND_URL=http://localhost:5173,http://localhost:5174
AI_MODE=real
RFDETR_MODEL=rtdetr-l.pt
HIGH_CONFIDENCE_THRESHOLD=0.80
LOW_CONFIDENCE_THRESHOLD=0.50
MAX_UPLOAD_SIZE_MB=10

LLM_MODE=real
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
LLM_TIMEOUT_SECONDS=30
```

---

## 🚀 Running the FastAPI Server

Start the development server with auto-reload:
```bash
uvicorn app.main:app --reload --port 8000
```

### Interactive API Documentation (Swagger / OpenAPI):
Open your browser and navigate to:
- **Swagger Docs:** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/api/health`

---

## 🤖 How RF-DETR & Hybrid Vision AI Work
1. **RF-DETR Model Loading**: On startup, `RTDETR('rtdetr-l.pt')` is loaded into memory **once** as a pre-initialized singleton to serve fast object detection without per-request latency.
2. **Quality Pre-Checker**: Evaluates resolution, file size, extreme dark/glare lighting, and blurriness.
3. **Confidence Evaluation**:
   - `Confidence >= 0.80`: Accepted directly as RF-DETR high confidence detection.
   - `0.50 <= Confidence < 0.80`: Triggers Multimodal Vision AI verification (Gemini 1.5 / OpenAI Vision).
   - `Confidence < 0.50`: Handled as uncertain object safeguard.

---

## 🧪 Running Automated Tests
```bash
pytest
```
Runs 25 automated unit and endpoint tests.
