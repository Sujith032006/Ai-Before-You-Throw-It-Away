import json
import logging
from typing import List
from app.schemas.recommendation import (
    RecommendationRequest, RecommendationResponse, RecommendationItem, EstimatedCost
)
from app.services.reuse_repository import reuse_repository
from app.recommendation.scoring import calculate_project_score
from app.ai.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)
COLOR_PALETTE = ["bg-emerald-100", "bg-teal-100", "bg-blue-100", "bg-purple-100", "bg-amber-100"]

async def generate_dynamic_ai_recommendations(req: RecommendationRequest) -> List[RecommendationItem]:
    """
    Generates dynamic AI upcycling recommendations for open-world objects (Chair, Laptop, Table, etc.)
    tailored to the user's goal, tools, materials, budget, and time constraints.
    """
    obj_name = req.object.object_name if req.object and req.object.object_name else req.object_name
    obj_display = req.object.display_name if req.object and req.object.display_name else obj_name.replace("_", " ").title()
    obj_mat = req.object.material if req.object and req.object.material else "material"
    obj_cond = req.object.condition if req.object and req.object.condition else "used"

    goal_str = req.custom_goal if req.custom_goal else req.goal
    tools_str = ", ".join(req.tools) if req.tools else "none (manual assembly)"
    mats_str = ", ".join(req.materials) if req.materials else "basic household items"
    b_max = req.budget.max if req.budget else req.budget_max
    t_max = req.time_minutes if req.time_minutes else req.max_time_minutes

    sys_prompt = """You are an expert upcycling & sustainable design engineer.
Generate 3 creative, practical, realistic upcycling projects for the specified object and user constraints.

Return strictly valid JSON with this schema:
{
  "projects": [
    {
      "project_id": "ai-proj-1",
      "title": "<Catchy Project Title>",
      "description": "<Concise 2-sentence description>",
      "match_score": 95,
      "why_it_matches": ["Uses your object", "Fits budget", "Easy assembly"],
      "difficulty": "easy",
      "estimated_time_minutes": 20,
      "estimated_cost_min": 10,
      "estimated_cost_max": 30,
      "tools_needed": ["scissors"],
      "materials_needed": ["soil"],
      "steps": ["Clean item", "Assemble"]
    }
  ]
}
"""

    user_prompt = f"""
Physical Object: {obj_display} (Material: {obj_mat}, Condition: {obj_cond})
User Goal: {goal_str}
Available Tools: {tools_str}
Available Materials: {mats_str}
Max Budget: ₹{b_max}
Max Time: {t_max} minutes
Desired Difficulty: {req.difficulty}
"""

    provider = get_llm_provider()
    ai_items: List[RecommendationItem] = []

    try:
        raw_res = await provider.generate_response(sys_prompt, user_prompt, expect_json=True)
        clean_json_str = raw_res.strip()
        if clean_json_str.startswith("```"):
            parts = clean_json_str.split("```")
            if len(parts) >= 2:
                clean_json_str = parts[1]
                if clean_json_str.startswith("json"):
                    clean_json_str = clean_json_str[4:]
        clean_json_str = clean_json_str.strip()

        data = json.loads(clean_json_str)
        proj_list = data.get("projects", [])

        for idx, p in enumerate(proj_list):
            c_min = float(p.get("estimated_cost_min", 0))
            c_max = float(p.get("estimated_cost_max", b_max))
            score_val = int(p.get("match_score", 90 - idx * 6))

            item = RecommendationItem(
                project_id=p.get("project_id", f"ai-proj-{idx+1}"),
                name=p.get("title", f"{obj_display} Upcycle Project"),
                title=p.get("title", f"{obj_display} Upcycle Project"),
                description=p.get("description", f"A great upcycling idea for your {obj_display}."),
                match_score=score_val,
                why_it_matches=p.get("why_it_matches", [f"Uses detected {obj_display}", "Matches user preferences"]),
                difficulty=p.get("difficulty", req.difficulty).title(),
                estimated_time_minutes=int(p.get("estimated_time_minutes", t_max)),
                estimated_cost_min=c_min,
                estimated_cost_max=c_max,
                estimated_cost=EstimatedCost(min=c_min, max=c_max, currency="INR"),
                matched_factors=p.get("why_it_matches", [f"Uses {obj_display}"]),
                missing_requirements=[],
                tools_needed=p.get("tools_needed", req.tools),
                materials_needed=p.get("materials_needed", req.materials),
                steps=p.get("steps", ["Inspect item", "Prepare project"]),
                is_top_match=(idx == 0),
                image_color=COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            )
            ai_items.append(item)
    except Exception as e:
        logger.warning(f"[Recommendation Engine] Dynamic AI generation fallback: {str(e)}")

    if not ai_items:
        # Guarantee fallback items for open-world objects
        ai_items = [
            RecommendationItem(
                project_id=f"ai-{obj_name}-1",
                name=f"{obj_display} Planter / Display Stand",
                title=f"{obj_display} Planter / Display Stand",
                description=f"Transform your {obj_display} into an attractive indoor or outdoor plant accent.",
                match_score=92,
                why_it_matches=[f"Uses {obj_display}", f"Fits budget under ₹{b_max}", "Easy difficulty"],
                difficulty="Easy",
                estimated_time_minutes=min(30, t_max),
                estimated_cost_min=0,
                estimated_cost_max=float(b_max),
                estimated_cost=EstimatedCost(min=0, max=float(b_max), currency="INR"),
                matched_factors=[f"Uses {obj_display}", "Matches gardening goal"],
                missing_requirements=[],
                tools_needed=req.tools,
                materials_needed=req.materials,
                steps=[f"Clean the surface of the {obj_display}.", "Set up decorative plants on top."],
                is_top_match=True,
                image_color="bg-emerald-100"
            ),
            RecommendationItem(
                project_id=f"ai-{obj_name}-2",
                name=f"{obj_display} Organizer Rack",
                title=f"{obj_display} Organizer Rack",
                description=f"Repurpose the {obj_display} into a storage or organizational shelf.",
                match_score=85,
                why_it_matches=[f"Uses {obj_display}", "Great utility"],
                difficulty="Easy",
                estimated_time_minutes=min(20, t_max),
                estimated_cost_min=0,
                estimated_cost_max=float(b_max),
                estimated_cost=EstimatedCost(min=0, max=float(b_max), currency="INR"),
                matched_factors=[f"Uses {obj_display}"],
                missing_requirements=[],
                tools_needed=req.tools,
                materials_needed=req.materials,
                steps=[f"Position {obj_display} in storage area.", "Organize items neatly."],
                is_top_match=False,
                image_color="bg-teal-100"
            )
        ]

    return ai_items

