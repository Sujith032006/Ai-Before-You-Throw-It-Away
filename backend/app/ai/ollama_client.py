import io
import json
import base64
import logging
import httpx
from PIL import Image
from typing import Dict, Any, Optional

from app.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

def convert_pil_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image to a Base64-encoded JPEG string."""
    buf = io.BytesIO()
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

class OllamaClient:
    """
    Dedicated Ollama API Client for Qwen3-VL and Local Vision Models.
    Handles connection, base64 encoding, JSON parsing, and error recovery.
    """

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.generate_url = f"{self.base_url}/api/generate"
        self.tags_url = f"{self.base_url}/api/tags"

    async def check_health(self) -> Dict[str, Any]:
        """Checks if Ollama server is reachable and if the requested vision model exists."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(self.tags_url)
                if res.status_code == 200:
                    models = [m.get("name", "") for m in res.json().get("models", [])]
                    model_found = any(self.model in m for m in models) or len(models) > 0
                    return {
                        "ollama": "available",
                        "model": self.model,
                        "status": "ready" if model_found else "model_not_found",
                        "available_models": models
                    }
        except Exception as e:
            logger.info(f"[Ollama Client] Server health check unreachable: {str(e)}")

        return {
            "ollama": "unavailable",
            "model": self.model,
            "status": "analyzer_unavailable",
            "available_models": []
        }

    async def generate_vision_response(self, prompt: str, image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Sends an image + prompt to Ollama Qwen3-VL and parses structured JSON response.
        """
        img_b64 = convert_pil_to_base64(image)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
            "format": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=float(OLLAMA_TIMEOUT_SECONDS)) as client:
                res = await client.post(self.generate_url, json=payload)
                if res.status_code != 200:
                    logger.warning(f"[Ollama Client] HTTP error {res.status_code}: {res.text}")
                    return None

                data = res.json()
                raw_response = data.get("response", "").strip()

                # Attempt clean JSON parsing
                return self._parse_json_safely(raw_response)
        except httpx.TimeoutException:
            logger.warning(f"[Ollama Client] Timeout connecting to {self.generate_url}")
            return None
        except Exception as e:
            logger.info(f"[Ollama Client] Error calling Ollama: {str(e)}")
            return None

    def _parse_json_safely(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        clean_str = text.strip()
        if clean_str.startswith("```"):
            parts = clean_str.split("```")
            if len(parts) >= 2:
                clean_str = parts[1]
                if clean_str.startswith("json"):
                    clean_str = clean_str[4:]
        clean_str = clean_str.strip()

        try:
            return json.loads(clean_str)
        except Exception as err:
            logger.warning(f"[Ollama Client] JSON parse error: {str(err)} on raw: {text[:100]}")
            return None

# Singleton Client Instance
ollama_client = OllamaClient()
