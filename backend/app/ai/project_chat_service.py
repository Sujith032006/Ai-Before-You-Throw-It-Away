import json
import logging
from typing import Dict, Any, List

from app.schemas.project_chat import ProjectChatRequest, ProjectChatResponse
from app.ai.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

DEFAULT_SUGGESTIONS = [
  "Show another option",
  "Reduce cost",
  "Make it easier",
  "Explain step 1"
]

SYSTEM_PROMPT_PROJECT_CHAT = """You are an expert DIY, upcycling, and sustainable product engineering assistant.
You help users build, modify, and troubleshoot upcycling projects for physical objects.

Analyze the user's question, conversation history, and current Project Context.

Determine the action type:
- "answer_question"
- "modify_project"
- "replace_material"
- "replace_tool"
- "reduce_budget"
- "reduce_time"
- "change_difficulty"
- "generate_alternatives"
- "explain_step"
- "restart_project"

STRICT RULES:
1. If the user asks for budget reduction (e.g. "I only have ₹20", "Make it under ₹20"), set action="reduce_budget" and recalculate estimated_cost <= 20.
2. If the user asks for time reduction (e.g. "Can I make it in 10 mins?"), set action="reduce_time" and simplify steps.
3. If the user asks to make it easier, set action="change_difficulty" and simplify operations.
4. If the user asks for alternative ideas (e.g. "Give me another idea"), set action="generate_alternatives" and provide 3 options in updated_project.
5. If the user asks to explain a step, set action="explain_step" and explain that specific step clearly.
6. If user says they lack a material/tool (e.g. "I don't have paint", "I don't have soil"), set action="replace_material" or "replace_tool" and offer safe substitutes.

Return strictly valid JSON:
{
  "message": "<Friendly, actionable response text>",
  "action": "<action_type>",
  "updated_project": {
    "title": "<Optional Updated Title>",
    "estimated_cost_max": 20,
    "estimated_time_minutes": 10,
    "difficulty": "Easy",
    "steps": ["Step 1", "Step 2"],
    "alternatives": ["Idea 1", "Idea 2", "Idea 3"]
  },
  "suggestions": [
    "Make it cheaper",
    "Make it easier",
    "Give another idea",
    "Explain next step"
  ]
}
"""

async def process_project_chat(req: ProjectChatRequest) -> ProjectChatResponse:
    ctx = req.project_context
    msg = req.message.strip()

    context_summary = f"""
PROJECT CONTEXT:
- Object: {ctx.object.name} (Material: {ctx.object.material}, Condition: {ctx.object.condition})
- Selected Project: {ctx.selected_project.title} (Difficulty: {ctx.selected_project.difficulty}, Time: {ctx.selected_project.estimated_time_minutes}m, Cost: ₹{ctx.selected_project.estimated_cost.get('min', 0)}–₹{ctx.selected_project.estimated_cost.get('max', 50)})
- User Preferences: Goal={ctx.user_preferences.goal}, CustomGoal={ctx.user_preferences.custom_goal}, Budget=₹{ctx.user_preferences.budget}, Time={ctx.user_preferences.time_minutes}m, Difficulty={ctx.user_preferences.difficulty}
- Tools Available: {', '.join(ctx.tools) if ctx.tools else 'none'}
- Materials Available: {', '.join(ctx.materials) if ctx.materials else 'none'}
- Current Active Step: {ctx.current_step}

CONVERSATION HISTORY:
"""
    for c in req.conversation[-6:]:
        context_summary += f"{c.role.upper()}: {c.content}\n"

    context_summary += f"\nUSER QUESTION: {msg}\n"

    provider = get_llm_provider()

    try:
        raw_res = await provider.generate_response(SYSTEM_PROMPT_PROJECT_CHAT, context_summary, expect_json=True)
        clean_json_str = raw_res.strip()
        if clean_json_str.startswith("```"):
            parts = clean_json_str.split("```")
            if len(parts) >= 2:
                clean_json_str = parts[1]
                if clean_json_str.startswith("json"):
                    clean_json_str = clean_json_str[4:]
        clean_json_str = clean_json_str.strip()

        data = json.loads(clean_json_str)

        return ProjectChatResponse(
            success=True,
            message=data.get("message", "I'm here to help you complete this project."),
            action=data.get("action", "answer_question"),
            updated_project=data.get("updated_project"),
            suggestions=data.get("suggestions", DEFAULT_SUGGESTIONS)
        )
    except Exception as e:
        logger.warning(f"[Project Chat Service] Error: {str(e)}. Using heuristic rule assistant.")

    # Rule-based fallback for high reliability
    msg_lower = msg.lower()
    if "paint" in msg_lower and ("don't have" in msg_lower or "no " in msg_lower):
        return ProjectChatResponse(
            success=True,
            message="No problem! You can leave the surface unpainted for a natural vintage look, or use decorative cloth/paper if available.",
            action="replace_material",
            updated_project={"steps": ["Clean item", "Assemble project without paint"]},
            suggestions=["Make it cheaper", "Give another idea", "Explain step 1"]
        )
    elif "₹20" in msg_lower or "20" in msg_lower or "cheaper" in msg_lower or "budget" in msg_lower:
        return ProjectChatResponse(
            success=True,
            message=f"I've updated the project to stay within ₹20 by removing paid decorative items and using zero-cost household materials.",
            action="reduce_budget",
            updated_project={
                "estimated_cost_max": 20,
                "estimated_cost": {"min": 0, "max": 20, "currency": "INR"}
            },
            suggestions=["Make it faster", "Explain step 1", "Start over"]
        )
    elif "easier" in msg_lower or "easy" in msg_lower:
        return ProjectChatResponse(
            success=True,
            message="I simplified the project into an Easy 2-step setup requiring minimal effort.",
            action="change_difficulty",
            updated_project={"difficulty": "Easy", "steps": ["Clean surface", "Position items"]},
            suggestions=["Make it cheaper", "Explain step 1"]
        )
    elif "another idea" in msg_lower or "alternatives" in msg_lower or "new project" in msg_lower:
        return ProjectChatResponse(
            success=True,
            message=f"Here are 3 alternative upcycling ideas for your {ctx.object.name}:",
            action="generate_alternatives",
            updated_project={
                "alternatives": [
                    f"{ctx.object.name.title()} Planter Holder",
                    f"{ctx.object.name.title()} Storage Organizer",
                    f"{ctx.object.name.title()} Decorative Stand"
                ]
            },
            suggestions=["Pick planter holder", "Pick storage organizer"]
        )
    elif "explain step" in msg_lower or "step 2" in msg_lower or "step 1" in msg_lower:
        return ProjectChatResponse(
            success=True,
            message=f"Step {ctx.current_step} Explanation: Position your item securely on a flat surface and attach components firmly so they remain stable.",
            action="explain_step",
            suggestions=["Next step", "I don't have this tool"]
        )

    return ProjectChatResponse(
        success=True,
        message=f"For your {ctx.object.name} {ctx.selected_project.title}, proceed carefully using your available tools.",
        action="answer_question",
        suggestions=DEFAULT_SUGGESTIONS
    )
