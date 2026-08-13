import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

from app.utils.config import LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
        pass

class MockLLMProvider(BaseLLMProvider):
    async def generate_response(self, system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
        logger.info("[MockLLMProvider] Generating mock LLM response.")
        
        # If calling for personalized guide JSON
        if expect_json or "structured JSON" in system_prompt or "Personalized DIY Guide" in system_prompt:
            mock_json = {
                "title": "Self-Watering Planter (Personalized)",
                "summary": "Customized step-by-step upcycling guide tailored to your available scissors and soil.",
                "estimated_time_minutes": 15,
                "estimated_cost": "₹10–₹30",
                "difficulty": "Easy",
                "materials": [
                    {"name": "Plastic Bottle", "available": True, "required": True},
                    {"name": "Soil", "available": True, "required": True},
                    {"name": "Cotton Yarn/Wick", "available": False, "required": True}
                ],
                "tools": [
                    {"name": "Scissors", "available": True, "required": True}
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Clean and Prepare",
                        "description": "Rinse the plastic bottle with clean water and dry thoroughly.",
                        "tip": "Use warm water to easily loosen any sticky adhesive."
                    },
                    {
                        "step_number": 2,
                        "title": "Cut Bottle In Half",
                        "description": "Carefully cut the plastic bottle horizontally about 4 inches below the bottle cap using your scissors.",
                        "tip": "Draw a straight guideline around the bottle using a marker first."
                    },
                    {
                        "step_number": 3,
                        "title": "Prepare the Wick (Material Missing Note)",
                        "description": "Since cotton is not in your available materials list, use any thick natural string or strip of clean cotton fabric.",
                        "tip": "The wick will draw water upwards into the soil automatically."
                    },
                    {
                        "step_number": 4,
                        "title": "Assemble Inverted Top",
                        "description": "Invert the top neck of the bottle so it sits inside the lower base like a funnel with the wick hanging into the bottom chamber.",
                        "tip": "Make sure the wick reaches near the bottom of the base."
                    },
                    {
                        "step_number": 5,
                        "title": "Add Soil and Plant",
                        "description": "Add potting soil to the top funnel section and fill the lower base with 2 inches of water.",
                        "tip": "Water gently from the top for the first time to prime the soil."
                    }
                ],
                "missing_items": ["Cotton Yarn/Wick"],
                "tips": [
                    "Keep water levels in the lower reservoir refilled every 3-5 days.",
                    "Place in indirect sunlight for optimal herb growth."
                ],
                "safety_notes": [
                    "Be careful when cutting plastic edges with scissors.",
                    "Smooth out sharp plastic cuts before planting."
                ]
            }
            return json.dumps(mock_json)
        
        # Chat responses
        user_lower = user_prompt.lower()
        if "glue" in user_lower:
            return "Based on your project context, you currently have scissors and soil. For the Self-Watering Planter, glue is not required! The inverted top section fits securely inside the bottom half without any adhesive."
        elif "time" in user_lower or "minutes" in user_lower or "10" in user_lower:
            return "The estimated project time for the Self-Watering Planter is 15 minutes. While 10 minutes might be tight, if your bottle is already clean, you can easily complete it in under 15 minutes!"
        elif "cotton" in user_lower:
            return "Since you don't have cotton yarn, you can substitute a strip cut from a clean old cotton T-shirt or kitchen twine. It will wick water just as effectively."
        else:
            return f"I'm your AI Project Assistant for the Self-Watering Planter! With your available scissors and soil, you're ready to complete this project safely and quickly. Let me know if you need any tip!"

class OpenAILLMProvider(BaseLLMProvider):
    async def generate_response(self, system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
        if not LLM_API_KEY:
            logger.warning("[OpenAILLMProvider] No LLM_API_KEY configured. Falling back to mock provider.")
            return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)
        
        logger.info(f"[OpenAILLMProvider] Sending request to OpenAI API (Model: {LLM_MODEL}).")
        
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }

        if expect_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=float(LLM_TIMEOUT_SECONDS)) as client:
                resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(f"[OpenAILLMProvider] OpenAI API error ({resp.status_code}): {resp.text}")
                    # Fallback to mock on API error
                    return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)
                
                res_data = resp.json()
                content = res_data["choices"][0]["message"]["content"]
                return content
        except Exception as e:
            logger.error(f"[OpenAILLMProvider] HTTP Exception calling LLM API: {str(e)}")
            return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)

class GeminiLLMProvider(BaseLLMProvider):
    async def generate_response(self, system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
        if not LLM_API_KEY:
            logger.warning("[GeminiLLMProvider] No LLM_API_KEY configured. Falling back to mock provider.")
            return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)

        model_name = LLM_MODEL if LLM_MODEL and LLM_MODEL != "gpt-4o-mini" else "gemini-1.5-flash"
        logger.info(f"[GeminiLLMProvider] Sending request to Gemini API (Model: {model_name}).")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={LLM_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3
            }
        }

        if expect_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            async with httpx.AsyncClient(timeout=float(LLM_TIMEOUT_SECONDS)) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(f"[GeminiLLMProvider] Gemini API error ({resp.status_code}): {resp.text}")
                    return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)
                
                res_data = resp.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return content
        except Exception as e:
            logger.error(f"[GeminiLLMProvider] HTTP Exception calling Gemini LLM API: {str(e)}")
            return await MockLLMProvider().generate_response(system_prompt, user_prompt, expect_json)

def get_llm_provider() -> BaseLLMProvider:
    if LLM_MODE == "real":
        if LLM_PROVIDER == "gemini":
            return GeminiLLMProvider()
        return OpenAILLMProvider()
    return MockLLMProvider()

