import os
from dotenv import load_dotenv

load_dotenv()

FRONTEND_URLS = [
    url.strip() for url in os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:5174").split(",")
]
AI_MODE = os.getenv("AI_MODE", "real").lower()

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# LLM Generation Provider Configuration (Used for Upcycling Recommendations & Chat)
LLM_MODE = os.getenv("LLM_MODE", "real").lower()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

# Ollama + Qwen3-VL Configuration (SOLE OBJECT ANALYZER)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:8b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "15"))
PRIMARY_ANALYZER_PROVIDER = os.getenv("PRIMARY_ANALYZER_PROVIDER", "ollama").lower()
