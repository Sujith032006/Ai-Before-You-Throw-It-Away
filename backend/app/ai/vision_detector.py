import base64
import io
import json
import logging
from typing import Optional
from PIL import Image
import httpx

from app.utils.config import LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT_SECONDS
from app.schemas.detection import DetectionItem, BoundingBox

logger = logging.getLogger(__name__)

SYSTEM_VISION_PROMPT = """You are an expert Open-World Computer Vision Assistant.
Identify the primary physical object visible in this image.
Do NOT restrict yourself to any predefined reuse or recycling list.
Identify what physical object is actually in the image.

Return strictly valid JSON with these keys:
{
  "object": "<base object name in lowercase, e.g. chair, table, laptop, smartphone, bottle, jar, box, can, shoe, bag, book, keyboard, monitor, fan, plant, toy, bicycle, car, food, etc.>",
  "display_name": "<Human readable name, e.g. Plastic Bottle, Glass Jar, Dining Chair, Laptop Computer>",
  "material": "<dominant material: plastic, glass, wood, metal, cardboard, fabric, cotton, denim, leather, electronic, paper, unknown>",
  "condition": "<usable, used, damaged, unknown>",
  "confidence": <float between 0.0 and 1.0 representing identification confidence>,
  "category": "<General physical category, e.g. Furniture, Electronics, Containers, Packaging, Clothing, Household Hardware, Unknown>"
}

Important:
- If the image is blurry, ambiguous, or no object is clearly visible, set "object": "unknown" and "confidence": 0.0.
- Do NOT guess if you are uncertain. Never force an object into a reuse category.
"""

async def analyze_image_with_vision_ai(image: Image.Image) -> Optional[DetectionItem]:
    """
    Multimodal Vision AI open-world object & material identifier (Gemini 1.5 / OpenAI GPT-4o-mini Vision)
    """
    if not LLM_API_KEY or LLM_MODE != "real":
        return None

    try:
        # Convert PIL Image to Base64 JPEG
        buffered = io.BytesIO()
        image.convert("RGB").save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        base64_img = base64.b64encode(img_bytes).decode("utf-8")

        if LLM_PROVIDER == "gemini":
            model_name = LLM_MODEL if LLM_MODEL and "gemini" in LLM_MODEL else "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={LLM_API_KEY}"
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
                    obj_name = data.get("object", "unknown").lower().strip()
                    conf = float(data.get("confidence", 0.90))
                    mat = data.get("material", "unknown")
                    cat = data.get("category", "Household Object")
                    disp = data.get("display_name", obj_name.title())

                    return DetectionItem(
                        object=obj_name,
                        display_name=disp,
                        confidence=conf,
                        material=mat,
                        category=cat,
                        bounding_box=BoundingBox(x1=10, y1=10, x2=image.width-10, y2=image.height-10)
                    )

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
                    obj_name = data.get("object", "unknown").lower().strip()
                    conf = float(data.get("confidence", 0.90))
                    mat = data.get("material", "unknown")
                    cat = data.get("category", "Household Object")
                    disp = data.get("display_name", obj_name.title())

                    return DetectionItem(
                        object=obj_name,
                        display_name=disp,
                        confidence=conf,
                        material=mat,
                        category=cat,
                        bounding_box=BoundingBox(x1=10, y1=10, x2=image.width-10, y2=image.height-10)
                    )

    except Exception as e:
        logger.error(f"[Vision Detector] Vision AI API call failed: {str(e)}")

    return None
