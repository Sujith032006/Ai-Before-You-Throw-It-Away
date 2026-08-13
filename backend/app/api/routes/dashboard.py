from fastapi import APIRouter, status
from app.schemas.dashboard import DashboardResponse
from app.services.persistence_service import get_dashboard_statistics

router = APIRouter(prefix="/api", tags=["Dashboard & Statistics"])

@router.get("/dashboard", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
async def get_dashboard():
    stats = get_dashboard_statistics()
    return DashboardResponse(
        success=True,
        total_scans=stats["total_scans"],
        total_projects=stats["total_projects"],
        completed_projects=stats["completed_projects"],
        recent_activity=stats["recent_activity"]
    )
