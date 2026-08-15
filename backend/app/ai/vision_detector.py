import base64
import io
import json
import logging
from typing import Optional, Dict, Any, List
from PIL import Image
import httpx

from app.utils.config import (
    LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, VISION_MODEL, LLM_TIMEOUT_SECONDS
)
from app.schemas.detection import DetectionItem, BoundingBox

logger = logging.getLogger(__name__)

SYSTEM_VISION_PROMPT = """You are a visual object identification system.
Analyze the uploaded image carefully.

Your first responsibility is to identify the actual physical object visible in the image.
Do NOT choose from a restricted recycling or reuse category.
Do NOT force the object into a known class.
Do NOT assume that every object is recyclable.

Identify the common real-world object name (e.g. chair, table, laptop, smartphone, keyboard, monitor, shoe, bag, book, fan, bicycle, toy, bottle, jar, cup, plate, box, cardboard box, tin can, plastic container, etc.).

If there are multiple distinct objects visible, list each important object in the "objects" array.

Separate object identity from material. For example:
- A bottle is an object. Plastic is its material.
- Do not call a bottle a plastic bottle unless the material can be reasonably determined.

Return strictly valid JSON with this exact schema:
{
  "status": "identified",
  "objects": [
    {
      "object_name": "<common lowercase name e.g. chair, laptop, bottle>",
      "display_name": "<Title Case Name e.g. Chair, Laptop, Bottle>",
      "material": "<plastic|glass|metal|paper|cardboard|wood|fabric|rubber|electronics|ceramic|mixed|unknown>",
      "condition": "<new|used|damaged|broken|dirty|intact|unknown>",
      "confidence": <float between 0.0 and 1.0>,
      "confidence_level": "<high|medium|low|unknown>"
    }
  ],
  "primary_object_index": 0,
  "image_quality": "good",
  "reasoning_summary": "<Short factual 1-sentence summary>"
}

Important:
- If the image is blurry, ambiguous, severely obstructed, or impossible to identify reliably, set "status": "ambiguous", "objects": [], and reasoning_summary explaining why.
- Never guess. Never invent an object.
"""

async def analyze_image_with_vision_ai(image: Image.Image) -> Optional[Dict[str, Any]]:
    """
    Primary Gemini Multimodal Vision Analyzer.
    Identifies actual open-world physical object, material, and condition.
    """
    if not LLM_API_KEY or LLM_MODE != "real":
        return None

    try:
        # Convert PIL Image to Base64 JPEG
        buffered = io.BytesIO()
        image.convert("RGB").save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        base64_img = base64.b64encode(img_bytes).decode("utf-8")

        target_model = VISION_MODEL if VISION_MODEL else LLM_MODEL
        if not target_model:
            target_model = "gemini-1.5-flash"

        if LLM_PROVIDER == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={LLM_API_KEY}"
            headers = {"Content-Type": "application/json"}

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": SYSTEM_VISION_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_img
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }

            async with httpx.AsyncClient(timeout=float(LLM_TIMEOUT_SECONDS)) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    res_json = resp.json()
                    raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    data = json.loads(raw_text)
                    return data

        elif LLM_PROVIDER == "openai":
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": LLM_MODEL if "gpt-4" in LLM_MODEL else "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_VISION_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image and identify the actual physical object and material:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }

            async with httpx.AsyncClient(timeout=float(LLM_TIMEOUT_SECONDS)) as client:
                resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    res_json = resp.json()
                    raw_text = res_json["choices"][0]["message"]["content"]
                    data = json.loads(raw_text)
                    return data

    except Exception as e:
        logger.error(f"[Vision Detector] Primary Gemini Vision API call failed: {str(e)}")

    return None
