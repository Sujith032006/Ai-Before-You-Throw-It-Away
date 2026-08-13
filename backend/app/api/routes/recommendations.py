from fastapi import APIRouter, HTTPException, status
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, ProjectDetailsResponse
from app.recommendation.recommendation_engine import get_recommendations
from app.services.reuse_repository import reuse_repository

from app.services.persistence_service import save_recommendations_list

router = APIRouter(prefix="/api", tags=["Recommendations"])

@router.post("/recommendations", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
async def recommend_projects(request: RecommendationRequest):
    res = get_recommendations(request)
    if res.recommendations:
        save_recommendations_list(
            scan_id=None,
            recommendations=[r.dict() for r in res.recommendations]
        )
    return res

@router.get("/projects/{project_id}", response_model=ProjectDetailsResponse, status_code=status.HTTP_200_OK)
async def get_project_details(project_id: str):
    project = reuse_repository.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    return ProjectDetailsResponse(
        success=True,
        project_id=project["id"],
        name=project["name"],
        description=project["description"],
        supported_objects=project.get("supported_objects", []),
        goals=project.get("goals", []),
        required_tools=project.get("required_tools", []),
        optional_tools=project.get("optional_tools", []),
        required_materials=project.get("required_materials", []),
        optional_materials=project.get("optional_materials", []),
        difficulty=project.get("difficulty", "easy").title(),
        estimated_time_minutes=project.get("estimated_time_minutes", 15),
        estimated_cost_min=float(project.get("estimated_cost_min", 0)),
        estimated_cost_max=float(project.get("estimated_cost_max", 30)),
        safety_notes=project.get("safety_notes", []),
        steps=project.get("steps", [])
    )
