import os
from dotenv import load_dotenv

load_dotenv()

FRONTEND_URLS = [
    url.strip() for url in os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:5174").split(",")
]
AI_MODE = os.getenv("AI_MODE", "real").lower()

# RF-DETR Bounding Box & Localization Configuration
RFDETR_MODEL = os.getenv("RFDETR_MODEL", "rtdetr-l.pt")
HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.80"))
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.50"))

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Primary Gemini Multimodal Vision Analyzer Configuration
VISION_MODEL = os.getenv("VISION_MODEL", os.getenv("LLM_MODEL", "gemini-1.5-flash"))
LLM_MODE = os.getenv("LLM_MODE", "real").lower()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