def get_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    all_projects = reuse_repository.get_all_projects()
    scored_items: List[RecommendationItem] = []

    for i, project in enumerate(all_projects):
        score, matched_factors, missing_reqs = calculate_project_score(project, req)
        if score >= 35:
            item = RecommendationItem(
                project_id=project["id"],
                name=project["name"],
                title=project["name"],
                description=project["description"],
                match_score=score,
                why_it_matches=matched_factors,
                difficulty=project.get("difficulty", "easy").title(),
                estimated_time_minutes=project.get("estimated_time_minutes", 15),
                estimated_cost_min=float(project.get("estimated_cost_min", 0)),
                estimated_cost_max=float(project.get("estimated_cost_max", 30)),
                estimated_cost=EstimatedCost(
                    min=float(project.get("estimated_cost_min", 0)),
                    max=float(project.get("estimated_cost_max", 30)),
                    currency="INR"
                ),
                matched_factors=matched_factors,
                missing_requirements=missing_reqs,
                tools_needed=project.get("required_tools", []),
                materials_needed=project.get("required_materials", []),
                steps=project.get("steps", []),
                is_top_match=False,
                image_color=COLOR_PALETTE[i % len(COLOR_PALETTE)]
            )
            scored_items.append(item)

    # Sort repository matches descending
    scored_items.sort(key=lambda x: x.match_score, reverse=True)

    # If no repository projects match open-world object (e.g. Chair, Laptop, Table), generate dynamic AI recommendations
    if not scored_items:
        import asyncio
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        ai_items = loop.run_until_complete(generate_dynamic_ai_recommendations(req))
        scored_items = ai_items

    if scored_items:
        scored_items[0].is_top_match = True
        top_match = scored_items[0]
    else:
        top_match = None

    return RecommendationResponse(
        success=True,
        object_name=req.object_name,
        top_recommendation=top_match,
        recommendations=scored_items,
        message=f"Found {len(scored_items)} upcycling project recommendations."
    )
