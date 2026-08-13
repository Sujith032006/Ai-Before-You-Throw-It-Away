from typing import List
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendationItem
from app.services.reuse_repository import reuse_repository
from app.recommendation.scoring import calculate_project_score

COLOR_PALETTE = ["bg-green-100", "bg-orange-100", "bg-blue-100", "bg-purple-100", "bg-amber-100"]

def get_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    all_projects = reuse_repository.get_all_projects()
    
    scored_items: List[RecommendationItem] = []

    for i, project in enumerate(all_projects):
        score, matched_factors, missing_reqs = calculate_project_score(project, req)
        
        # Only include items with a reasonable score (> 25)
        if score >= 25:
            item = RecommendationItem(
                project_id=project["id"],
                name=project["name"],
                description=project["description"],
                match_score=score,
                difficulty=project.get("difficulty", "easy").title(),
                estimated_time_minutes=project.get("estimated_time_minutes", 15),
                estimated_cost_min=float(project.get("estimated_cost_min", 0)),
                estimated_cost_max=float(project.get("estimated_cost_max", 30)),
                matched_factors=matched_factors,
                missing_requirements=missing_reqs,
                is_top_match=False,
                image_color=COLOR_PALETTE[i % len(COLOR_PALETTE)]
            )
            scored_items.append(item)

    # Sort by match score descending
    scored_items.sort(key=lambda x: x.match_score, reverse=True)

    if not scored_items:
        return RecommendationResponse(
            success=True,
            object_name=req.object_name,
            top_recommendation=None,
            recommendations=[],
            message="No suitable reuse ideas were found for this combination. Try changing your goal, budget, or difficulty."
        )

    # Mark the highest scoring project as top match
    scored_items[0].is_top_match = True
    top_match = scored_items[0]

    return RecommendationResponse(
        success=True,
        object_name=req.object_name,
        top_recommendation=top_match,
        recommendations=scored_items,
        message=f"Found {len(scored_items)} upcycling project recommendations."
    )
