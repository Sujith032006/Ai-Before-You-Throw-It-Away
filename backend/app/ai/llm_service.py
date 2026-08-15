import json
import logging
from typing import Dict, Any, List
from app.schemas.ai import (
    PersonalizedGuideRequest, PersonalizedGuideResponse, 
    GuideItemStatus, GuideStep, ChatRequest, ChatResponse,
    GeneralIdeasRequest, GeneralIdeasResponse,
    AssistantChatRequest, AssistantChatResponse
)
from app.services.reuse_repository import reuse_repository
from app.ai.llm_provider import get_llm_provider
from app.ai.prompts import SYSTEM_PROMPT_GUIDE, SYSTEM_PROMPT_CHAT, build_guide_prompt, build_chat_prompt

logger = logging.getLogger(__name__)

async def generate_personalized_guide(req: PersonalizedGuideRequest) -> PersonalizedGuideResponse:
    project = reuse_repository.get_project_by_id(req.project_id)
    if not project:
        # Fallback if project id is unknown
        project = {
            "id": req.project_id,
            "name": req.project_id.replace("-", " ").title(),
            "description": "Standard DIY upcycling guide.",
            "difficulty": req.difficulty,
            "estimated_time_minutes": req.max_time_minutes,
            "estimated_cost_min": req.budget_min,
            "estimated_cost_max": req.budget_max,
            "required_tools": req.available_tools,
            "required_materials": req.available_materials,
            "steps": ["Prepare your scanned item.", "Assemble according to preference."],
            "safety_notes": ["Handle tools carefully."]
        }

    provider = get_llm_provider()
    user_prompt = build_guide_prompt(project, req)

    try:
        raw_response = await provider.generate_response(SYSTEM_PROMPT_GUIDE, user_prompt, expect_json=True)
        clean_json_str = raw_response.strip()
        if clean_json_str.startswith("```"):
            parts = clean_json_str.split("```")
            if len(parts) >= 2:
                clean_json_str = parts[1]
                if clean_json_str.startswith("json"):
                    clean_json_str = clean_json_str[4:]
        clean_json_str = clean_json_str.strip()
        
        data = json.loads(clean_json_str)
        
        materials = [GuideItemStatus(**m) for m in data.get("materials", [])]
        tools = [GuideItemStatus(**t) for t in data.get("tools", [])]
        steps = [GuideStep(**s) for s in data.get("steps", [])]

        return PersonalizedGuideResponse(
            success=True,
            project_id=project.get("id", req.project_id),
            title=data.get("title", project.get("name")),
            summary=data.get("summary", project.get("description")),
            estimated_time_minutes=data.get("estimated_time_minutes", project.get("estimated_time_minutes", 15)),
            estimated_cost=data.get("estimated_cost", f"₹{project.get('estimated_cost_min', 0)}–₹{project.get('estimated_cost_max', 30)}"),
            difficulty=data.get("difficulty", project.get("difficulty", "Easy").title()),
            materials=materials,
            tools=tools,
            steps=steps,
            missing_items=data.get("missing_items", []),
            tips=data.get("tips", []),
            safety_notes=data.get("safety_notes", project.get("safety_notes", [])),
            is_ai_generated=True,
            message="Guide successfully personalized by AI."
        )
    except Exception as e:
        logger.error(f"[LLM Service] Error generating personalized guide: {str(e)}. Using standard fallback.")
        
        req_tools = [t.lower().strip() for t in project.get("required_tools", [])]
        user_tools = [t.lower().strip() for t in req.available_tools]
        req_mats = [m.lower().strip() for m in project.get("required_materials", [])]
        user_mats = [m.lower().strip() for m in req.available_materials]

        tool_statuses = [
            GuideItemStatus(name=t.title(), available=(t in user_tools), required=True)
            for t in req_tools
        ]
        mat_statuses = [
            GuideItemStatus(name=m.title(), available=(m in user_mats), required=True)
            for m in req_mats
        ]
        missing = [m.title() for m in req_mats if m not in user_mats] + [t.title() for t in req_tools if t not in user_tools]

        fallback_steps = [
            GuideStep(step_number=idx+1, title=f"Step {idx+1}", description=step_text)
            for idx, step_text in enumerate(project.get("steps", []))
        ]

        return PersonalizedGuideResponse(
            success=True,
            project_id=project["id"],
            title=project["name"],
            summary=project["description"],
            estimated_time_minutes=project.get("estimated_time_minutes", 15),
            estimated_cost=f"₹{project.get('estimated_cost_min', 0)}–₹{project.get('estimated_cost_max', 30)}",
            difficulty=project.get("difficulty", "easy").title(),
            materials=mat_statuses,
            tools=tool_statuses,
            steps=fallback_steps,
            missing_items=missing,
            tips=["Follow standard instructions provided above."],
            safety_notes=project.get("safety_notes", []),
            is_ai_generated=False,
            message="AI personalization unavailable. Rendering standard project guide."
        )

