import os
from dotenv import load_dotenv

load_dotenv()

FRONTEND_URLS = [
    url.strip() for url in os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:5174").split(",")
]
AI_MODE = os.getenv("AI_MODE", "mock").lower()
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolo11n.pt")
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.25"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Stage 5 LLM Configuration
LLM_MODE = os.getenv("LLM_MODE", "mock").lower()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
