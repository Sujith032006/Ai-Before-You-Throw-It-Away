from typing import Dict, Any, Tuple, List
from app.schemas.recommendation import RecommendationRequest

# Configurable Scoring Weights (Total = 100)
WEIGHT_OBJECT = 30.0
WEIGHT_GOAL = 25.0
WEIGHT_TOOL = 15.0
WEIGHT_MATERIAL = 10.0
WEIGHT_BUDGET = 10.0
WEIGHT_DIFFICULTY = 5.0
WEIGHT_TIME = 5.0

def calculate_project_score(project: Dict[str, Any], req: RecommendationRequest) -> Tuple[int, List[str], List[str]]:
    score = 0.0
    matched_factors: List[str] = []
    missing_requirements: List[str] = []

    # 1. Object Compatibility (30 pts)
    req_obj_clean = req.object_name.lower().strip().replace(" ", "_")
    req_obj_raw = req.object_name.lower().strip()
    supported = [s.lower().strip() for s in project.get("supported_objects", [])]

    if req_obj_clean in supported or req_obj_raw in supported:
        score += WEIGHT_OBJECT
        matched_factors.append(f"Works directly with your scanned item ({req.object_name})")
    elif any(s in req_obj_raw or req_obj_raw in s for s in supported):
        score += WEIGHT_OBJECT * 0.7
        matched_factors.append(f"Compatible with item category ({project['name']})")
    else:
        # Object is not compatible
        score += 0.0
        missing_requirements.append(f"Requires object of type: {', '.join(project.get('supported_objects', []))}")

    # 2. Goal Compatibility (25 pts)
    req_goal = req.goal.lower().strip()
    project_goals = [g.lower().strip() for g in project.get("goals", [])]

    if req_goal == "surprise_me":
        score += WEIGHT_GOAL
        matched_factors.append("Matches your flexible goal preference")
    elif req_goal in project_goals:
        score += WEIGHT_GOAL
        goal_title = req.goal.replace("_", " ").title()
        matched_factors.append(f"Matches your target goal ({goal_title})")
    else:
        score += WEIGHT_GOAL * 0.2

    # 3. Tool Compatibility (15 pts)
    req_tools = [t.lower().strip() for t in project.get("required_tools", [])]
    user_tools = [t.lower().strip() for t in req.tools]

    if not req_tools:
        score += WEIGHT_TOOL
        matched_factors.append("Requires no special tools")
    else:
        matched_tools = [t for t in req_tools if t in user_tools]
        missing_tools = [t for t in req_tools if t not in user_tools]
        
        ratio = len(matched_tools) / len(req_tools)
        score += WEIGHT_TOOL * ratio

        if ratio == 1.0:
            matched_factors.append(f"You have all required tools ({', '.join(matched_tools)})")
        elif matched_tools:
            matched_factors.append(f"You have tools: {', '.join(matched_tools)}")

        for t in missing_tools:
            missing_requirements.append(f"Missing tool: {t.title()}")

    # 4. Material Compatibility (10 pts)
    req_mats = [m.lower().strip() for m in project.get("required_materials", [])]
    user_mats = [m.lower().strip() for m in req.materials]

    if not req_mats:
        score += WEIGHT_MATERIAL
        matched_factors.append("Requires no extra materials")
    else:
        matched_mats = [m for m in req_mats if m in user_mats]
        missing_mats = [m for m in req_mats if m not in user_mats]

        ratio = len(matched_mats) / len(req_mats)
        score += WEIGHT_MATERIAL * ratio

        if ratio == 1.0:
            matched_factors.append(f"You have all required materials ({', '.join(matched_mats)})")
        elif matched_mats:
            matched_factors.append(f"You have materials: {', '.join(matched_mats)}")

        for m in missing_mats:
            missing_requirements.append(f"Missing material: {m.title()}")

    # 5. Budget Compatibility (10 pts)
    proj_max_cost = float(project.get("estimated_cost_max", 0))
    user_max_budget = float(req.budget_max)

    if proj_max_cost <= user_max_budget:
        score += WEIGHT_BUDGET
        matched_factors.append(f"Fits within your budget (Est. ₹{project.get('estimated_cost_min', 0)}–₹{proj_max_cost})")
    elif proj_max_cost <= user_max_budget * 1.5:
        score += WEIGHT_BUDGET * 0.5
        matched_factors.append("Slightly over requested budget range")
    else:
        missing_requirements.append(f"Higher cost than preferred budget (Est. ₹{proj_max_cost})")

    # 6. Difficulty Compatibility (5 pts)
    proj_diff = project.get("difficulty", "easy").lower()
    user_diff = req.difficulty.lower()

    diff_map = {"easy": 1, "medium": 2, "hard": 3}
    p_val = diff_map.get(proj_diff, 1)
    u_val = diff_map.get(user_diff, 1)

    if p_val <= u_val:
        score += WEIGHT_DIFFICULTY
        matched_factors.append(f"Fits your {proj_diff.title()} difficulty preference")
    else:
        score += WEIGHT_DIFFICULTY * 0.3
        missing_requirements.append(f"Higher difficulty ({proj_diff.title()})")

    # 7. Time Compatibility (5 pts)
    proj_time = int(project.get("estimated_time_minutes", 15))
    user_max_time = int(req.max_time_minutes)

    if proj_time <= user_max_time:
        score += WEIGHT_TIME
        matched_factors.append(f"Quick project (~{proj_time} mins)")
    else:
        score += WEIGHT_TIME * 0.4
        missing_requirements.append(f"Takes longer than preferred time ({proj_time} mins)")

    final_score = int(round(score))
    return final_score, matched_factors, missing_requirements