async def chat_with_assistant(req: ChatRequest) -> ChatResponse:
    project = reuse_repository.get_project_by_id(req.project_id)
    if not project:
        project = {"name": "Upcycling Project", "estimated_time_minutes": 15}

    provider = get_llm_provider()
    user_prompt = build_chat_prompt(project, req.user_context, req.message, req.conversation)

    try:
        reply_text = await provider.generate_response(SYSTEM_PROMPT_CHAT, user_prompt, expect_json=False)
        return ChatResponse(
            success=True,
            message=reply_text.strip()
        )
    except Exception as e:
        logger.error(f"[LLM Service] Error in AI Chat: {str(e)}")
        return ChatResponse(
            success=False,
            message="Sorry, the AI Assistant is temporarily unavailable. Please refer to the safety notes and guide steps above.",
            error=str(e)
        )

async def assistant_chat_service(req: AssistantChatRequest) -> AssistantChatResponse:
    """
    Reactive AI Assistant service that responds with full context and modifies projects on request.
    """
    ctx = req.context or {}
    msg = req.message

    sys_prompt = """You are a helpful, creative, safety-conscious DIY & upcycling assistant.
You help users upcycle physical items into useful, beautiful projects.

If the user asks to modify the project (e.g. "I don't have glue", "Make it faster", "I only have scissors"), react appropriately:
1. Explain how you modified the steps.
2. Return JSON containing "answer", "updated_project" (optional dict with new steps or title), and "changed_fields".

If the user asks to explain a step (e.g. "Explain step 2"), explain that step clearly.

Return JSON:
{
  "answer": "<Friendly helpful explanation>",
  "updated_project": null,
  "changed_fields": []
}
"""

    context_str = f"Context:\n- Object: {ctx.get('object', 'item')}\n- Material: {ctx.get('material', 'unknown')}\n- Goals: {ctx.get('goals', [])}\n- Tools: {ctx.get('tools', [])}\n- Materials: {ctx.get('materials', [])}\n- Budget: {ctx.get('budget', '0-50')}\n- Difficulty: {ctx.get('difficulty', 'easy')}\n- Time: {ctx.get('time', '30m')}\n\nUser Question: {msg}"

    provider = get_llm_provider()
    try:
        raw_res = await provider.generate_response(sys_prompt, context_str, expect_json=True)
        clean_json_str = raw_res.strip()
        if clean_json_str.startswith("```"):
            parts = clean_json_str.split("```")
            if len(parts) >= 2:
                clean_json_str = parts[1]
                if clean_json_str.startswith("json"):
                    clean_json_str = clean_json_str[4:]
        clean_json_str = clean_json_str.strip()

        data = json.loads(clean_json_str)
        return AssistantChatResponse(
            success=True,
            answer=data.get("answer", "I'm here to help you upcycle your item!"),
            updated_project=data.get("updated_project"),
            changed_fields=data.get("changed_fields", [])
        )
    except Exception as e:
        logger.warning(f"[LLM Service] Error in assistant_chat_service: {str(e)}")
        return AssistantChatResponse(
            success=True,
            answer=f"No problem! Regarding '{msg}', you can proceed safely using your available tools and materials.",
            updated_project=None,
            changed_fields=[]
        )

async def generate_general_ideas(req: GeneralIdeasRequest) -> GeneralIdeasResponse:
    obj = req.object_name.replace("_", " ").title()
    mat = req.material if req.material and req.material != "unknown" else "material"

    prompt = f"Provide 4 creative, practical upcycling, refurbishing, or repurposing ideas for a {obj} (Made of: {mat}). Return as a JSON array of strings under key 'ideas'."
    sys_prompt = "You are an expert sustainable design and upcycling assistant. Return valid JSON: {\"ideas\": [\"Idea 1\", \"Idea 2\", \"Idea 3\", \"Idea 4\"]}"

    provider = get_llm_provider()
    try:
        raw_res = await provider.generate_response(sys_prompt, prompt, expect_json=True)
        clean_json_str = raw_res.strip()
        if clean_json_str.startswith("```"):
            parts = clean_json_str.split("```")
            if len(parts) >= 2:
                clean_json_str = parts[1]
                if clean_json_str.startswith("json"):
                    clean_json_str = clean_json_str[4:]
        clean_json_str = clean_json_str.strip()

        data = json.loads(clean_json_str)
        ideas_list = data.get("ideas", [])
        if not ideas_list:
            ideas_list = [
                f"Repaint or refinish the surface of the {obj} to give it a fresh look.",
                f"Repurpose the {obj} as a decorative planter or garden ornament.",
                f"Convert into a unique storage or organizational rack.",
                f"Donate to a local community recycling center or furniture charity."
            ]
        return GeneralIdeasResponse(
            success=True,
            object_name=obj,
            ideas=ideas_list,
            message=f"Generated {len(ideas_list)} general upcycling ideas for {obj}."
        )
    except Exception as e:
        logger.warning(f"[LLM Service] Error generating general ideas: {str(e)}")
        fallback_ideas = [
            f"Repaint or refinish the surface of the {obj} to give it a fresh modern look.",
            f"Repurpose the {obj} as an outdoor planter or garden centerpiece.",
            f"Convert into a unique storage shelf or wall hanger.",
            f"Donate to a local repair workshop or community charity."
        ]
        return GeneralIdeasResponse(
            success=True,
            object_name=obj,
            ideas=fallback_ideas,
            message=f"Generated fallback ideas for {obj}."
        )
