# 🐍 Before You Throw It Away — FastAPI Backend

FastAPI application providing computer vision object detection endpoints powered by Ultralytics YOLO.

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
YOLO_MODEL=yolo11n.pt
YOLO_CONFIDENCE_THRESHOLD=0.40
MAX_UPLOAD_SIZE_MB=5
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

## 🤖 How YOLO Model Download & Loading Works
1. On the very first run (when `AI_MODE=real`), Ultralytics automatically downloads the lightweight `yolo11n.pt` model weights (~6 MB) if not already present.
2. The model is loaded into memory **once** when the detector initializes.
3. Every `POST /api/scan` request reuses this instance without re-downloading or re-loading weights.

---

## 🧪 Running Automated Tests
```bash
pytest
```
